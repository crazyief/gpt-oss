/**
 * Conversations store
 *
 * Purpose: Manage conversation list and current conversation state
 *
 * State management strategy:
 * - Writable store for conversation list
 * - Separate store for current conversation ID
 * - Derived stores for filtering (search) and sorting
 * - Helper functions for CRUD operations
 *
 * Usage:
 * import { conversations, currentConversationId, loadConversations } from '$stores/conversations';
 * await loadConversations(projectId); // Fetch from API
 * currentConversationId.set(123); // Switch conversation
 */

import { writable, derived, type Readable } from 'svelte/store';
import type { Conversation } from '$types';

/**
 * Conversations store state
 *
 * Stores array of conversations, loading state, and search query
 */
interface ConversationsState {
	items: Conversation[];
	isLoading: boolean;
	error: string | null;
	searchQuery: string; // For real-time filtering
}

/**
 * Initial state for conversations store
 */
const initialState: ConversationsState = {
	items: [],
	isLoading: false,
	error: null,
	searchQuery: ''
};

/**
 * Writable conversations store
 *
 * Core store for conversation list state management
 */
function createConversationsStore() {
	const { subscribe, set, update } = writable<ConversationsState>(initialState);

	return {
		subscribe,

		/**
		 * Set loading state
		 *
		 * Called when starting API request
		 */
		setLoading: (isLoading: boolean) => {
			update((state) => ({ ...state, isLoading }));
		},

		/**
		 * Set conversations list
		 *
		 * Called after successful API fetch
		 *
		 * @param conversations - Array of conversations from API
		 */
		setConversations: (conversations: Conversation[]) => {
			set({ ...initialState, items: conversations });
		},

		/**
		 * Add new conversation to list
		 *
		 * Called after successful conversation creation
		 *
		 * @param conversation - Newly created conversation
		 */
		addConversation: (conversation: Conversation) => {
			update((state) => ({
				...state,
				items: [conversation, ...state.items] // Prepend new conversation
			}));
		},

		/**
		 * Update existing conversation
		 *
		 * Called after successful conversation update (e.g., title change)
		 *
		 * @param conversationId - ID of conversation to update
		 * @param updates - Partial conversation data to merge
		 */
		updateConversation: (conversationId: number, updates: Partial<Conversation>) => {
			update((state) => ({
				...state,
				items: state.items.map((c) => (c.id === conversationId ? { ...c, ...updates } : c))
			}));
		},

		/**
		 * Remove conversation from list
		 *
		 * Called after successful conversation deletion
		 *
		 * @param conversationId - ID of conversation to remove
		 */
		removeConversation: (conversationId: number) => {
			update((state) => ({
				...state,
				items: state.items.filter((c) => c.id !== conversationId)
			}));
		},

		/**
		 * Set search query for filtering
		 *
		 * Called when user types in search input
		 *
		 * @param query - Search query string
		 */
		setSearchQuery: (query: string) => {
			update((state) => ({ ...state, searchQuery: query }));
		},

		/**
		 * Set error state
		 *
		 * Called when API request fails
		 *
		 * @param error - Error message
		 */
		setError: (error: string) => {
			update((state) => ({ ...state, error, isLoading: false }));
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
		 * Called when switching projects or logging out
		 */
		reset: () => {
			set(initialState);
		}
	};
}

/**
 * Conversations store instance
 *
 * Use this store in components for conversation list state
 */
export const conversations = createConversationsStore();

/**
 * Current conversation ID store
 *
 * Tracks which conversation is currently active in chat interface
 *
 * WHY separate store instead of property in conversations state:
 * - Independent subscription: Components can subscribe to current ID without re-rendering on list changes
 * - Performance: Changing active conversation doesn't trigger list re-renders
 * - Simplicity: Easier to track "active item" separately from "list of items"
 * - URL sync: Can sync with route params without coupling to list state
 *
 * WHY number | null instead of number | undefined:
 * - null is explicit "no selection" (user on project home, not in conversation)
 * - undefined suggests uninitialized state (bug)
 * - JSON serialization: null serializes, undefined doesn't (future: persist to localStorage)
 *
 * Usage:
 * import { currentConversationId } from '$stores/conversations';
 * currentConversationId.set(123); // Switch to conversation 123
 * if ($currentConversationId === 123) { ... }
 */
export const currentConversationId = writable<number | null>(null);

/**
 * Derived store: filtered conversations
 *
 * Returns conversations filtered by search query (case-insensitive title match)
 *
 * WHY search filtering in derived store instead of component:
 * - Reusability: Multiple components can consume filtered data without duplicating logic
 * - Performance: Svelte caches result until $conversations changes (memoization)
 * - Testability: Easier to unit test store logic than component-embedded filtering
 * - Separation: Keeps components focused on rendering, not filtering logic
 *
 * WHY case-insensitive substring match:
 * - Better UX: User doesn't need to match exact casing ("api" matches "API Project")
 * - Substring: Partial matches work ("proj" matches "My Project")
 * - Trade-off: Simple but not fuzzy search (future enhancement: use Fuse.js)
 *
 * WHY toLowerCase() on both query and title:
 * - Normalize casing for comparison (case-insensitive)
 * - Alternative considered: regex with 'i' flag, but includes() is faster for simple substring match
 *
 * Usage:
 * import { filteredConversations } from '$stores/conversations';
 * {#each $filteredConversations as conversation}...{/each}
 */
export const filteredConversations: Readable<Conversation[]> = derived(
	conversations,
	($conversations) => {
		const query = $conversations.searchQuery.toLowerCase();

		// If no search query, return all conversations (no filtering overhead)
		if (!query) {
			return $conversations.items;
		}

		// Filter by title (case-insensitive substring match)
		return $conversations.items.filter((c) => c.title.toLowerCase().includes(query));
	}
);

/**
 * Derived store: sorted and filtered conversations
 *
 * Returns conversations sorted by last_message_at (newest first), then filtered by search
 *
 * WHY sort by last_message_at instead of created_at:
 * - Recent activity is more relevant than creation date
 * - Mimics familiar chat app UX (Slack, Discord, WhatsApp)
 * - Active conversations "bubble up" to top automatically
 * - Users can quickly find their recent work
 *
 * WHY handle null last_message_at explicitly:
 * - New conversations have no messages yet (last_message_at = null)
 * - Null comparisons fail silently in JavaScript, causing unpredictable sort order
 * - Explicit handling ensures empty conversations always go to bottom
 * - Prevents NaN from new Date(null).getTime() breaking sort
 *
 * WHY derive from filteredConversations instead of conversations:
 * - Compose transformations: filter → sort (pipeline pattern)
 * - Performance: Only sort filtered results, not entire list
 * - Svelte optimizes: Only recalculates when filteredConversations changes
 *
 * WHY spread operator [...$filteredConversations]:
 * - Array.sort() mutates in place, must create new array for immutability
 * - Prevents side effects in components subscribed to filteredConversations
 *
 * Usage:
 * import { sortedFilteredConversations } from '$stores/conversations';
 * {#each $sortedFilteredConversations as conversation}...{/each}
 */
export const sortedFilteredConversations: Readable<Conversation[]> = derived(
	filteredConversations,
	($filteredConversations) =>
		[...$filteredConversations].sort((a, b) => {
			// Conversations with no messages go to bottom
			if (!a.last_message_at && !b.last_message_at) return 0;
			if (!a.last_message_at) return 1;
			if (!b.last_message_at) return -1;

			// Sort by last_message_at descending (newest first)
			return new Date(b.last_message_at).getTime() - new Date(a.last_message_at).getTime();
		})
);
