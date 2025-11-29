<script lang="ts">
/**
 * ChatHistoryItem component
 *
 * Purpose: Single conversation item in sidebar chat history
 *
 * Features:
 * - Display conversation title and metadata
 * - Active/selected state styling
 * - Delete button with confirmation
 * - Truncate long titles with ellipsis
 * - Show relative timestamp ("2 hours ago")
 *
 * Design decisions:
 * - Hover reveals delete button (keeps UI clean)
 * - Active state uses blue accent (matches selected item pattern)
 * - Title truncation preserves start (more important than end)
 * - Delete confirmation prevents accidental deletion
 */

import { createEventDispatcher, onDestroy } from 'svelte';
import type { Conversation } from '$lib/types';
import { formatRelativeTime } from '$lib/utils/date';

// Props
export let conversation: Conversation;
export let isActive: boolean = false;

// Event dispatcher
const dispatch = createEventDispatcher<{
	select: { conversationId: number };
	delete: { conversationId: number };
}>();

// Component state
let showDeleteConfirm = false;
let deleteConfirmTimeoutId: ReturnType<typeof setTimeout> | null = null;

// Cleanup timeout on destroy to prevent memory leak
onDestroy(() => {
	if (deleteConfirmTimeoutId !== null) {
		clearTimeout(deleteConfirmTimeoutId);
	}
});

/**
 * Handle conversation selection
 *
 * WHY dispatch event instead of directly updating store:
 * - Separation of concerns: Item component doesn't know about routing or stores
 * - Reusability: Can use in different contexts (sidebar, search results, etc.)
 * - Testability: Easy to test event dispatch without mocking stores
 */
function handleSelect() {
	dispatch('select', { conversationId: conversation.id });
}

/**
 * Handle delete button click
 *
 * Two-step deletion:
 * 1. First click: Show confirmation (prevents accidents)
 * 2. Second click: Actually delete
 *
 * WHY two-step instead of modal dialog:
 * - Inline: No modal overlay (simpler, faster)
 * - Context: Confirmation appears right where user clicked
 * - Dismissible: Click outside or Escape cancels (future enhancement)
 */
function handleDeleteClick(event: Event) {
	event.stopPropagation(); // Prevent triggering handleSelect

	if (!showDeleteConfirm) {
		showDeleteConfirm = true;
		// Clear any existing timeout to prevent conflicts
		if (deleteConfirmTimeoutId !== null) {
			clearTimeout(deleteConfirmTimeoutId);
		}
		// Auto-hide confirmation after 3 seconds (UX safety)
		deleteConfirmTimeoutId = setTimeout(() => {
			showDeleteConfirm = false;
			deleteConfirmTimeoutId = null;
		}, 3000);
	}
}

/**
 * Confirm deletion
 *
 * WHY stop propagation:
 * - Prevent selecting conversation when confirming delete
 * - Prevent event bubbling to parent (sidebar click-outside handler)
 */
function handleConfirmDelete(event: Event) {
	event.stopPropagation();
	dispatch('delete', { conversationId: conversation.id });
	showDeleteConfirm = false;
}

/**
 * Cancel deletion
 */
function handleCancelDelete(event: Event) {
	event.stopPropagation();
	showDeleteConfirm = false;
}

// formatRelativeTime moved to $lib/utils/date.ts
// WHY centralized utility: Ensures consistent timezone handling across all components
// See date.ts for detailed explanation of UTC timestamp parsing fix
</script>

<div
	class="chat-history-item"
	class:active={isActive}
	on:click={handleSelect}
	on:keydown={(e) => e.key === 'Enter' && handleSelect()}
	role="button"
	tabindex="0"
	aria-label={`Conversation: ${conversation.title}`}
	aria-current={isActive ? 'true' : 'false'}
>
	<!-- Left: Conversation info -->
	<div class="conversation-info">
		<!-- Title (truncated) -->
		<div class="title" title={conversation.title}>
			{conversation.title}
		</div>

		<!-- Metadata: message count + timestamp -->
		<div class="metadata">
			<span class="message-count">
				{conversation.message_count} {conversation.message_count === 1 ? 'message' : 'messages'}
			</span>
			<span class="separator">•</span>
			<span class="timestamp">
				{formatRelativeTime(conversation.last_message_at)}
			</span>
		</div>
	</div>

	<!-- Right: Delete button (hover to reveal) -->
	<div class="actions">
		{#if showDeleteConfirm}
			<!-- Confirmation buttons -->
			<button
				type="button"
				on:click={handleConfirmDelete}
				class="confirm-delete-button"
				aria-label="Confirm delete"
			>
				<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M16 5L8 13L4 9" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
				</svg>
			</button>
			<button
				type="button"
				on:click={handleCancelDelete}
				class="cancel-delete-button"
				aria-label="Cancel delete"
			>
				<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M15 5L5 15M5 5l15 15" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
				</svg>
			</button>
		{:else}
			<!-- Delete button (hover to reveal) -->
			<button
				type="button"
				on:click={handleDeleteClick}
				class="delete-button"
				aria-label="Delete conversation"
			>
				<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path
						d="M3 5h14M7 5V4a1.5 1.5 0 0 1 1.5-1.5h3a1.5 1.5 0 0 1 1.5 1.5v1m2.5 0v11a2.5 2.5 0 0 1-2.5 2.5h-6a2.5 2.5 0 0 1-2.5-2.5V5h11z"
						stroke="currentColor"
						stroke-width="1.8"
						stroke-linecap="round"
					/>
				</svg>
			</button>
		{/if}
	</div>
</div>

<style>
	/**
	 * Chat history item container (theme-aware)
	 */
	.chat-history-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
		height: 48px;
		padding: 0.5rem 0.75rem;
		margin-bottom: 0.75rem;
		cursor: pointer;
		border-radius: 0.5rem;
		transition: all 0.2s ease;
		background-color: transparent;
	}

	.chat-history-item:hover {
		background-color: var(--bg-hover);
	}

	.chat-history-item.active {
		background-color: var(--accent-muted);
		border-left: 3px solid var(--accent);
	}

	.chat-history-item:focus {
		outline: 2px solid var(--accent);
		outline-offset: -2px;
	}

	.conversation-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		flex: 1;
		min-width: 0;
	}

	.title {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--text-primary);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.active .title {
		color: var(--accent);
	}

	.metadata {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		font-size: 0.75rem;
		color: var(--text-muted);
	}

	.separator {
		color: var(--border-primary);
	}

	.actions {
		display: flex;
		gap: 0.25rem;
		opacity: 0;
		transition: opacity 0.2s ease;
	}

	.chat-history-item:hover .actions,
	.chat-history-item:focus .actions,
	.actions:has(.confirm-delete-button),
	.actions:has(.cancel-delete-button) {
		opacity: 1;
	}

	.delete-button,
	.confirm-delete-button,
	.cancel-delete-button {
		padding: 0.5rem;
		background: none;
		border: none;
		border-radius: 0.375rem;
		color: var(--text-muted);
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.delete-button:hover,
	.cancel-delete-button:hover {
		background-color: var(--bg-hover);
		color: var(--error);
	}

	.confirm-delete-button {
		color: var(--success);
	}

	.confirm-delete-button:hover {
		background-color: var(--success-muted, rgba(22, 163, 74, 0.1));
		color: var(--success);
	}
</style>
