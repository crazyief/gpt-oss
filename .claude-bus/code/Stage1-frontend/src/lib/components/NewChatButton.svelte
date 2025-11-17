<script lang="ts">
/**
 * NewChatButton component
 *
 * Purpose: Button to create new conversation
 *
 * Features:
 * - Creates new conversation in current project
 * - Switches to new conversation immediately
 * - Loading state during API call
 * - Error handling with user feedback
 *
 * Design decisions:
 * - Prominent placement: Top of sidebar (easy to find)
 * - Icon + text: Clear affordance for action
 * - Optimistic UI: Immediately show new conversation, then sync with backend
 *
 * WHY create conversation immediately vs. on first message:
 * - User intent: Clicking "New Chat" expresses intent to start conversation
 * - Navigation: Need conversation ID for routing (/chat/[id])
 * - Consistency: Matches ChatGPT, Claude, etc. UX patterns
 */

import { createEventDispatcher } from 'svelte';
import { conversations, currentConversationId } from '$lib/stores/conversations';
import { messages } from '$lib/stores/messages';
import { createConversation } from '$lib/services/api-client';

// Component state
let isLoading = false;
let error: string | null = null;

// Event dispatcher for parent component notifications
const dispatch = createEventDispatcher<{
	created: { conversationId: number };
}>();

/**
 * Create new conversation
 *
 * Flow:
 * 1. Call API to create conversation
 * 2. Add conversation to store
 * 3. Switch to new conversation
 * 4. Clear message history (fresh start)
 * 5. Notify parent component
 *
 * WHY optimistic UI not used here:
 * - Need ID: Must wait for backend to generate conversation ID
 * - Simple operation: Creation is fast (<500ms), loading state acceptable
 * - Error handling: Easier to handle errors before updating store
 *
 * Future enhancement: Optimistic UI with client-generated UUID, then sync with backend
 */
async function handleNewChat() {
	try {
		isLoading = true;
		error = null;

		// Create conversation via API (uses mock data for now)
		const newConversation = await createConversation({
			title: 'New Conversation'
			// project_id will be set from context in future (Stage 2+)
		});

		// Add to conversations store
		conversations.addConversation(newConversation);

		// Switch to new conversation
		currentConversationId.set(newConversation.id);

		// Clear message history for fresh start
		messages.reset();

		// Notify parent (e.g., for analytics, routing)
		dispatch('created', { conversationId: newConversation.id });
	} catch (err) {
		error = err instanceof Error ? err.message : 'Failed to create conversation';
		console.error('Failed to create conversation:', err);
	} finally {
		isLoading = false;
	}
}
</script>

<button
	type="button"
	on:click={handleNewChat}
	disabled={isLoading}
	class="new-chat-button"
	aria-label="Create new conversation"
>
	<!-- Plus icon (universal symbol for "create new") -->
	<svg
		class="icon"
		width="20"
		height="20"
		viewBox="0 0 20 20"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		aria-hidden="true"
	>
		<path
			d="M10 4v12M4 10h12"
			stroke="currentColor"
			stroke-width="2"
			stroke-linecap="round"
		/>
	</svg>

	<!-- Button text (loading state shows spinner) -->
	<span class="text">
		{#if isLoading}
			Creating...
		{:else}
			New Chat
		{/if}
	</span>
</button>

<!-- Error message (shown below button if creation fails) -->
{#if error}
	<div class="error-message" role="alert">
		{error}
	</div>
{/if}

<style>
	/**
	 * New chat button
	 *
	 * Style: Full-width button with icon + text
	 * WHY full-width instead of icon-only:
	 * - Discoverability: Text label makes action obvious
	 * - Mobile-friendly: Larger touch target
	 * - Accessibility: Screen readers announce "New Chat" clearly
	 *
	 * WHY blue gradient background:
	 * - Primary action: Most common user action in sidebar
	 * - Visual hierarchy: Stands out from conversation list
	 * - Brand consistency: Matches ChatGPT-inspired design system
	 */
	.new-chat-button {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.75rem 1rem;
		margin: 0.75rem;
		background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); /* Blue gradient */
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	/**
	 * Button hover state
	 *
	 * WHY darken on hover instead of lighten:
	 * - Affordance: Signals button is interactive
	 * - Common pattern: Most UI libraries darken primary buttons on hover
	 */
	.new-chat-button:hover:not(:disabled) {
		background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
		transform: translateY(-1px); /* Subtle lift effect */
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}

	/**
	 * Button active state (pressed)
	 *
	 * WHY scale down instead of just background change:
	 * - Tactile feedback: Mimics physical button press
	 * - Modern UX: Apple, Material Design use this pattern
	 */
	.new-chat-button:active:not(:disabled) {
		transform: translateY(0) scale(0.98);
	}

	/**
	 * Button disabled state
	 *
	 * WHY reduce opacity instead of gray background:
	 * - Visual consistency: Keep brand color visible
	 * - Loading indication: User sees button is still "New Chat" but temporarily disabled
	 */
	.new-chat-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	/**
	 * Icon styling
	 *
	 * WHY 20px icon size:
	 * - Balance: Not too small (hard to see) or too large (overwhelming)
	 * - Alignment: Matches text line height for vertical centering
	 */
	.icon {
		flex-shrink: 0; /* Prevent icon from shrinking if text wraps */
	}

	/**
	 * Text styling
	 *
	 * WHY separate span for text:
	 * - Conditional rendering: Can show "Creating..." during loading
	 * - Future i18n: Easy to replace with translation key
	 */
	.text {
		white-space: nowrap; /* Prevent text from wrapping */
	}

	/**
	 * Error message styling
	 *
	 * WHY show error below button instead of toast notification:
	 * - Context: Error is directly related to this button action
	 * - Persistence: User can read error without time pressure (toasts auto-dismiss)
	 * - Simplicity: No need for toast/notification system in Stage 1
	 */
	.error-message {
		margin: 0 0.75rem;
		padding: 0.5rem;
		background-color: #fef2f2; /* Red 50 */
		color: #dc2626; /* Red 600 */
		border-radius: 0.375rem;
		font-size: 0.75rem;
		border: 1px solid #fecaca; /* Red 200 */
	}
</style>
