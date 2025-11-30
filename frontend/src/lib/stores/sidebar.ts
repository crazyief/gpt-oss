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

/**
 * Local storage key for sidebar preference
 *
 * Used to persist sidebar state across sessions
 */
const SIDEBAR_STORAGE_KEY = 'gpt-oss-sidebar-open';

/**
 * Check if running in browser at call time
 *
 * CRITICAL: This function checks at CALL TIME, not module load time.
 * This is necessary because module-level constants like `const browser = typeof window !== 'undefined'`
 * or even `import { browser } from '$app/environment'` can be evaluated during SSR
 * and cached incorrectly.
 *
 * @returns true if running in browser with localStorage available
 */
function isBrowser(): boolean {
	return typeof window !== 'undefined' && typeof localStorage !== 'undefined';
}

/**
 * Load sidebar state from localStorage
 *
 * Returns true if sidebar was open, false if closed, true by default
 *
 * Note: Only runs in browser (not during SSR)
 *
 * IMPORTANT: Default to TRUE (open) to ensure sidebar is visible on first load.
 * The ChatTab onMount will also call open() to guarantee visibility.
 */
function loadSidebarState(): boolean {
	if (!isBrowser()) return true; // Default open for SSR

	try {
		const stored = localStorage.getItem(SIDEBAR_STORAGE_KEY);
		// Default to open (true) if no stored value
		// Only return false if explicitly stored as 'false'
		if (stored === null) {
			return true;
		}
		return stored === 'true';
	} catch {
		// If localStorage is unavailable or corrupted, default to open
		return true;
	}
}

/**
 * Save sidebar state to localStorage
 *
 * Persists user preference across sessions
 *
 * @param isOpen - Whether sidebar is open
 */
function saveSidebarState(isOpen: boolean): void {
	if (!isBrowser()) return; // Skip during SSR

	try {
		localStorage.setItem(SIDEBAR_STORAGE_KEY, String(isOpen));
	} catch {
		// Silently fail if localStorage is not available
	}
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
