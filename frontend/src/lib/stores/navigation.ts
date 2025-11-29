/**
 * Navigation Store - Active tab management
 *
 * Tabs: chat, documents, settings
 */

import { writable } from 'svelte/store';

export type Tab = 'chat' | 'documents' | 'settings';

const DEFAULT_TAB: Tab = 'chat';

function createNavigationStore() {
	const { subscribe, set } = writable<Tab>(DEFAULT_TAB);

	return {
		subscribe,

		/**
		 * Set active tab
		 */
		setTab: (tab: Tab) => {
			set(tab);
		},

		/**
		 * Reset to default tab (chat)
		 */
		reset: () => {
			set(DEFAULT_TAB);
		}
	};
}

export const activeTab = createNavigationStore();

/**
 * Tab configuration for UI
 */
export const tabs: { id: Tab; label: string; icon: string }[] = [
	{ id: 'chat', label: 'Chat', icon: 'chat' },
	{ id: 'documents', label: 'Documents', icon: 'document' },
	{ id: 'settings', label: 'Settings', icon: 'settings' }
];
