<script lang="ts">
/**
 * MessageActions component
 *
 * Purpose: Action buttons for assistant messages (reactions, regenerate)
 *
 * Features:
 * - Thumbs up/down reactions (toggle behavior)
 * - Regenerate response button
 * - Optimistic UI updates
 * - Hover reveal (progressive disclosure)
 *
 * Design decisions:
 * - Optimistic UI: Update immediately, revert on error
 * - Toggle behavior: Click same reaction to remove
 * - Event dispatch: Parent controls regenerate logic
 *
 * WHY separate component:
 * - Reusability: Can be used on other message types
 * - Complex state: Reaction handling has its own logic
 * - Clear separation: UI actions vs content display
 */

import { createEventDispatcher } from 'svelte';
import type { MessageReaction } from '$lib/types';
import { messages as messagesApi } from '$lib/services/api';
import { logger } from '$lib/utils/logger';

// Props
export let messageId: number;
export let currentReaction: MessageReaction | null = null;
export let messageContent: string = ''; // For copy functionality
export let hideCopyButton: boolean = false; // Hide copy button (when parent has its own)

// Event dispatcher
const dispatch = createEventDispatcher<{
	regenerate: { messageId: number };
}>();

// Component state
let isUpdatingReaction = false;
let localReaction = currentReaction;
let showCopiedFeedback = false;

/**
 * Sync local reaction with prop changes
 *
 * WHY reactive statement:
 * - Prop updates: Parent may update reaction externally
 * - Two-way sync: Keep local state in sync with prop
 */
$: localReaction = currentReaction;

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
 * @param reaction - Reaction type ('thumbs_up', 'thumbs_down')
 */
async function handleReaction(reaction: MessageReaction) {
	if (isUpdatingReaction) return; // Prevent double-clicks

	const previousReaction = localReaction;

	// If clicking same reaction, remove it (toggle behavior)
	const newReaction = localReaction === reaction ? null : reaction;

	try {
		isUpdatingReaction = true;

		// Optimistic update (immediately show new reaction)
		localReaction = newReaction;
		currentReaction = newReaction; // Update prop binding

		// Persist to backend
		await messagesApi.updateMessageReaction(messageId, newReaction);
	} catch (err) {
		logger.error('Failed to update reaction:', { error: err });

		// Revert on error
		localReaction = previousReaction;
		currentReaction = previousReaction;
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
	dispatch('regenerate', { messageId });
}

/**
 * Copy message content to clipboard
 */
async function handleCopy() {
	try {
		await navigator.clipboard.writeText(messageContent);
		showCopiedFeedback = true;

		// Hide feedback after 2 seconds
		setTimeout(() => {
			showCopiedFeedback = false;
		}, 2000);
	} catch (err) {
		logger.error('Failed to copy message:', { error: err });
	}
}
</script>

<div class="message-actions">
	<!-- Thumbs up reaction -->
	<button
		type="button"
		on:click={() => handleReaction('thumbs_up')}
		class="reaction-button"
		class:active={localReaction === 'thumbs_up'}
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
				fill={localReaction === 'thumbs_up' ? 'currentColor' : 'none'}
			/>
		</svg>
	</button>

	<!-- Thumbs down reaction -->
	<button
		type="button"
		on:click={() => handleReaction('thumbs_down')}
		class="reaction-button"
		class:active={localReaction === 'thumbs_down'}
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
				fill={localReaction === 'thumbs_down' ? 'currentColor' : 'none'}
			/>
		</svg>
	</button>

	<!-- Copy button (conditionally hidden when parent has its own) -->
	{#if !hideCopyButton}
		<button
			type="button"
			on:click={handleCopy}
			class="copy-button"
			aria-label="Copy message"
		>
			{#if showCopiedFeedback}
				<svg
					width="16"
					height="16"
					viewBox="0 0 16 16"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M13 3L5.5 10.5L3 8"
						stroke="currentColor"
						stroke-width="1.5"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
				</svg>
				<span>Copied!</span>
			{:else}
				<svg
					width="16"
					height="16"
					viewBox="0 0 16 16"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M5 2H11C11.5523 2 12 2.44772 12 3V11M5 5H4C3.44772 5 3 5.44772 3 6V13C3 13.5523 3.44772 14 4 14H11C11.5523 14 12 13.5523 12 13V12"
						stroke="currentColor"
						stroke-width="1.5"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
				</svg>
				<span>Copy</span>
			{/if}
		</button>
	{/if}

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

<style>
	/**
	 * Message actions (reactions + regenerate + copy)
	 *
	 * WHY flex-wrap: nowrap:
	 * - User request: All buttons on same horizontal line
	 * - Super-AI recommendation: Use horizontal scroll on mobile if needed
	 * - flex-shrink: 0 on buttons prevents compression
	 */
	.message-actions {
		display: flex;
		align-items: center;
		flex-wrap: nowrap; /* Keep all buttons on same line */
		gap: 0.5rem;
		margin-top: 0.75rem;
		overflow-x: auto; /* Allow horizontal scroll on narrow screens */
		overflow-y: hidden;
		-webkit-overflow-scrolling: touch; /* Smooth scrolling on iOS */
		scrollbar-width: thin; /* Firefox */
		padding-bottom: 0.25rem; /* Space for scrollbar */
	}

	/* Scrollbar styling */
	.message-actions::-webkit-scrollbar {
		height: 4px;
	}

	.message-actions::-webkit-scrollbar-thumb {
		background: rgba(0, 0, 0, 0.2);
		border-radius: 2px;
	}

	/* Hide scrollbar on desktop where buttons fit */
	@media (min-width: 640px) {
		.message-actions {
			overflow-x: visible;
		}
	}

	/**
	 * Reaction buttons - Modern pill style with hover glow
	 */
	.reaction-button {
		flex-shrink: 0;
		padding: 0.5rem;
		background: linear-gradient(135deg, #fafbfc 0%, #f3f4f6 100%);
		border: 1px solid #e2e8f0;
		border-radius: 0.5rem;
		color: #64748b;
		cursor: pointer;
		transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
		min-height: 36px;
		min-width: 36px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	}

	.reaction-button:hover {
		background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
		border-color: #cbd5e1;
		color: #475569;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
		transform: translateY(-1px) scale(1.05);
	}

	.reaction-button.active {
		background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
		border-color: #60a5fa;
		color: #2563eb;
		box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3), 0 0 0 3px rgba(191, 219, 254, 0.2);
	}

	.reaction-button.active:hover {
		box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4), 0 0 0 4px rgba(191, 219, 254, 0.25);
	}

	.reaction-button:active {
		transform: scale(0.95);
	}

	.reaction-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}

	/**
	 * Copy button - Elegant gradient pill
	 */
	.copy-button {
		flex-shrink: 0;
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.5rem 0.875rem;
		background: linear-gradient(135deg, #fafbfc 0%, #f1f5f9 100%);
		border: 1px solid #e2e8f0;
		border-radius: 0.5rem;
		color: #64748b;
		font-size: 0.75rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
		white-space: nowrap;
		min-height: 36px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	}

	.copy-button:hover {
		background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
		border-color: #7dd3fc;
		color: #0284c7;
		box-shadow: 0 4px 8px rgba(6, 182, 212, 0.2);
		transform: translateY(-1px);
	}

	.copy-button:active {
		transform: scale(0.98);
	}

	/**
	 * Regenerate button - Neutral color (user requested: no special color)
	 */
	.regenerate-button {
		flex-shrink: 0;
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.5rem 0.875rem;
		background: linear-gradient(135deg, #fafbfc 0%, #f1f5f9 100%);
		border: 1px solid #e2e8f0;
		border-radius: 0.5rem;
		color: #64748b;
		font-size: 0.75rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
		white-space: nowrap;
		min-height: 36px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	}

	.regenerate-button:hover {
		background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
		border-color: #cbd5e1;
		color: #475569;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
		transform: translateY(-1px) scale(1.02);
	}

	.regenerate-button:active {
		transform: scale(0.98);
	}

	.regenerate-button svg {
		transition: transform 0.3s ease;
	}

	.regenerate-button:hover svg {
		transform: rotate(180deg);
	}
</style>
