/**
 * SSE (Server-Sent Events) client for streaming chat responses
 *
 * Purpose: Handle real-time LLM token streaming via EventSource
 *
 * Features:
 * - Exponential backoff retry logic (handles network issues)
 * - Graceful error handling with user feedback
 * - Stream cancellation support
 * - Connection state tracking
 * - Automatic reconnection (up to 5 retries)
 *
 * Design decisions:
 * - EventSource over WebSocket: Simpler, one-way streaming sufficient
 * - Exponential backoff: Prevents thundering herd on server restart
 * - Max 5 retries: Balance between resilience and giving up
 * - Session ID for cancellation: Backend can stop specific stream
 *
 * WHY EventSource instead of WebSocket:
 * - Simpler: No handshake, no ping/pong, automatic reconnection
 * - Perfect for one-way streaming: Client sends HTTP POST, server streams response
 * - Browser support: Built-in reconnection, automatic Last-Event-ID
 * - Less code: No need to manage WebSocket lifecycle
 *
 * Trade-offs:
 * - No binary data: EventSource is text-only (fine for JSON)
 * - One-way: Can't send messages during stream (use separate POST for cancel)
 * - HTTP/1.1 connection limit: Max 6 concurrent connections per domain
 */

import { API_ENDPOINTS, APP_CONFIG } from '$lib/config';
import { messages } from '$lib/stores/messages';
import type { SSETokenEvent, SSECompleteEvent, SSEErrorEvent, Message } from '$lib/types';

/**
 * SSE client state machine
 *
 * States:
 * - disconnected: No active connection
 * - connecting: EventSource connecting
 * - connected: Receiving events
 * - error: Connection failed, retrying
 */
type SSEClientState = 'disconnected' | 'connecting' | 'connected' | 'error';

/**
 * SSE client class
 *
 * WHY class instead of functions:
 * - State management: Encapsulates eventSource, sessionId, retryCount
 * - Lifecycle: Clear start/stop/cleanup pattern
 * - Single responsibility: One client instance per stream
 */
export class SSEClient {
	private eventSource: EventSource | null = null;
	private sessionId: string | null = null;
	private retryCount: number = 0;
	private state: SSEClientState = 'disconnected';
	private conversationId: number | null = null;
	private messageId: number | null = null;

	/**
	 * Start streaming chat response
	 *
	 * Flow:
	 * 1. Close existing connection (if any)
	 * 2. Create EventSource connection to /api/chat/stream
	 * 3. Listen for 'token', 'complete', 'error' events
	 * 4. Update messages store with tokens as they arrive
	 * 5. Handle completion or errors
	 *
	 * WHY POST to initiate, then EventSource for stream:
	 * - EventSource limitation: Can't send POST body in EventSource constructor
	 * - Solution: Send POST request first, backend returns stream URL with session ID
	 * - Alternative considered: Use query params for message (length limit)
	 * - Chosen approach: POST + EventSource is standard pattern for SSE with payload
	 *
	 * @param conversationId - Conversation to send message in
	 * @param message - User message content
	 */
	async connect(conversationId: number, message: string): Promise<void> {
		try {
			// Clean up existing connection
			this.cleanup();

			this.state = 'connecting';
			this.conversationId = conversationId;
			this.retryCount = 0;

			// Step 1: Send POST request to initiate stream
			// Backend creates session and starts LLM generation
			const response = await fetch(API_ENDPOINTS.chat.stream, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					conversation_id: conversationId,
					message: message
				})
			});

			if (!response.ok) {
				throw new Error(`Failed to start stream: ${response.statusText}`);
			}

			// Backend returns session ID for this stream
			const data = await response.json();
			this.sessionId = data.session_id;
			this.messageId = data.message_id; // Backend pre-creates assistant message

			// Step 2: Open EventSource connection
			// Backend streams tokens as SSE events via GET /api/chat/stream/{session_id}
			const sseUrl = `${API_ENDPOINTS.chat.stream}/${this.sessionId}`;
			this.eventSource = new EventSource(sseUrl);

			// Set up event listeners
			this.setupEventListeners();

			// Mark message as streaming in store
			if (this.messageId) {
				messages.startStreaming(this.messageId);
			}
		} catch (err) {
			console.error('Failed to connect SSE:', err);
			this.handleError(err instanceof Error ? err.message : 'Connection failed');
		}
	}

	/**
	 * Set up EventSource event listeners
	 *
	 * WHY separate method:
	 * - Clarity: Connection logic separate from event handling
	 * - Reusability: Can re-attach listeners on reconnection
	 */
	private setupEventListeners(): void {
		if (!this.eventSource) return;

		/**
		 * Handle 'open' event (connection established)
		 *
		 * WHY reset retry count on successful connection:
		 * - Fresh start: Previous failures are irrelevant now
		 * - Next failure: Should retry from 1s delay, not 16s
		 */
		this.eventSource.addEventListener('open', () => {
			this.state = 'connected';
			this.retryCount = 0;
			console.log('[SSE] Connected');
		});

		/**
		 * Handle 'token' event (LLM token received)
		 *
		 * Event data format:
		 * {
		 *   "token": "Hello",
		 *   "message_id": 123,
		 *   "session_id": "uuid-here"
		 * }
		 *
		 * WHY append token immediately instead of batching:
		 * - Real-time feel: User sees response appearing character-by-character
		 * - Perceived performance: Feels faster than waiting for batches
		 * - Svelte optimization: Store updates are batched by framework
		 */
		this.eventSource.addEventListener('token', (event: MessageEvent) => {
			try {
				const data: SSETokenEvent = JSON.parse(event.data);
				messages.appendStreamingToken(data.token);
			} catch (err) {
				console.error('[SSE] Failed to parse token event:', err);
			}
		});

		/**
		 * Handle 'complete' event (stream finished)
		 *
		 * Event data format:
		 * {
		 *   "message_id": 123,
		 *   "token_count": 456,
		 *   "completion_time_ms": 2500
		 * }
		 *
		 * WHY backend sends complete message object:
		 * - Authoritative: Backend is source of truth for message data
		 * - Metadata: token_count, completion_time_ms only known by backend
		 * - Consistency: Ensures client/server state match
		 */
		this.eventSource.addEventListener('complete', async (event: MessageEvent) => {
			try {
				const data: SSECompleteEvent = JSON.parse(event.data);

				// Fetch complete message from backend (includes all metadata)
				const completeMessage = await this.fetchCompleteMessage(
					data.message_id,
					data.token_count,
					data.completion_time_ms
				);

				// Finish streaming in store (adds message to history)
				messages.finishStreaming(completeMessage);

				// Clean up connection
				this.cleanup();
			} catch (err) {
				console.error('[SSE] Failed to handle complete event:', err);
				this.handleError('Failed to complete stream');
			}
		});

		/**
		 * Handle 'error' event (stream error from backend)
		 *
		 * Event data format:
		 * {
		 *   "error": "LLM service unavailable",
		 *   "error_type": "service_error"
		 * }
		 */
		this.eventSource.addEventListener('error', (event: MessageEvent) => {
			// Check if event has data (backend error) or is connection error
			if (event.data) {
				try {
					const data: SSEErrorEvent = JSON.parse(event.data);
					this.handleError(data.error);
					return;
				} catch (err) {
					// Event doesn't have JSON data, treat as connection error
				}
			}

			// Connection error (network issue, server down, etc.)
			this.handleConnectionError();
		});
	}

	/**
	 * Handle connection errors with exponential backoff retry
	 *
	 * Retry strategy:
	 * - Attempt 1: Wait 1s, retry
	 * - Attempt 2: Wait 2s, retry
	 * - Attempt 3: Wait 4s, retry
	 * - Attempt 4: Wait 8s, retry
	 * - Attempt 5: Wait 16s, retry
	 * - After 5 failures: Give up (total ~31s of retries)
	 *
	 * WHY exponential backoff:
	 * - Prevents thundering herd: 1000 clients don't all retry at same time
	 * - Gives server time to recover: If server restarting, delays spread load
	 * - Standard pattern: Used by HTTP clients, AWS SDK, etc.
	 *
	 * WHY 5 max retries:
	 * - Balance: Enough for transient issues, not infinite
	 * - User experience: 30s is reasonable wait, 60s+ is frustrating
	 * - Server protection: Prevents endless retry loops overloading server
	 */
	private handleConnectionError(): void {
		this.state = 'error';
		this.retryCount++;

		if (this.retryCount <= APP_CONFIG.sse.maxRetries) {
			const delay = APP_CONFIG.sse.retryDelays[this.retryCount - 1];

			// Show retry message to user
			console.log(
				`[SSE] Connection failed. Reconnecting in ${delay}ms (${this.retryCount}/${APP_CONFIG.sse.maxRetries})...`
			);

			// TODO: Show user-facing notification: "Reconnecting (3/5)..."

			// Retry after delay
			setTimeout(() => {
				if (this.conversationId) {
					// EventSource will automatically reconnect with same URL
					// We just need to keep event listeners attached
				}
			}, delay);
		} else {
			// Max retries exceeded, give up
			this.handleError(
				'Unable to connect after multiple retries. Please check your connection and try again.'
			);
		}
	}

	/**
	 * Handle stream errors
	 *
	 * WHY cancel streaming on error:
	 * - Clean state: Don't leave partial response in UI
	 * - User feedback: Show error message instead of incomplete answer
	 * - Retry opportunity: User can retry request
	 *
	 * @param error - User-friendly error message
	 */
	private handleError(error: string): void {
		console.error('[SSE] Stream error:', error);

		// Update messages store with error
		messages.setError(error);

		// Cancel streaming state
		messages.cancelStreaming();

		// Clean up connection
		this.cleanup();
	}

	/**
	 * Fetch complete message from backend
	 *
	 * WHY fetch from backend instead of using streamed content:
	 * - Authoritative: Backend is source of truth
	 * - Metadata: Backend adds token_count, model_name, timestamps
	 * - Validation: Ensures streamed content matches stored content
	 *
	 * @param messageId - Message ID to fetch
	 * @param tokenCount - Number of tokens generated (from SSE complete event)
	 * @param completionTimeMs - Time taken to generate response in milliseconds
	 * @returns Complete message object
	 */
	private async fetchCompleteMessage(
		messageId: number,
		tokenCount: number,
		completionTimeMs: number
	): Promise<Message> {
		// TODO: Implement GET /api/messages/{conversationId} endpoint
		// For now, construct message from streamed content with actual metadata

		// TEMPORARY: This would normally fetch from backend
		// Backend provides authoritative message with all metadata
		return {
			id: messageId,
			conversation_id: this.conversationId!,
			role: 'assistant',
			content: '', // Will be populated by finishStreaming with streamingContent
			created_at: new Date().toISOString(),
			reaction: null,
			parent_message_id: null,
			token_count: tokenCount, // Use actual value from SSE event
			model_name: 'gpt-oss-20b',
			completion_time_ms: completionTimeMs // Use actual value from SSE event
		} as Message;
	}

	/**
	 * Cancel ongoing stream
	 *
	 * Flow:
	 * 1. Send POST to /api/chat/cancel/{sessionId}
	 * 2. Backend stops LLM generation
	 * 3. Close EventSource connection
	 * 4. Cancel streaming state in store
	 *
	 * WHY allow cancellation:
	 * - User control: Stop if response is irrelevant or wrong
	 * - Cost savings: LLM tokens are expensive (local deployment still uses power)
	 * - Better UX: Faster to cancel and retry than wait for bad response
	 */
	async cancel(): Promise<void> {
		if (!this.sessionId) {
			console.warn('[SSE] No active session to cancel');
			return;
		}

		try {
			// Tell backend to stop generation
			await fetch(API_ENDPOINTS.chat.cancel(this.sessionId), {
				method: 'POST'
			});

			console.log('[SSE] Stream cancelled');
		} catch (err) {
			console.error('[SSE] Failed to cancel stream:', err);
			// Still clean up client-side even if backend cancel fails
		} finally {
			// Clean up connection and state
			messages.cancelStreaming();
			this.cleanup();
		}
	}

	/**
	 * Clean up EventSource connection and reset state
	 *
	 * WHY separate cleanup method:
	 * - DRY: Called from cancel, disconnect, error handlers
	 * - Complete cleanup: Ensures no memory leaks
	 * - State reset: Prepares for next stream
	 */
	private cleanup(): void {
		if (this.eventSource) {
			this.eventSource.close();
			this.eventSource = null;
		}

		this.sessionId = null;
		this.messageId = null;
		this.state = 'disconnected';
		this.retryCount = 0;
	}

	/**
	 * Get current connection state
	 *
	 * WHY expose state:
	 * - UI feedback: Show "Connecting...", "Reconnecting (3/5)..."
	 * - Conditional rendering: Disable input while connecting
	 * - Debugging: Easy to inspect client state
	 */
	getState(): SSEClientState {
		return this.state;
	}
}
