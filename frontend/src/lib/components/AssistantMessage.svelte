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
import { formatTime } from '$lib/utils/date';
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

// formatTime moved to $lib/utils/date.ts
// WHY centralized utility: Ensures consistent UTC timestamp handling across all components

/**
 * Calculate tokens per second
 *
 * @param tokenCount - Number of tokens generated
 * @param completionTimeMs - Time taken in milliseconds
 * @returns Tokens per second, or null if data unavailable
 */
function calculateTokensPerSecond(tokenCount: number, completionTimeMs: number): number | null {
	if (!tokenCount || !completionTimeMs || completionTimeMs === 0) {
		return null;
	}
	return tokenCount / (completionTimeMs / 1000);
}

// Calculate tokens/sec for display
$: tokensPerSec = calculateTokensPerSecond(message.token_count, message.completion_time_ms);

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
			{#if tokensPerSec !== null}
				<span class="metadata-separator">•</span>
				<span class="metadata" title="Tokens per second">
					{tokensPerSec.toFixed(1)} tok/s
				</span>
			{/if}
		</div>

		<!-- Action buttons (reactions + copy + regenerate - all horizontal) -->
		<MessageActions
			messageId={message.id}
			currentReaction={message.reaction}
			messageContent={message.content}
			hideCopyButton={false}
			on:regenerate={handleRegenerate}
		/>
	</div>
</div>

<style>
	/**
	 * Assistant message container - Smooth entrance animation
	 */
	.assistant-message-container {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		margin: 1rem 0;
		padding: 0 1rem;
		animation: slideIn 0.3s ease-out;
	}

	/**
	 * Assistant avatar - Modern gradient with glow
	 */
	.assistant-avatar {
		flex-shrink: 0;
		width: 2.25rem;
		height: 2.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
		color: #0284c7;
		border-radius: 50%;
		border: 2px solid #bae6fd;
		box-shadow: 0 2px 8px rgba(2, 132, 199, 0.15), 0 0 0 4px rgba(186, 230, 253, 0.1);
		transition: all 0.3s ease;
	}

	.assistant-avatar:hover {
		transform: scale(1.05);
		box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25), 0 0 0 6px rgba(186, 230, 253, 0.15);
	}

	/**
	 * Assistant message bubble - Soft blue gradient with glassmorphism
	 *
	 * User requested: Better background color (more visually interesting)
	 * Changed from white-gray to soft blue gradient
	 */
	.assistant-message-bubble {
		position: relative;
		max-width: 70%;
		padding: 1rem 1.25rem;
		background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); /* Soft blue gradient */
		color: #1e293b;
		border-radius: 1.25rem 1.25rem 1.25rem 0.25rem;
		border: 1px solid rgba(186, 230, 253, 0.6);
		box-shadow: 0 4px 12px rgba(6, 182, 212, 0.12), 0 1px 3px rgba(14, 165, 233, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.9);
		backdrop-filter: blur(10px);
		transition: all 0.2s ease;
	}

	/* Subtle hover effect for interactivity */
	.assistant-message-bubble:hover {
		box-shadow: 0 6px 16px rgba(6, 182, 212, 0.18), 0 2px 4px rgba(14, 165, 233, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.9);
		transform: translateY(-1px);
	}

	/* Glassmorphism highlight */
	.assistant-message-bubble::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 1px;
		background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.8) 50%, transparent 100%);
		border-radius: 1.25rem 1.25rem 0 0;
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
