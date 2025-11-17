/**
 * Messages store
 *
 * Purpose: Manage messages for current conversation and streaming state
 *
 * State management strategy:
 * - Writable store for message list
 * - Streaming state (isStreaming, streamingContent)
 * - Helper functions for adding messages, handling SSE events
 *
 * Usage:
 * import { messages, loadMessages, addUserMessage } from '$stores/messages';
 * await loadMessages(conversationId); // Load chat history
 * addUserMessage({ ... }); // Add user message
 * appendStreamingToken('Hello'); // Append token during streaming
 */

import { writable } from 'svelte/store';
import type { Message } from '$types';

/**
 * Messages store state
 *
 * Stores messages, streaming state, and error state
 *
 * WHY include streaming state in messages store:
 * - Cohesion: Streaming is tightly coupled to message display
 * - Single source of truth: Prevents sync issues between separate stores
 * - Atomic updates: Can update messages and streaming state together
 * - Simpler subscription: Components subscribe once, get both message list and streaming status
 *
 * WHY separate streamingContent from items array:
 * - Performance: Don't trigger array re-renders for every token (hundreds per response)
 * - Append efficiency: String concatenation is faster than array mutations
 * - Clear separation: Streaming (temporary) vs. persisted messages (permanent)
 * - Only add to items when complete: Prevents partial messages in history
 */
interface MessagesState {
	items: Message[];
	isLoading: boolean;
	error: string | null;

	// Streaming state
	isStreaming: boolean;
	streamingMessageId: number | null; // ID of message being streamed
	streamingContent: string; // Accumulated tokens during streaming
}

/**
 * Initial state for messages store
 */
const initialState: MessagesState = {
	items: [],
	isLoading: false,
	error: null,
	isStreaming: false,
	streamingMessageId: null,
	streamingContent: ''
};

/**
 * Writable messages store
 *
 * Core store for message list and streaming state management
 */
function createMessagesStore() {
	const { subscribe, set, update } = writable<MessagesState>(initialState);

	return {
		subscribe,

		/**
		 * Set loading state
		 *
		 * Called when fetching message history from API
		 */
		setLoading: (isLoading: boolean) => {
			update((state) => ({ ...state, isLoading }));
		},

		/**
		 * Set messages list
		 *
		 * Called after successful API fetch
		 *
		 * @param messages - Array of messages from API
		 */
		setMessages: (messages: Message[]) => {
			set({ ...initialState, items: messages });
		},

		/**
		 * Add message to list
		 *
		 * Called after sending user message or receiving assistant message
		 *
		 * @param message - Message object
		 */
		addMessage: (message: Message) => {
			update((state) => ({
				...state,
				items: [...state.items, message] // Append to end
			}));
		},

		/**
		 * Update existing message
		 *
		 * Called when adding reaction or updating message metadata
		 *
		 * WHY use map() for single message update:
		 * - Immutability: Creates new array, preserves original state
		 * - Svelte reactivity: New array reference triggers subscriber updates
		 * - Simplicity: Single pattern for all updates (no special-case logic)
		 * - Performance acceptable: Array traversal is fast for typical chat history (<1000 messages)
		 *
		 * WHY support Partial<Message> updates:
		 * - Reaction updates: Only change reaction field, preserve content/timestamps
		 * - Metadata updates: Can update individual fields without full message object
		 * - Type safety: TypeScript ensures only valid Message fields are passed
		 * - Prevents bugs: Can't accidentally overwrite unrelated fields with undefined
		 *
		 * Example use cases:
		 * - updateMessage(42, { reaction: 'thumbs_up' }) // Add reaction
		 * - updateMessage(42, { reaction: null }) // Remove reaction
		 *
		 * @param messageId - ID of message to update
		 * @param updates - Partial message data to merge
		 */
		updateMessage: (messageId: number, updates: Partial<Message>) => {
			update((state) => ({
				...state,
				items: state.items.map((m) => (m.id === messageId ? { ...m, ...updates } : m))
			}));
		},

		/**
		 * Start streaming
		 *
		 * Called when SSE stream begins
		 *
		 * @param messageId - ID of assistant message being streamed
		 */
		startStreaming: (messageId: number) => {
			update((state) => ({
				...state,
				isStreaming: true,
				streamingMessageId: messageId,
				streamingContent: ''
			}));
		},

		/**
		 * Append streaming token
		 *
		 * Called for each SSE token event
		 *
		 * @param token - Token text to append
		 */
		appendStreamingToken: (token: string) => {
			update((state) => ({
				...state,
				streamingContent: state.streamingContent + token
			}));
		},

		/**
		 * Finish streaming
		 *
		 * Called when SSE complete event received
		 *
		 * Creates final message with accumulated content
		 *
		 * WHY append messageData instead of creating from streamingContent:
		 * - Backend provides authoritative message object (includes ID, timestamps, metadata)
		 * - Prevents client/server state divergence
		 * - messageData.content may differ from streamingContent (backend post-processing)
		 * - Ensures database ID is correct for future updates (reactions, regenerate)
		 *
		 * WHY clear streamingContent after adding to items:
		 * - Free memory: Long responses can be several KB
		 * - Prevent display bugs: Ensures next stream starts clean
		 * - State hygiene: Explicit cleanup prevents stale state issues
		 *
		 * @param messageData - Complete message data from SSE complete event
		 */
		finishStreaming: (messageData: Message) => {
			update((state) => ({
				...state,
				isStreaming: false,
				streamingMessageId: null,
				streamingContent: '',
				items: [...state.items, messageData] // Add completed message
			}));
		},

		/**
		 * Cancel streaming
		 *
		 * Called when user cancels stream or error occurs
		 */
		cancelStreaming: () => {
			update((state) => ({
				...state,
				isStreaming: false,
				streamingMessageId: null,
				streamingContent: ''
			}));
		},

		/**
		 * Set error state
		 *
		 * Called when API request fails or streaming error occurs
		 *
		 * @param error - Error message
		 */
		setError: (error: string) => {
			update((state) => ({
				...state,
				error,
				isLoading: false,
				isStreaming: false
			}));
		},

		/**
		 * Clear error state
		 *
		 * Called to dismiss error message
		 */
		clearError: () => {
			update((state) => ({ ...state, error: null }));
		},

		/**
		 * Reset store to initial state
		 *
		 * Called when switching conversations
		 */
		reset: () => {
			set(initialState);
		}
	};
}

/**
 * Messages store instance
 *
 * Use this store in components for message list and streaming state
 */
export const messages = createMessagesStore();
