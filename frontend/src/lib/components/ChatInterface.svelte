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
import { currentConversationId, conversations } from '$lib/stores/conversations';
import { messages } from '$lib/stores/messages';
import MessageList from './MessageList.svelte';
import MessageInput from './MessageInput.svelte';
import { SSEClient } from '$lib/services/sse-client';
import { fetchMessages, updateConversation, fetchProjects, fetchConversations } from '$lib/services/api-client';
import { currentProjectId } from '$lib/stores/projects';
import type { Project } from '$lib/types';

// Component state
let sseClient: SSEClient;
let loadingMessages = false;
let conversationTitle = 'New Conversation';
let isEditingTitle = false;
let editTitleValue = '';

// Project management
let projects: Project[] = [];
let conversationProjectId: number | null = null;
let isChangingProject = false;

// ============================================================================
// CRITICAL PROJECT CONSTANT: SAFE ZONE TOKEN LIMIT
// ============================================================================
//
// **SAFE_ZONE_TOKEN = 22,800 tokens**
//
// This is the ABSOLUTE MAXIMUM token limit for the entire GPT-OSS project.
// This number MUST be respected across ALL features:
// - ✅ Chat conversations (current feature)
// - ✅ RAG document retrieval (Stage 2+)
// - ✅ Knowledge graph queries (Stage 4+)
// - ✅ Multi-document analysis (Stage 5+)
//
// WHY 22,800 tokens specifically:
// ────────────────────────────────────────────────────────────────────────────
// Based on extensive testing documented in:
// backend/tests/MODEL_COMPARISON_AND_RECOMMENDATIONS.md
//
// Test Methodology:
// - Model: Magistral-Small-2506-Q6_K_L @ 32k context window
// - Test data: 1,500 items with random 8-character IDs
// - Result: 1,500 items × 15.2 tokens/item = 22,800 tokens
// - Behavior: 100% accuracy up to 22,800 tokens, then HARD CLIFF FAILURE
//
// Native vs Usable Context:
// - Native context window: 32,768 tokens (architectural limit)
// - Usable context (tested): 22,800 tokens (hard cliff failure point)
// - Difference: System overhead, prompt formatting, safety margins
//
// Failure Pattern (CRITICAL):
// - Below 22,800 tokens: 100% accuracy, perfect reliability
// - At 22,800 tokens: Hard cliff - model fails completely
// - Above 22,800 tokens: Context overflow, unpredictable behavior
//
// User Directive:
// "22,800 will be the key number we gonna use in this very important project.
// For RAG or Chat, will always not exceed 22,800. We can give it a name,
// such as 'Safe Zone Number'."
//
// ⚠️ DO NOT EXCEED THIS LIMIT - IT IS NOT NEGOTIABLE ⚠️
// ============================================================================

/**
 * SAFE ZONE TOKEN - Critical project-wide constant
 *
 * This is the maximum safe token limit for the entire GPT-OSS LightRAG system.
 * Tested capacity: 1,500 items = 22,800 tokens (hard cliff failure point)
 *
 * IMPORTANT: All features (Chat, RAG, Knowledge Graph) must respect this limit.
 */
const SAFE_ZONE_TOKEN = 22800; // Maximum tested: 1,500 items @ 32k context

/**
 * Legacy alias for backward compatibility
 * @deprecated Use SAFE_ZONE_TOKEN instead
 */
const MAX_CONTEXT_TOKENS = SAFE_ZONE_TOKEN;

/**
 * Calculate total tokens used in conversation
 *
 * WHY track total tokens:
 * - Context awareness: User can see how much context is being used
 * - Performance indicator: High token count = slower responses
 * - Context limit warning: Approaching max context needs attention
 *
 * @returns Total token count across all messages
 */
$: totalTokens = $messages.items.reduce((sum, msg) => sum + (msg.token_count || 0), 0);

/**
 * Calculate percentage of max context used
 */
$: contextPercentage = (totalTokens / MAX_CONTEXT_TOKENS) * 100;

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

		// Load conversation metadata from store
		const conversation = $conversations.items.find((c) => c.id === conversationId);
		if (conversation) {
			conversationTitle = conversation.title;
			conversationProjectId = conversation.project_id;
		}
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
		// Check if this is the first message (auto-generate title)
		// WHY check conversationTitle === 'New Conversation':
		// - Indicates default title, user hasn't sent any messages yet
		// - Auto-title improves UX (no manual rename needed)
		// - ChatGPT pattern: first message becomes title
		if (conversationTitle === 'New Conversation' && $messages.items.length === 0) {
			// Generate title from first 50 characters of message
			const autoTitle = message.length > 50 ? message.substring(0, 50) + '...' : message;

			try {
				await updateConversation($currentConversationId, { title: autoTitle });
				conversationTitle = autoTitle;

				// Update conversation in store
				conversations.updateConversation($currentConversationId, { title: autoTitle });
			} catch (err) {
				console.error('Failed to auto-generate title:', err);
				// Non-fatal: Continue with message send even if title update fails
			}
		}

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
 * Start editing conversation title
 *
 * WHY inline editing instead of modal:
 * - Less disruptive: User stays in context
 * - Faster: Click to edit, escape to cancel
 * - Common pattern: Notion, Slack use inline editing
 */
function startEditTitle() {
	editTitleValue = conversationTitle;
	isEditingTitle = true;
}

/**
 * Save edited conversation title
 *
 * WHY async:
 * - Need to call API to persist changes
 * - Update both local state and store
 * - Handle errors gracefully
 */
async function saveEditTitle() {
	if (!$currentConversationId || !editTitleValue.trim()) {
		isEditingTitle = false;
		return;
	}

	const newTitle = editTitleValue.trim();

	try {
		await updateConversation($currentConversationId, { title: newTitle });
		conversationTitle = newTitle;

		// Update conversation in store (updates sidebar)
		conversations.updateConversation($currentConversationId, { title: newTitle });

		isEditingTitle = false;
	} catch (err) {
		console.error('Failed to update title:', err);
		// Revert to original title on error
		editTitleValue = conversationTitle;
		isEditingTitle = false;
	}
}

/**
 * Cancel title editing
 */
function cancelEditTitle() {
	isEditingTitle = false;
	editTitleValue = '';
}

/**
 * Handle keydown in title input
 *
 * WHY keyboard shortcuts:
 * - Enter: Save (intuitive, matches form behavior)
 * - Escape: Cancel (common pattern)
 * - Tab: Save and move focus (accessibility)
 */
function handleTitleKeydown(event: KeyboardEvent) {
	if (event.key === 'Enter') {
		event.preventDefault();
		saveEditTitle();
	} else if (event.key === 'Escape') {
		event.preventDefault();
		cancelEditTitle();
	}
}

/**
 * Load projects on mount
 *
 * WHY load projects here instead of using global store:
 * - Encapsulation: Chat interface manages its own project selector
 * - Freshness: Always get latest project list when opening chat
 */
async function loadProjectsList() {
	try {
		const response = await fetchProjects();
		projects = response.projects;
	} catch (err) {
		console.error('Failed to load projects:', err);
	}
}

/**
 * Change conversation's project
 *
 * WHY allow changing project:
 * - Organization: User can move conversations to correct project
 * - Mistake correction: Fix wrong project selection
 * - Reorganization: User can reorganize conversations later
 *
 * WHY reload conversations after change:
 * - Fresh data: Sidebar shows updated project assignment
 * - Filter consistency: If viewing filtered project list, conversation may move out of view
 * - Project counts: Conversation counts update for affected projects
 *
 * @param event - Select change event
 */
async function handleProjectChange(event: Event) {
	if (!$currentConversationId) return;

	const target = event.target as HTMLSelectElement;
	const newProjectId = parseInt(target.value, 10);

	try {
		isChangingProject = true;

		// Update conversation project via API
		await updateConversation($currentConversationId, { project_id: newProjectId });

		// Update local state
		conversationProjectId = newProjectId;

		// Reload conversation list for current project filter
		// This ensures sidebar shows updated assignments and counts
		const filterProjectId = $currentProjectId === null ? undefined : $currentProjectId;
		const response = await fetchConversations(filterProjectId);
		conversations.setConversations(response.conversations);

		// Reload projects to update conversation counts
		await loadProjectsList();

		console.log(`Conversation ${$currentConversationId} moved to project ${newProjectId}`);
	} catch (err) {
		console.error('Failed to change project:', err);
		// Revert select to original value
		target.value = conversationProjectId?.toString() || '';

		// Show error to user
		alert(`Failed to change project: ${err instanceof Error ? err.message : 'Unknown error'}`);
	} finally {
		isChangingProject = false;
	}
}

/**
 * Initialize SSE client on mount
 */
onMount(async () => {
	sseClient = new SSEClient();

	// Load projects for project selector
	await loadProjectsList();
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
			{#if isEditingTitle}
				<!-- Title input (edit mode) -->
				<input
					type="text"
					bind:value={editTitleValue}
					on:keydown={handleTitleKeydown}
					on:blur={saveEditTitle}
					class="conversation-title-input"
					placeholder="Enter conversation title"
					autofocus
				/>
			{:else}
				<!-- Title display (click to edit) -->
				<h1
					class="conversation-title"
					on:click={startEditTitle}
					on:keydown={(e) => e.key === 'Enter' && startEditTitle()}
					role="button"
					tabindex="0"
					title="Click to edit title"
				>
					{conversationTitle}
					<svg class="edit-icon" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M11.5 2.5l2 2L6 12H4v-2l7.5-7.5z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
					</svg>
				</h1>
			{/if}

			{#if $currentConversationId}
				<p class="conversation-id">ID: {$currentConversationId}</p>
			{/if}

			<!-- Project selector -->
			{#if projects.length > 0 && conversationProjectId !== null}
				<div class="project-selector-wrapper">
					<label for="conversation-project" class="project-label">
						<svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M2 3h10M2 7h10M2 11h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
						</svg>
						Project:
					</label>
					<select
						id="conversation-project"
						value={conversationProjectId}
						on:change={handleProjectChange}
						disabled={isChangingProject}
						class="project-select"
						aria-label="Change conversation project"
					>
						{#each projects as project (project.id)}
							<option value={project.id}>
								{project.name}
							</option>
						{/each}
					</select>
				</div>
			{/if}

			<!-- Token usage indicator -->
			{#if totalTokens > 0}
				<div class="token-usage" class:warning={contextPercentage > 80} class:critical={contextPercentage > 95}>
					<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M8 2v12M4 6l4-4 4 4M4 10l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
					<span class="token-count">{totalTokens.toLocaleString()} / {MAX_CONTEXT_TOKENS.toLocaleString()}</span>
					<span class="token-percentage">({contextPercentage.toFixed(1)}%)</span>
				</div>
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

	/**
	 * Conversation title (click to edit)
	 *
	 * WHY clickable:
	 * - Inline editing: Click to edit without modal
	 * - Edit icon appears on hover (progressive disclosure)
	 */
	.conversation-title {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: #111827; /* Gray 900 */
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.25rem 0.5rem;
		border-radius: 0.375rem;
		transition: background-color 0.2s ease;
	}

	.conversation-title:hover {
		background-color: #f3f4f6; /* Gray 100 */
	}

	/**
	 * Edit icon (show on hover)
	 *
	 * WHY hidden by default:
	 * - Clean UI: Don't clutter header
	 * - Progressive disclosure: Appears when needed
	 */
	.edit-icon {
		opacity: 0;
		transition: opacity 0.2s ease;
		color: #9ca3af; /* Gray 400 */
	}

	.conversation-title:hover .edit-icon {
		opacity: 1;
	}

	/**
	 * Title input (edit mode)
	 *
	 * WHY same size as title:
	 * - Visual consistency: No layout shift when switching
	 * - User expectation: Input looks like it replaced title
	 */
	.conversation-title-input {
		margin: 0;
		padding: 0.25rem 0.5rem;
		font-size: 1.25rem;
		font-weight: 600;
		color: #111827; /* Gray 900 */
		border: 2px solid #3b82f6; /* Blue 500 */
		border-radius: 0.375rem;
		background-color: #ffffff;
		outline: none;
		width: 100%;
		max-width: 500px;
	}

	.conversation-id {
		margin: 0.25rem 0 0 0;
		font-size: 0.75rem;
		color: #6b7280; /* Gray 500 */
	}

	/**
	 * Project selector
	 *
	 * WHY allow changing project in chat header:
	 * - Convenience: User can reorganize conversations without leaving chat
	 * - Contextual: Shows which project this conversation belongs to
	 * - Immediate feedback: Can see and change project right away
	 */
	.project-selector-wrapper {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 0.5rem;
	}

	.project-label {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		font-size: 0.75rem;
		font-weight: 500;
		color: #6b7280; /* Gray 500 */
	}

	.project-label svg {
		flex-shrink: 0;
	}

	.project-select {
		padding: 0.25rem 0.5rem;
		font-size: 0.75rem;
		border: 1px solid #e5e7eb; /* Gray 200 */
		border-radius: 0.375rem;
		background-color: #ffffff;
		color: #111827; /* Gray 900 */
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.project-select:hover:not(:disabled) {
		border-color: #d1d5db; /* Gray 300 */
		background-color: #f9fafb; /* Gray 50 */
	}

	.project-select:focus {
		outline: none;
		border-color: #3b82f6; /* Blue 500 */
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	.project-select:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/**
	 * Token usage indicator
	 *
	 * WHY show token count:
	 * - Context awareness: User knows how much context is used
	 * - Performance: High token count = slower inference
	 * - Warning system: Color-coded thresholds
	 *
	 * Color thresholds:
	 * - Normal (< 80%): Blue/gray (informational)
	 * - Warning (80-95%): Orange (caution)
	 * - Critical (> 95%): Red (approaching limit)
	 */
	.token-usage {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		margin-top: 0.5rem;
		padding: 0.375rem 0.625rem;
		background-color: #eff6ff; /* Blue 50 */
		color: #3b82f6; /* Blue 500 */
		border: 1px solid #dbeafe; /* Blue 100 */
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 500;
		width: fit-content;
	}

	.token-usage svg {
		flex-shrink: 0;
	}

	.token-count {
		font-weight: 600;
	}

	.token-percentage {
		color: #60a5fa; /* Blue 400 */
		font-weight: 400;
	}

	/**
	 * Warning state (80-95% of context used)
	 *
	 * WHY orange color:
	 * - Caution: Approaching context limit
	 * - Visibility: Stands out from normal blue
	 * - Not critical yet: Can still continue conversation
	 */
	.token-usage.warning {
		background-color: #fff7ed; /* Orange 50 */
		color: #f97316; /* Orange 500 */
		border-color: #fed7aa; /* Orange 200 */
	}

	.token-usage.warning .token-percentage {
		color: #fb923c; /* Orange 400 */
	}

	/**
	 * Critical state (> 95% of context used)
	 *
	 * WHY red color:
	 * - Urgent: Very close to context limit
	 * - Action needed: User should start new conversation
	 * - Warning: Next response might be truncated
	 */
	.token-usage.critical {
		background-color: #fef2f2; /* Red 50 */
		color: #dc2626; /* Red 600 */
		border-color: #fecaca; /* Red 200 */
	}

	.token-usage.critical .token-percentage {
		color: #ef4444; /* Red 500 */
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
