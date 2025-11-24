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
import ChatHeader from './ChatHeader.svelte';
import { SSEClient } from '$lib/services/sse-client';
import { projects as projectsApi, conversations as conversationsApi } from '$lib/services/api';
import { currentProjectId } from '$lib/stores/projects';
import { logger } from '$lib/utils/logger';
import type { Project } from '$lib/types';

// Component state
let sseClient: SSEClient;
let loadingMessages = false;
let conversationTitle = 'New Conversation';

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

		const messageList = await conversationsApi.getConversationMessages(conversationId);
		messages.setMessages(messageList);

		// Load conversation metadata from store
		const conversation = $conversations.items.find((c) => c.id === conversationId);
		if (conversation) {
			conversationTitle = conversation.title;
			conversationProjectId = conversation.project_id;
		}
	} catch (err) {
		logger.error('Failed to load messages', { conversationId, error: err });
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
 * 3. Update conversation metadata (message_count, last_message_at)
 * 4. Start SSE stream for assistant response
 * 5. SSE client handles token streaming
 *
 * WHY optimistic UI for user message:
 * - Instant feedback: User sees their message immediately
 * - Better UX: No waiting for backend to echo message
 * - Low risk: User message is simple, unlikely to fail
 *
 * WHY update conversation metadata here:
 * - Real-time updates: Conversation list shows accurate message count immediately
 * - Sorting: Conversation moves to top of list (sorted by last_message_at)
 * - User feedback: Visual confirmation that message was sent
 *
 * @param event - Custom event with message content
 */
async function handleSendMessage(event: CustomEvent<{ message: string }>) {
	if (!$currentConversationId) {
		logger.error('Cannot send message: No conversation selected');
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
				await conversationsApi.updateConversation($currentConversationId, { title: autoTitle });
				conversationTitle = autoTitle;

				// Update conversation in store
				conversations.updateConversation($currentConversationId, { title: autoTitle });
			} catch (err) {
				logger.warn('Failed to auto-generate conversation title', { error: err });
				// Non-fatal: Continue with message send even if title update fails
			}
		}

		// Add user message optimistically (assume success)
		const now = new Date().toISOString();
		const userMessage = {
			id: Date.now(), // Temporary ID (backend will provide real ID)
			conversation_id: $currentConversationId,
			role: 'user' as const,
			content: message,
			created_at: now,
			reaction: null,
			parent_message_id: null,
			token_count: message.split(/\s+/).length // Rough estimate
		};

		messages.addMessage(userMessage);

		// Update conversation metadata in store (real-time list update)
		// This makes the conversation:
		// 1. Move to top of list (sorted by last_message_at)
		// 2. Show accurate message count
		// 3. Show "Just now" timestamp
		const currentMessageCount = $messages.items.length; // Includes user message just added
		conversations.updateConversation($currentConversationId, {
			message_count: currentMessageCount,
			last_message_at: now,
			updated_at: now
		});

		// Start SSE stream for assistant response
		await sseClient.connect($currentConversationId, message);
	} catch (err) {
		logger.error('Failed to send message', { conversationId: $currentConversationId, error: err });
		messages.setError(err instanceof Error ? err.message : 'Failed to send message');
	}
}

/**
 * Handle stream cancellation
 */
function handleCancelStream() {
	sseClient.cancel();
}

/**
 * Handle save title event from ChatHeader
 */
async function handleSaveTitle(event: CustomEvent<{ title: string }>) {
	if (!$currentConversationId) return;

	const newTitle = event.detail.title;

	try {
		await conversationsApi.updateConversation($currentConversationId, { title: newTitle });
		conversationTitle = newTitle;

		// Update conversation in store (updates sidebar)
		conversations.updateConversation($currentConversationId, { title: newTitle });
	} catch (err) {
		logger.error('Failed to update conversation title', {
			conversationId: $currentConversationId,
			error: err
		});
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
		const response = await projectsApi.fetchProjects();
		projects = response.projects;
	} catch (err) {
		logger.error('Failed to load projects list', { error: err });
	}
}

/**
 * Handle change project event from ChatHeader
 */
async function handleChangeProject(event: CustomEvent<{ projectId: number }>) {
	if (!$currentConversationId) return;

	const newProjectId = event.detail.projectId;

	try {
		isChangingProject = true;

		// Update conversation project via API
		await conversationsApi.updateConversation($currentConversationId, { project_id: newProjectId });

		// Update local state
		conversationProjectId = newProjectId;

		// Reload conversation list for current project filter
		if ($currentProjectId !== null) {
			const convList = await conversationsApi.getConversations($currentProjectId);
			conversations.setConversations(convList);
		}

		// Reload projects to update conversation counts
		await loadProjectsList();

		logger.info('Conversation moved to new project', {
			conversationId: $currentConversationId,
			newProjectId
		});
	} catch (err) {
		logger.error('Failed to change conversation project', {
			conversationId: $currentConversationId,
			newProjectId,
			error: err
		});
		// Revert to original project
		conversationProjectId = conversationProjectId;

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
	<!-- Chat header component -->
	<ChatHeader
		bind:conversationTitle
		conversationId={$currentConversationId}
		{projects}
		{conversationProjectId}
		{isChangingProject}
		{totalTokens}
		maxTokens={MAX_CONTEXT_TOKENS}
		isStreaming={$messages.isStreaming}
		on:saveTitle={handleSaveTitle}
		on:changeProject={handleChangeProject}
		on:cancelStream={handleCancelStream}
	/>

	<!-- Message list (scrollable area) -->
	<MessageList />

	<!-- Message input (fixed at bottom) -->
	<MessageInput on:send={handleSendMessage} disabled={$messages.isStreaming} />
</div>

<style>
	/**
	 * Chat interface container - Modern gradient background
	 *
	 * Layout: Flexbox column (header + messages + input)
	 * WHY gradient background:
	 * - Visual depth: More interesting than flat white
	 * - Elegant: Subtle gradient doesn't distract
	 * - Modern: ChatGPT-inspired design pattern
	 */
	.chat-interface {
		display: flex;
		flex-direction: column;
		height: 100%;
		background: linear-gradient(180deg, #fafbfc 0%, #f5f7fa 50%, #eff2f7 100%);
		position: relative;
	}

	/* Subtle background pattern for texture */
	.chat-interface::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-image: radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.02) 0%, transparent 50%),
			radial-gradient(circle at 75% 75%, rgba(147, 51, 234, 0.02) 0%, transparent 50%);
		pointer-events: none;
		z-index: 0;
	}

	/* Ensure children are above background pattern */
	.chat-interface > :global(*) {
		position: relative;
		z-index: 1;
	}
</style>
