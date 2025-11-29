/**
 * SSE (Server-Sent Events) client for streaming chat responses
 *
 * Features: Exponential backoff retry, graceful error handling, stream cancellation
 * Uses EventSource for one-way streaming (simpler than WebSocket for this use case)
 * Refactored: Retry logic extracted to retry-handler.ts, message factory to message-factory.ts
 */

import { API_ENDPOINTS, APP_CONFIG } from '$lib/config';
import { messages } from '$lib/stores/messages';
import { conversations } from '$lib/stores/conversations';
import { logger } from '$lib/utils/logger';
import { toast } from '$lib/stores/toast';
import { csrfClient } from '$lib/services/core/csrf';
import { RetryHandler } from '$lib/services/sse/retry-handler';
import { fetchCompleteMessage } from '$lib/services/sse/message-factory';
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
	private retryHandler: RetryHandler = new RetryHandler();
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
			this.retryHandler.reset(); // Reset retry state for new connection

			// Step 1: Send POST request to initiate stream
			// Backend creates session and starts LLM generation
			// Get CSRF token for POST request
			const csrfToken = await csrfClient.getToken();
			const response = await fetch(API_ENDPOINTS.chat.stream, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRF-Token': csrfToken
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
			logger.error('Failed to connect SSE', { error: err });
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
			this.retryHandler.reset(); // Reset on successful connection
			logger.info('SSE connection established');
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
				logger.error('Failed to parse SSE token event', { error: err });
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
		 *
		 * WHY update conversation metadata here:
		 * - Real-time updates: Conversation list updates when assistant response completes
		 * - Message count: Increment count to reflect assistant message
		 * - Sorting: Conversation stays at top (most recent activity)
		 */
		this.eventSource.addEventListener('complete', async (event: MessageEvent) => {
			try {
				const data: SSECompleteEvent = JSON.parse(event.data);

				// Fetch complete message from backend (includes all metadata)
				const completeMessage = await fetchCompleteMessage(
					data.message_id,
					this.conversationId!,
					data.token_count,
					data.completion_time_ms
				);

				// Finish streaming in store (adds message to history)
				messages.finishStreaming(completeMessage);

				// Update conversation metadata after assistant message completes
				// This ensures conversation list shows:
				// 1. Accurate message count (includes assistant response)
				// 2. Latest timestamp (conversation moves/stays at top)
				// 3. Real-time updates without page refresh
				if (this.conversationId) {
					// Get message store state synchronously to get current count
					let currentMessageCount = 0;
					const unsubscribe = messages.subscribe((state) => {
						currentMessageCount = state.items.length;
					});
					unsubscribe(); // Immediately unsubscribe

					const now = new Date().toISOString();
					conversations.updateConversation(this.conversationId, {
						message_count: currentMessageCount,
						last_message_at: now,
						updated_at: now
					});
				}

				// Clean up connection
				this.cleanup();
			} catch (err) {
				logger.error('Failed to handle SSE complete event', { error: err });
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
	 * Uses RetryHandler for exponential backoff logic
	 */
	private handleConnectionError(): void {
		this.state = 'error';

		// FIXED (BUG-QA-001): Close current EventSource before retrying
		// Prevents race condition where EventSource auto-reconnects while manual retry is pending
		if (this.eventSource) {
			this.eventSource.close();
			this.eventSource = null;
		}

		// Schedule retry using RetryHandler
		const retryScheduled = this.retryHandler.scheduleRetry(() => {
			if (this.sessionId && this.conversationId) {
				const sseUrl = `${API_ENDPOINTS.chat.stream}/${this.sessionId}`;
				this.eventSource = new EventSource(sseUrl);
				this.setupEventListeners();
			}
		});

		// If max retries exceeded, give up
		if (!retryScheduled) {
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
		logger.error('SSE stream error', { error });
		toast.error(error);

		// Update messages store with error
		messages.setError(error);

		// Cancel streaming state
		messages.cancelStreaming();

		// Clean up connection
		this.cleanup();
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
			logger.warn('No active SSE session to cancel');
			return;
		}

		try {
			// Tell backend to stop generation
			const csrfToken = await csrfClient.getToken();
			await fetch(API_ENDPOINTS.chat.cancel(this.sessionId), {
				method: 'POST',
				headers: {
					'X-CSRF-Token': csrfToken
				}
			});

			logger.info('SSE stream cancelled', { sessionId: this.sessionId });
		} catch (err) {
			logger.error('Failed to cancel SSE stream', { error: err });
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
		this.retryHandler.cleanup(); // Prevent retry race condition

		if (this.eventSource) {
			this.eventSource.close();
			this.eventSource = null;
		}

		this.sessionId = null;
		this.messageId = null;
		this.state = 'disconnected';
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
