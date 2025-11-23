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

import { createEventDispatcher } from 'svelte';
import type { Conversation } from '$lib/types';

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
		// Auto-hide confirmation after 3 seconds (UX safety)
		setTimeout(() => {
			showDeleteConfirm = false;
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

/**
 * Format relative timestamp
 *
 * Examples: "2 minutes ago", "5 hours ago", "3 days ago"
 *
 * WHY relative instead of absolute timestamp:
 * - Relevance: "2 hours ago" is more meaningful than "14:32"
 * - Scanning: User can quickly identify recent conversations
 * - Space-efficient: Shorter than full datetime
 *
 * @param isoDate - ISO 8601 datetime string
 * @returns Human-readable relative time string
 */
function formatRelativeTime(isoDate: string | null): string {
	if (!isoDate) return 'No messages';

	const date = new Date(isoDate);
	const now = new Date();
	const diffMs = now.getTime() - date.getTime();
	const diffMins = Math.floor(diffMs / 60000);
	const diffHours = Math.floor(diffMs / 3600000);
	const diffDays = Math.floor(diffMs / 86400000);

	if (diffMins < 1) return 'Just now';
	if (diffMins < 60) return `${diffMins}m ago`;
	if (diffHours < 24) return `${diffHours}h ago`;
	if (diffDays < 7) return `${diffDays}d ago`;
	if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
	return `${Math.floor(diffDays / 30)}mo ago`;
}
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
	 * Chat history item container
	 *
	 * Layout: Flexbox with conversation info (left) and actions (right)
	 * WHY fixed height (48px):
	 * - Predictable layout: Virtual scrolling needs consistent item heights
	 * - Scanning efficiency: Uniform height improves readability
	 * - Touch-friendly: Meets minimum 44px touch target
	 */
	.chat-history-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
		height: 48px;
		padding: 0.5rem 0.75rem;
		cursor: pointer;
		border-radius: 0.5rem;
		transition: all 0.2s ease;
	}

	/**
	 * Hover state
	 *
	 * WHY subtle gray background:
	 * - Affordance: Signals item is clickable
	 * - Not too strong: Doesn't overwhelm active state
	 */
	.chat-history-item:hover {
		background-color: #f3f4f6; /* Gray 100 */
	}

	/**
	 * Active/selected state
	 *
	 * WHY blue background instead of border:
	 * - Prominence: Clearly indicates current conversation
	 * - Consistency: Matches common sidebar patterns (Slack, Discord)
	 */
	.chat-history-item.active {
		background-color: #eff6ff; /* Blue 50 */
		border-left: 3px solid #3b82f6; /* Blue 500 accent */
	}

	/**
	 * Focus state (keyboard navigation)
	 *
	 * Accessibility: Visible focus indicator
	 */
	.chat-history-item:focus {
		outline: 2px solid #3b82f6;
		outline-offset: -2px;
	}

	/**
	 * Conversation info section (left)
	 *
	 * WHY flex-direction column:
	 * - Vertical stacking: Title above metadata
	 * - Flex-grow: Takes available space (pushes actions to right)
	 */
	.conversation-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		flex: 1;
		min-width: 0; /* Allow text truncation */
	}

	/**
	 * Conversation title
	 *
	 * WHY text-overflow ellipsis:
	 * - Prevents layout break: Long titles don't overflow container
	 * - UX: User can see start of title (most important part)
	 * - Accessibility: Full title available via hover (title attribute)
	 */
	.title {
		font-size: 0.875rem;
		font-weight: 500;
		color: #111827; /* Gray 900 */
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	/**
	 * Active item title styling
	 *
	 * WHY blue color when active:
	 * - Emphasis: Reinforces selected state
	 * - Consistency: Matches blue accent border
	 */
	.active .title {
		color: #3b82f6; /* Blue 500 */
	}

	/**
	 * Metadata row (message count + timestamp)
	 *
	 * Layout: Horizontal with separator dot
	 */
	.metadata {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		font-size: 0.75rem;
		color: #6b7280; /* Gray 500 */
	}

	.separator {
		color: #d1d5db; /* Gray 300 */
	}

	/**
	 * Actions section (right)
	 *
	 * WHY opacity 0 by default, opacity 1 on hover:
	 * - Clean UI: Hides delete button until needed
	 * - Hover reveal: Progressive disclosure pattern
	 * - Prevents accidental clicks: User must deliberately hover
	 */
	.actions {
		display: flex;
		gap: 0.25rem;
		opacity: 0;
		transition: opacity 0.2s ease;
	}

	.chat-history-item:hover .actions,
	.chat-history-item:focus .actions {
		opacity: 1;
	}

	/**
	 * Delete button styling
	 *
	 * WHY larger padding and icon size:
	 * - Clickability: Easier to hit with mouse or touch
	 * - Accessibility: Meets 44x44px minimum touch target
	 * - Universal: Trash icon is recognizable
	 */
	.delete-button,
	.confirm-delete-button,
	.cancel-delete-button {
		padding: 0.5rem;
		background: none;
		border: none;
		border-radius: 0.375rem;
		color: #6b7280; /* Gray 500 */
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.delete-button:hover,
	.cancel-delete-button:hover {
		background-color: #e5e7eb; /* Gray 200 */
		color: #dc2626; /* Red 600 */
	}

	.confirm-delete-button {
		color: #16a34a; /* Green 600 */
	}

	.confirm-delete-button:hover {
		background-color: #dcfce7; /* Green 100 */
		color: #15803d; /* Green 700 */
	}
</style>
