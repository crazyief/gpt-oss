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
import { updateMessageReaction } from '$lib/services/api-client';

// Props
export let messageId: number;
export let currentReaction: MessageReaction | null = null;

// Event dispatcher
const dispatch = createEventDispatcher<{
	regenerate: { messageId: number };
}>();

// Component state
let isUpdatingReaction = false;
let localReaction = currentReaction;

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
		await updateMessageReaction(messageId, newReaction);
	} catch (err) {
		console.error('Failed to update reaction:', err);

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

	.reaction-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
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
</style>
