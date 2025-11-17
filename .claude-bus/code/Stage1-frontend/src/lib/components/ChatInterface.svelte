<script lang="ts">
/**
 * ChatInterface component
 *
 * Purpose: Main chat area with messages and input
 *
 * Features:
 * - Display conversation messages
 * - Message input with SSE streaming
 * - Real-time token streaming display
 * - Cancel stream functionality
 * - Error handling and retry
 *
 * Layout structure:
 * ┌────────────────────┐
 * │  Conversation Info │  (header)
 * ├────────────────────┤
 * │                    │
 * │   Message List     │  (scrollable)
 * │   (auto-scroll)    │
 * │                    │
 * ├────────────────────┤
 * │  Message Input     │  (fixed bottom)
 * └────────────────────┘
 *
 * WHY single component for entire chat interface:
 * - Cohesion: All chat functionality in one place
 * - State management: Messages, streaming, SSE client share context
 * - Event coordination: Input triggers SSE, SSE updates messages
 */

import { onMount, onDestroy } from 'svelte';
import { currentConversationId } from '$lib/stores/conversations';
import { messages } from '$lib/stores/messages';
import MessageList from './MessageList.svelte';
import MessageInput from './MessageInput.svelte';
import { SSEClient } from '$lib/services/sse-client';
import { fetchMessages } from '$lib/services/api-client';

// Component state
let sseClient: SSEClient;
let loadingMessages = false;
let conversationTitle = 'New Conversation'; // TODO: Load from conversation data

/**
 * Load messages when conversation changes
 *
 * WHY reactive statement instead of onMount:
 * - Conversation switching: Load messages when user selects different conversation
 * - Reactivity: Automatically re-run when $currentConversationId changes
 */
$: if ($currentConversationId) {
	loadConversationMessages($currentConversationId);
}

/**
 * Load messages for conversation
 *
 * Flow:
 * 1. Set loading state
 * 2. Fetch messages from API
 * 3. Update messages store
 * 4. Handle errors
 *
 * @param conversationId - Conversation ID to load messages for
 */
async function loadConversationMessages(conversationId: number) {
	try {
		loadingMessages = true;
		messages.setLoading(true);

		const response = await fetchMessages(conversationId);
		messages.setMessages(response.messages);

		// TODO: Load conversation metadata (title, etc.)
		// conversationTitle = conversation.title;
	} catch (err) {
		console.error('Failed to load messages:', err);
		messages.setError(err instanceof Error ? err.message : 'Failed to load messages');
	} finally {
		loadingMessages = false;
		messages.setLoading(false);
	}
}

/**
 * Handle message send
 *
 * Flow:
 * 1. Validate conversation selected
 * 2. Add user message to store (optimistic UI)
 * 3. Start SSE stream for assistant response
 * 4. SSE client handles token streaming
 *
 * WHY optimistic UI for user message:
 * - Instant feedback: User sees their message immediately
 * - Better UX: No waiting for backend to echo message
 * - Low risk: User message is simple, unlikely to fail
 *
 * @param event - Custom event with message content
 */
async function handleSendMessage(event: CustomEvent<{ message: string }>) {
	if (!$currentConversationId) {
		console.error('No conversation selected');
		return;
	}

	const { message } = event.detail;

	try {
		// Add user message optimistically (assume success)
		const userMessage = {
			id: Date.now(), // Temporary ID (backend will provide real ID)
			conversation_id: $currentConversationId,
			role: 'user' as const,
			content: message,
			created_at: new Date().toISOString(),
			reaction: null,
			parent_message_id: null,
			token_count: message.split(/\s+/).length // Rough estimate
		};

		messages.addMessage(userMessage);

		// Start SSE stream for assistant response
		await sseClient.connect($currentConversationId, message);
	} catch (err) {
		console.error('Failed to send message:', err);
		messages.setError(err instanceof Error ? err.message : 'Failed to send message');
	}
}

/**
 * Handle stream cancellation
 *
 * WHY allow cancellation:
 * - User control: Stop if response is wrong direction
 * - Save resources: LLM tokens are expensive
 * - Better UX: Faster to cancel and retry
 */
function handleCancelStream() {
	sseClient.cancel();
}

/**
 * Initialize SSE client on mount
 */
onMount(() => {
	sseClient = new SSEClient();
});

/**
 * Clean up SSE client on unmount
 *
 * WHY cleanup important:
 * - Memory leaks: EventSource connections stay open
 * - Server resources: Backend keeps stream alive
 * - Best practice: Always clean up subscriptions
 */
onDestroy(() => {
	if (sseClient) {
		sseClient.cancel();
	}
});
</script>

<div class="chat-interface">
	<!-- Chat header -->
	<div class="chat-header">
		<div class="conversation-info">
			<h1 class="conversation-title">{conversationTitle}</h1>
			{#if $currentConversationId}
				<p class="conversation-id">ID: {$currentConversationId}</p>
			{/if}
		</div>

		<!-- Cancel stream button (show during streaming) -->
		{#if $messages.isStreaming}
			<button
				type="button"
				on:click={handleCancelStream}
				class="cancel-button"
				aria-label="Cancel stream"
			>
				<svg
					width="20"
					height="20"
					viewBox="0 0 20 20"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<rect x="4" y="4" width="12" height="12" rx="1" fill="currentColor" />
				</svg>
				<span>Stop</span>
			</button>
		{/if}
	</div>

	<!-- Message list (scrollable area) -->
	<MessageList />

	<!-- Message input (fixed at bottom) -->
	<MessageInput on:send={handleSendMessage} disabled={$messages.isStreaming} />
</div>

<style>
	/**
	 * Chat interface container
	 *
	 * Layout: Flexbox column (header + messages + input)
	 * WHY height: 100%:
	 * - Fill parent: Takes all available space
	 * - Fixed layout: Header and input fixed, messages scroll
	 */
	.chat-interface {
		display: flex;
		flex-direction: column;
		height: 100%;
		background-color: #ffffff;
	}

	/**
	 * Chat header
	 *
	 * WHY sticky positioning:
	 * - Always visible: User always sees conversation context
	 * - Fixed reference: Cancel button easy to find
	 */
	.chat-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 1.5rem;
		border-bottom: 1px solid #e5e7eb; /* Gray 200 */
		background-color: #ffffff;
		position: sticky;
		top: 0;
		z-index: 10;
	}

	/**
	 * Conversation info
	 */
	.conversation-info {
		flex: 1;
	}

	.conversation-title {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: #111827; /* Gray 900 */
	}

	.conversation-id {
		margin: 0.25rem 0 0 0;
		font-size: 0.75rem;
		color: #6b7280; /* Gray 500 */
	}

	/**
	 * Cancel button (during streaming)
	 *
	 * WHY red color:
	 * - Destructive action: Stops ongoing process
	 * - Attention: User notices button easily
	 * - Convention: Stop buttons are often red
	 */
	.cancel-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background-color: #fee2e2; /* Red 100 */
		color: #dc2626; /* Red 600 */
		border: 1px solid #fecaca; /* Red 200 */
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.cancel-button:hover {
		background-color: #fecaca; /* Red 200 */
		border-color: #fca5a5; /* Red 300 */
	}

	/**
	 * Responsive: Smaller header on mobile
	 */
	@media (max-width: 768px) {
		.chat-header {
			padding: 0.75rem 1rem;
		}

		.conversation-title {
			font-size: 1.125rem;
		}
	}
</style>
