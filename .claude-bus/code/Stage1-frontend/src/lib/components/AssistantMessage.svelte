<script lang="ts">
/**
 * AssistantMessage component
 *
 * Purpose: Container for AI assistant messages with markdown rendering and interactions
 *
 * Features:
 * - Message layout (avatar + bubble)
 * - Timestamp and metadata display
 * - Composed from specialized sub-components
 *
 * Sub-components:
 * - MessageContent: Markdown rendering with syntax highlighting
 * - StreamingIndicator: Typing animation during AI response
 * - MessageActions: Reactions and regenerate button
 *
 * Design decisions:
 * - Left-aligned layout (AI on left, user on right)
 * - Gray background (neutral, not attention-grabbing)
 * - Composition pattern: Smaller, focused sub-components
 *
 * WHY refactored into smaller components:
 * - Code quality: Original 546 lines exceeded 400-line limit
 * - Maintainability: Each component has single responsibility
 * - Reusability: Sub-components can be used elsewhere
 * - Testability: Easier to test smaller, focused components
 */

import { createEventDispatcher } from 'svelte';
import type { Message } from '$lib/types';
import MessageContent from './MessageContent.svelte';
import StreamingIndicator from './StreamingIndicator.svelte';
import MessageActions from './MessageActions.svelte';

// Props
export let message: Message;
export let isStreaming: boolean = false; // Show typing indicator

// Event dispatcher for regenerate event
const dispatch = createEventDispatcher<{
	regenerate: { messageId: number };
}>();

/**
 * Format timestamp for display
 *
 * @param isoDate - ISO 8601 timestamp string
 * @returns Formatted time string (HH:MM)
 */
function formatTime(isoDate: string): string {
	const date = new Date(isoDate);
	const hours = date.getHours().toString().padStart(2, '0');
	const minutes = date.getMinutes().toString().padStart(2, '0');
	return `${hours}:${minutes}`;
}

/**
 * Handle regenerate event from MessageActions
 *
 * WHY pass-through event:
 * - Parent control: ChatInterface needs to handle regeneration
 * - Decoupling: MessageActions doesn't know about parent logic
 */
function handleRegenerate(event: CustomEvent<{ messageId: number }>) {
	dispatch('regenerate', event.detail);
}
</script>

<div class="assistant-message-container">
	<!-- Assistant avatar/icon -->
	<div class="assistant-avatar">
		<svg
			width="24"
			height="24"
			viewBox="0 0 24 24"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
		>
			<!-- AI/robot icon -->
			<rect x="5" y="5" width="14" height="14" rx="2" stroke="currentColor" stroke-width="2" />
			<circle cx="9" cy="10" r="1" fill="currentColor" />
			<circle cx="15" cy="10" r="1" fill="currentColor" />
			<path d="M9 14h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
		</svg>
	</div>

	<!-- Message bubble -->
	<div class="assistant-message-bubble">
		<!-- Message content (markdown rendered) -->
		<MessageContent content={message.content} {isStreaming} />

		<!-- Streaming indicator (typing animation) -->
		<StreamingIndicator
			{isStreaming}
			tokenCount={message.token_count}
			completionTimeMs={message.completion_time_ms}
		/>

		<!-- Message footer (timestamp + metadata) -->
		<div class="message-footer">
			<!-- Timestamp -->
			<span class="timestamp" title={message.created_at}>
				{formatTime(message.created_at)}
			</span>

			<!-- Metadata (token count, model) -->
			{#if message.token_count > 0}
				<span class="metadata-separator">•</span>
				<span class="metadata">
					{message.token_count} tokens
				</span>
			{/if}
			{#if message.completion_time_ms}
				<span class="metadata-separator">•</span>
				<span class="metadata">
					{(message.completion_time_ms / 1000).toFixed(1)}s
				</span>
			{/if}
		</div>

		<!-- Action buttons (reactions + regenerate) -->
		<MessageActions
			messageId={message.id}
			currentReaction={message.reaction}
			on:regenerate={handleRegenerate}
		/>
	</div>
</div>

<style>
	/**
	 * Assistant message container
	 *
	 * Layout: Avatar (left) + bubble (right)
	 */
	.assistant-message-container {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		margin: 1rem 0;
		padding: 0 1rem;
	}

	/**
	 * Assistant avatar
	 *
	 * WHY different color from user avatar:
	 * - Visual distinction: Easy to scan who said what
	 * - Neutral color: Gray represents AI/system
	 */
	.assistant-avatar {
		flex-shrink: 0;
		width: 2rem;
		height: 2rem;
		display: flex;
		align-items: center;
		justify-content: center;
		background-color: #f3f4f6; /* Gray 100 */
		color: #6b7280; /* Gray 500 */
		border-radius: 50%;
	}

	/**
	 * Assistant message bubble
	 *
	 * WHY gray background instead of gradient:
	 * - Neutral: AI is informational, not action-oriented
	 * - Readability: Light background for dark text (markdown)
	 * - Distinction: Different from user's blue gradient
	 */
	.assistant-message-bubble {
		max-width: 70%;
		padding: 0.75rem 1rem;
		background-color: #f9fafb; /* Gray 50 */
		color: #111827; /* Gray 900 */
		border-radius: 1rem 1rem 1rem 0; /* Rounded except bottom-left */
		border: 1px solid #e5e7eb; /* Gray 200 */
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	}

	/**
	 * Message footer (timestamp + metadata)
	 */
	.message-footer {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		margin-top: 0.5rem;
		font-size: 0.75rem;
		color: #9ca3af; /* Gray 400 */
	}

	.metadata-separator {
		color: #d1d5db; /* Gray 300 */
	}

	/**
	 * Responsive: Full-width on mobile
	 */
	@media (max-width: 768px) {
		.assistant-message-bubble {
			max-width: 85%;
		}
	}
</style>
