<script lang="ts">
/**
 * MessageList component
 *
 * Purpose: Scrollable list of messages with auto-scroll and streaming support
 *
 * Features:
 * - Render user and assistant messages
 * - Auto-scroll to bottom on new messages
 * - Conditional auto-scroll (only if user at bottom)
 * - Loading state for fetching history
 * - Empty state for new conversations
 * - Streaming message display
 *
 * Design decisions:
 * - Auto-scroll only if user at bottom (preserves scroll position when reading)
 * - 100px threshold for "at bottom" detection (accounts for slight scroll)
 * - Scroll behavior: smooth for better UX
 *
 * WHY conditional auto-scroll instead of always scrolling:
 * - User control: If user scrolled up to read, don't interrupt
 * - UX pattern: Slack, Discord, WhatsApp use this behavior
 * - Prevents frustration: User can read old messages without being pulled down
 */

import { onMount, afterUpdate } from 'svelte';
import { messages } from '$lib/stores/messages';
import UserMessage from './UserMessage.svelte';
import AssistantMessage from './AssistantMessage.svelte';
import { APP_CONFIG } from '$lib/config';
import type { Message } from '$lib/types';

// Component state
let scrollContainer: HTMLElement;
let wasAtBottom = true; // Track if user was at bottom before update

/**
 * Check if scroll position is at bottom
 *
 * WHY 100px threshold:
 * - Flexible: User doesn't have to be exactly at bottom
 * - Mobile-friendly: Touch scrolling is imprecise
 * - Prevents edge cases: Rounding errors in scroll calculations
 *
 * Formula: scrollTop + clientHeight >= scrollHeight - threshold
 * - scrollTop: Current scroll position from top
 * - clientHeight: Visible height of container
 * - scrollHeight: Total height of content
 * - If sum >= scrollHeight - 100, user is "at bottom"
 *
 * @returns True if user is at or near bottom of scroll
 */
function isAtBottom(): boolean {
	if (!scrollContainer) return true;

	const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
	const threshold = APP_CONFIG.chat.autoScrollThreshold;

	return scrollTop + clientHeight >= scrollHeight - threshold;
}

/**
 * Scroll to bottom of message list
 *
 * WHY smooth scroll:
 * - Better UX: Sudden jumps are jarring
 * - User awareness: Smooth scroll shows context of movement
 *
 * WHY optional instant scroll:
 * - Initial load: Instant scroll on first render
 * - User action: Instant scroll when user sends message
 * - Streaming: Smooth scroll as tokens appear
 *
 * @param instant - Skip smooth animation (default: false)
 */
function scrollToBottom(instant: boolean = false) {
	if (!scrollContainer) return;

	scrollContainer.scrollTo({
		top: scrollContainer.scrollHeight,
		behavior: instant ? 'auto' : 'smooth'
	});
}

/**
 * Track scroll position before updates
 *
 * WHY beforeUpdate instead of checking in afterUpdate:
 * - Timing: Need to know state *before* DOM changes
 * - Prevents flicker: Decide whether to scroll based on previous position
 */
function beforeUpdate() {
	wasAtBottom = isAtBottom();
}

/**
 * Auto-scroll to bottom after updates (if appropriate)
 *
 * Scroll conditions:
 * 1. New message added AND user was at bottom (don't interrupt reading)
 * 2. Streaming in progress (always follow streaming content)
 *
 * WHY afterUpdate instead of reactive statement:
 * - DOM timing: Need to wait for new messages to render
 * - Height calculation: scrollHeight only correct after render
 */
afterUpdate(() => {
	if (wasAtBottom || $messages.isStreaming) {
		scrollToBottom();
	}
});

/**
 * Scroll to bottom on initial mount
 *
 * WHY instant scroll on mount:
 * - Initial load: User hasn't scrolled yet
 * - Performance: Instant is faster than smooth for large lists
 */
onMount(() => {
	scrollToBottom(true);
});
</script>

<div class="message-list-container" bind:this={scrollContainer}>
	{#if $messages.isLoading}
		<!-- Loading state -->
		<div class="loading-state">
			<div class="spinner"></div>
			<p>Loading messages...</p>
		</div>
	{:else if $messages.error}
		<!-- Error state -->
		<div class="error-state" role="alert">
			<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
				<path
					d="M12 9v2m0 4h.01M12 21a9 9 0 1 1 0-18 9 9 0 0 1 0 18z"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
				/>
			</svg>
			<p>{$messages.error}</p>
		</div>
	{:else if $messages.items.length === 0 && !$messages.isStreaming}
		<!-- Empty state (new conversation) -->
		<div class="empty-state">
			<svg
				width="64"
				height="64"
				viewBox="0 0 64 64"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M16 40V20a4 4 0 0 1 4-4h24a4 4 0 0 1 4 4v16a4 4 0 0 1-4 4H24l-8 8v-8z"
					stroke="currentColor"
					stroke-width="3"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
			<h3>Start a conversation</h3>
			<p>Ask a question or send a message to begin</p>
		</div>
	{:else}
		<!-- Message list -->
		<div class="messages">
			<!-- Render persisted messages -->
			{#each $messages.items as message (message.id)}
				{#if message.role === 'user'}
					<UserMessage {message} />
				{:else}
					<AssistantMessage {message} isStreaming={false} />
				{/if}
			{/each}

			<!-- Render streaming message (temporary, not persisted yet) -->
			{#if $messages.isStreaming && $messages.streamingMessageId}
				<AssistantMessage
					message={{
						id: $messages.streamingMessageId,
						conversation_id: 0, // Temporary
						role: 'assistant',
						content: $messages.streamingContent,
						created_at: new Date().toISOString(),
						reaction: null,
						parent_message_id: null,
						token_count: 0
					}}
					isStreaming={true}
				/>
			{/if}
		</div>
	{/if}
</div>

<style>
	/**
	 * Message list container
	 *
	 * WHY flex-direction: column:
	 * - Vertical layout: Messages stack vertically
	 * - Natural flow: New messages appear at bottom
	 *
	 * WHY overflow-y: auto:
	 * - Scrollable: Container has fixed height, content scrolls
	 * - Auto scrollbar: Only appears when content overflows
	 */
	.message-list-container {
		flex: 1; /* Fill available space in chat interface */
		overflow-y: auto;
		overflow-x: hidden;
		padding: 1rem 0;
		background-color: #ffffff;
	}

	/**
	 * Messages container
	 *
	 * WHY separate container from scroll container:
	 * - Padding: Messages have vertical padding, scroll container doesn't
	 * - Spacing: Gap between messages
	 */
	.messages {
		display: flex;
		flex-direction: column;
		gap: 0.5rem; /* Space between messages */
	}

	/**
	 * Loading state
	 */
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		gap: 1rem;
		color: #6b7280; /* Gray 500 */
	}

	.spinner {
		width: 2rem;
		height: 2rem;
		border: 3px solid #e5e7eb; /* Gray 200 */
		border-top-color: #3b82f6; /* Blue 500 */
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	/**
	 * Error state
	 */
	.error-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		gap: 0.5rem;
		padding: 2rem;
		color: #dc2626; /* Red 600 */
		text-align: center;
	}

	/**
	 * Empty state
	 *
	 * WHY friendly empty state:
	 * - Guidance: Tells user what to do
	 * - Welcoming: Encourages first message
	 * - Not an error: Empty conversation is normal state
	 */
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		gap: 1rem;
		padding: 2rem;
		text-align: center;
		color: #6b7280; /* Gray 500 */
	}

	.empty-state svg {
		color: #d1d5db; /* Gray 300 */
	}

	.empty-state h3 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: #111827; /* Gray 900 */
	}

	.empty-state p {
		margin: 0;
		font-size: 0.9375rem;
		color: #6b7280; /* Gray 500 */
	}

	/**
	 * Scrollbar styling (WebKit browsers)
	 */
	.message-list-container::-webkit-scrollbar {
		width: 8px;
	}

	.message-list-container::-webkit-scrollbar-track {
		background: #f9fafb; /* Gray 50 */
	}

	.message-list-container::-webkit-scrollbar-thumb {
		background: #d1d5db; /* Gray 300 */
		border-radius: 4px;
	}

	.message-list-container::-webkit-scrollbar-thumb:hover {
		background: #9ca3af; /* Gray 400 */
	}
</style>
