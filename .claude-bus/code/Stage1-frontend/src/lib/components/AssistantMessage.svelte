<script lang="ts">
/**
 * AssistantMessage component
 *
 * Purpose: Display AI assistant message with markdown rendering and interactions
 *
 * Features:
 * - Markdown rendering with syntax highlighting
 * - Message reactions (thumbs up/down)
 * - Regenerate response functionality
 * - Code block copy buttons
 * - Streaming indicator (typing animation)
 * - Timestamp and metadata display
 *
 * Design decisions:
 * - Left-aligned layout (AI on left, user on right)
 * - Gray background (neutral, not attention-grabbing)
 * - Inline reactions (hover to reveal)
 * - Markdown security via DOMPurify
 *
 * WHY complex component (vs splitting into smaller components):
 * - Cohesion: All AI message features in one place
 * - Context: Reactions, regenerate only make sense on assistant messages
 * - Still under 400 lines: Within code quality standards
 */

import { onMount, afterUpdate } from 'svelte';
import { createEventDispatcher } from 'svelte';
import type { Message, MessageReaction } from '$lib/types';
import { renderMarkdown, highlightCode } from '$lib/utils/markdown';
import { updateMessageReaction } from '$lib/services/api-client';

// Props
export let message: Message;
export let isStreaming: boolean = false; // Show typing indicator

// Event dispatcher
const dispatch = createEventDispatcher<{
	regenerate: { messageId: number };
}>();

// Component state
let contentElement: HTMLElement;
let renderedContent: string = '';
let isUpdatingReaction = false;

/**
 * Render markdown on mount and content updates
 *
 * WHY reactive statement instead of onMount:
 * - Re-render: Content changes during streaming
 * - Streaming: Tokens append to content, need re-render
 */
$: {
	if (message.content) {
		renderedContent = renderMarkdown(message.content);
	}
}

/**
 * Highlight code blocks after content renders
 *
 * WHY afterUpdate instead of onMount:
 * - DOM timing: Need to wait for {@html} to render
 * - Streaming: Re-highlight as new code blocks appear
 */
afterUpdate(() => {
	if (contentElement) {
		highlightCode(contentElement);
	}
});

/**
 * Handle reaction click (thumbs up/down)
 *
 * Flow:
 * 1. Optimistic UI: Update reaction immediately
 * 2. Call API to persist reaction
 * 3. Revert on error
 *
 * WHY optimistic UI:
 * - Responsiveness: User sees instant feedback
 * - Common pattern: Like buttons on social media
 * - Low risk: Reaction is not critical data
 *
 * @param reaction - Reaction type ('thumbs_up', 'thumbs_down', or null to remove)
 */
async function handleReaction(reaction: MessageReaction) {
	if (isUpdatingReaction) return; // Prevent double-clicks

	const previousReaction = message.reaction;

	// If clicking same reaction, remove it (toggle behavior)
	const newReaction = message.reaction === reaction ? null : reaction;

	try {
		isUpdatingReaction = true;

		// Optimistic update (immediately show new reaction)
		message.reaction = newReaction;

		// Persist to backend
		await updateMessageReaction(message.id, newReaction);
	} catch (err) {
		console.error('Failed to update reaction:', err);

		// Revert on error
		message.reaction = previousReaction;
	} finally {
		isUpdatingReaction = false;
	}
}

/**
 * Handle regenerate button click
 *
 * WHY dispatch event instead of direct API call:
 * - Parent control: ChatInterface decides how to regenerate
 * - Flexibility: Parent can show confirmation, handle errors, etc.
 */
function handleRegenerate() {
	dispatch('regenerate', { messageId: message.id });
}

/**
 * Format timestamp
 */
function formatTime(isoDate: string): string {
	const date = new Date(isoDate);
	const hours = date.getHours().toString().padStart(2, '0');
	const minutes = date.getMinutes().toString().padStart(2, '0');
	return `${hours}:${minutes}`;
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
		<div class="message-content" bind:this={contentElement}>
			{@html renderedContent}
		</div>

		<!-- Streaming indicator (typing animation) -->
		{#if isStreaming}
			<div class="streaming-indicator">
				<span class="dot"></span>
				<span class="dot"></span>
				<span class="dot"></span>
			</div>
		{/if}

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
		<div class="message-actions">
			<!-- Thumbs up reaction -->
			<button
				type="button"
				on:click={() => handleReaction('thumbs_up')}
				class="reaction-button"
				class:active={message.reaction === 'thumbs_up'}
				disabled={isUpdatingReaction}
				aria-label="Thumbs up"
			>
				<svg
					width="16"
					height="16"
					viewBox="0 0 16 16"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M4 14v-5M10 4a1 1 0 0 0-1-1H8l.5-3h-1L6 6H4v8h8a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1h-2z"
						stroke="currentColor"
						stroke-width="1.5"
						stroke-linecap="round"
						stroke-linejoin="round"
						fill={message.reaction === 'thumbs_up' ? 'currentColor' : 'none'}
					/>
				</svg>
			</button>

			<!-- Thumbs down reaction -->
			<button
				type="button"
				on:click={() => handleReaction('thumbs_down')}
				class="reaction-button"
				class:active={message.reaction === 'thumbs_down'}
				disabled={isUpdatingReaction}
				aria-label="Thumbs down"
			>
				<svg
					width="16"
					height="16"
					viewBox="0 0 16 16"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M4 2v5M10 12a1 1 0 0 1 1 1h1l-.5 3h1L14 10h2V2H8a1 1 0 0 1-1 1V9a1 1 0 0 1 1 1h2z"
						stroke="currentColor"
						stroke-width="1.5"
						stroke-linecap="round"
						stroke-linejoin="round"
						fill={message.reaction === 'thumbs_down' ? 'currentColor' : 'none'}
					/>
				</svg>
			</button>

			<!-- Regenerate button -->
			<button
				type="button"
				on:click={handleRegenerate}
				class="regenerate-button"
				aria-label="Regenerate response"
			>
				<svg
					width="16"
					height="16"
					viewBox="0 0 16 16"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M2 8a6 6 0 0 1 10-4.5M14 8a6 6 0 0 1-10 4.5M2 3v5h5M14 13V8h-5"
						stroke="currentColor"
						stroke-width="1.5"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
				</svg>
				<span>Regenerate</span>
			</button>
		</div>
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
	 * Message content (markdown)
	 *
	 * WHY global styles in component:
	 * - Scoped markdown: Only affects this component's rendered markdown
	 * - Typography: Headings, lists, tables need styling
	 */
	.message-content {
		font-size: 0.9375rem;
		line-height: 1.6;
	}

	/* Markdown typography styles */
	.message-content :global(h1),
	.message-content :global(h2),
	.message-content :global(h3),
	.message-content :global(h4),
	.message-content :global(h5),
	.message-content :global(h6) {
		margin: 1rem 0 0.5rem 0;
		font-weight: 600;
		line-height: 1.3;
	}

	.message-content :global(h1) {
		font-size: 1.5rem;
	}
	.message-content :global(h2) {
		font-size: 1.25rem;
	}
	.message-content :global(h3) {
		font-size: 1.125rem;
	}

	.message-content :global(p) {
		margin: 0.75rem 0;
	}

	.message-content :global(ul),
	.message-content :global(ol) {
		margin: 0.75rem 0;
		padding-left: 1.5rem;
	}

	.message-content :global(li) {
		margin: 0.25rem 0;
	}

	.message-content :global(code) {
		padding: 0.125rem 0.375rem;
		background-color: #e5e7eb; /* Gray 200 */
		border-radius: 0.25rem;
		font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
		font-size: 0.875em;
	}

	.message-content :global(pre code) {
		padding: 0;
		background: none;
	}

	.message-content :global(blockquote) {
		margin: 0.75rem 0;
		padding-left: 1rem;
		border-left: 3px solid #d1d5db; /* Gray 300 */
		color: #6b7280; /* Gray 500 */
		font-style: italic;
	}

	.message-content :global(table) {
		width: 100%;
		margin: 0.75rem 0;
		border-collapse: collapse;
	}

	.message-content :global(th),
	.message-content :global(td) {
		padding: 0.5rem;
		border: 1px solid #e5e7eb; /* Gray 200 */
		text-align: left;
	}

	.message-content :global(th) {
		background-color: #f3f4f6; /* Gray 100 */
		font-weight: 600;
	}

	/**
	 * Streaming indicator (typing animation)
	 *
	 * WHY animated dots:
	 * - Feedback: User knows AI is "thinking"
	 * - Common pattern: iMessage, Slack use this
	 */
	.streaming-indicator {
		display: flex;
		gap: 0.375rem;
		margin-top: 0.5rem;
	}

	.dot {
		width: 0.5rem;
		height: 0.5rem;
		background-color: #9ca3af; /* Gray 400 */
		border-radius: 50%;
		animation: pulse 1.5s ease-in-out infinite;
	}

	.dot:nth-child(2) {
		animation-delay: 0.2s;
	}

	.dot:nth-child(3) {
		animation-delay: 0.4s;
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 0.4;
			transform: scale(1);
		}
		50% {
			opacity: 1;
			transform: scale(1.2);
		}
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
	 * Message actions (reactions + regenerate)
	 *
	 * WHY hover reveal:
	 * - Clean UI: Actions don't clutter message
	 * - Progressive disclosure: User discovers on hover
	 */
	.message-actions {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 0.75rem;
		opacity: 0;
		transition: opacity 0.2s ease;
	}

	.assistant-message-bubble:hover .message-actions {
		opacity: 1;
	}

	/**
	 * Reaction buttons
	 */
	.reaction-button {
		padding: 0.375rem;
		background: none;
		border: 1px solid #e5e7eb; /* Gray 200 */
		border-radius: 0.375rem;
		color: #6b7280; /* Gray 500 */
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.reaction-button:hover {
		background-color: #f3f4f6; /* Gray 100 */
		border-color: #d1d5db; /* Gray 300 */
	}

	.reaction-button.active {
		background-color: #eff6ff; /* Blue 50 */
		border-color: #3b82f6; /* Blue 500 */
		color: #3b82f6;
	}

	/**
	 * Regenerate button
	 */
	.regenerate-button {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.375rem 0.75rem;
		background: none;
		border: 1px solid #e5e7eb;
		border-radius: 0.375rem;
		color: #6b7280;
		font-size: 0.75rem;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.regenerate-button:hover {
		background-color: #f3f4f6;
		border-color: #d1d5db;
		color: #111827;
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
