/**
 * Sidebar store
 *
 * Purpose: Manage sidebar visibility state
 *
 * State management strategy:
 * - Simple writable store for isOpen boolean
 * - Helper functions for toggle, open, close
 * - Persists state to localStorage for user preference
 *
 * Usage:
 * import { sidebarOpen, toggleSidebar } from '$stores/sidebar';
 * toggleSidebar(); // Toggle sidebar
 * sidebarOpen.set(true); // Open sidebar
 * {#if $sidebarOpen}...{/if} // Conditional rendering
 */

import { writable } from 'svelte/store';

// Browser detection (SvelteKit-compatible)
const browser = typeof window !== 'undefined';

/**
 * Local storage key for sidebar preference
 *
 * Used to persist sidebar state across sessions
 */
const SIDEBAR_STORAGE_KEY = 'gpt-oss-sidebar-open';

/**
 * Load sidebar state from localStorage
 *
 * Returns true if sidebar was open, false if closed, true by default
 *
 * Note: Only runs in browser (not during SSR)
 */
function loadSidebarState(): boolean {
	if (!browser) return true; // Default open for SSR

	const stored = localStorage.getItem(SIDEBAR_STORAGE_KEY);
	return stored === null ? true : stored === 'true';
}

/**
 * Save sidebar state to localStorage
 *
 * Persists user preference across sessions
 *
 * @param isOpen - Whether sidebar is open
 */
function saveSidebarState(isOpen: boolean): void {
	if (!browser) return; // Skip during SSR

	localStorage.setItem(SIDEBAR_STORAGE_KEY, String(isOpen));
}

/**
 * Sidebar open store
 *
 * Writable store with localStorage persistence
 */
function createSidebarStore() {
	const { subscribe, set, update } = writable<boolean>(loadSidebarState());

	return {
		subscribe,

		/**
		 * Set sidebar state
		 *
		 * @param isOpen - Whether sidebar should be open
		 */
		set: (isOpen: boolean) => {
			set(isOpen);
			saveSidebarState(isOpen);
		},

		/**
		 * Open sidebar
		 *
		 * Sets state to true and persists to localStorage
		 */
		open: () => {
			set(true);
			saveSidebarState(true);
		},

		/**
		 * Close sidebar
		 *
		 * Sets state to false and persists to localStorage
		 */
		close: () => {
			set(false);
			saveSidebarState(false);
		},

		/**
		 * Toggle sidebar
		 *
		 * Flips current state and persists to localStorage
		 */
		toggle: () => {
			update((isOpen) => {
				const newState = !isOpen;
				saveSidebarState(newState);
				return newState;
			});
		}
	};
}

/**
 * Sidebar open store instance
 *
 * Use this store in components for sidebar visibility
 */
export const sidebarOpen = createSidebarStore();
