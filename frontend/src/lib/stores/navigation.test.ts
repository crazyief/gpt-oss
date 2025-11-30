/**
 * Unit tests for navigation store
 *
 * Tests: Tab switching, reset functionality
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { activeTab, tabs, type Tab } from './navigation';

describe('navigation store', () => {
	beforeEach(() => {
		activeTab.reset();
	});

	describe('initial state', () => {
		it('should start with chat tab active', () => {
			const tab = get(activeTab);
			expect(tab).toBe('chat');
		});
	});

	describe('setTab', () => {
		it('should switch to chat tab', () => {
			activeTab.setTab('chat');
			const tab = get(activeTab);
			expect(tab).toBe('chat');
		});

		it('should switch to documents tab', () => {
			activeTab.setTab('documents');
			const tab = get(activeTab);
			expect(tab).toBe('documents');
		});

		it('should switch to settings tab', () => {
			activeTab.setTab('settings');
			const tab = get(activeTab);
			expect(tab).toBe('settings');
		});

		it('should update when switching tabs multiple times', () => {
			activeTab.setTab('documents');
			expect(get(activeTab)).toBe('documents');

			activeTab.setTab('settings');
			expect(get(activeTab)).toBe('settings');

			activeTab.setTab('chat');
			expect(get(activeTab)).toBe('chat');
		});
	});

	describe('reset', () => {
		it('should reset to chat tab', () => {
			activeTab.setTab('settings');
			activeTab.reset();

			const tab = get(activeTab);
			expect(tab).toBe('chat');
		});

		it('should reset from any tab', () => {
			const tabsToTest: Tab[] = ['chat', 'documents', 'settings'];

			tabsToTest.forEach((testTab) => {
				activeTab.setTab(testTab);
				activeTab.reset();
				expect(get(activeTab)).toBe('chat');
			});
		});
	});

	describe('tabs configuration', () => {
		it('should have 3 tabs defined', () => {
			expect(tabs).toHaveLength(3);
		});

		it('should have chat tab with correct properties', () => {
			const chatTab = tabs.find((t) => t.id === 'chat');
			expect(chatTab).toBeDefined();
			expect(chatTab?.label).toBe('Chat');
			expect(chatTab?.icon).toBe('chat');
		});

		it('should have documents tab with correct properties', () => {
			const docsTab = tabs.find((t) => t.id === 'documents');
			expect(docsTab).toBeDefined();
			expect(docsTab?.label).toBe('Documents');
			expect(docsTab?.icon).toBe('document');
		});

		it('should have settings tab with correct properties', () => {
			const settingsTab = tabs.find((t) => t.id === 'settings');
			expect(settingsTab).toBeDefined();
			expect(settingsTab?.label).toBe('Settings');
			expect(settingsTab?.icon).toBe('settings');
		});

		it('should have unique tab IDs', () => {
			const ids = tabs.map((t) => t.id);
			const uniqueIds = new Set(ids);
			expect(uniqueIds.size).toBe(tabs.length);
		});

		it('should have non-empty labels', () => {
			tabs.forEach((tab) => {
				expect(tab.label).toBeTruthy();
				expect(tab.label.length).toBeGreaterThan(0);
			});
		});

		it('should have non-empty icons', () => {
			tabs.forEach((tab) => {
				expect(tab.icon).toBeTruthy();
				expect(tab.icon.length).toBeGreaterThan(0);
			});
		});
	});

	describe('reactive updates', () => {
		it('should notify subscribers when tab changes', () => {
			let notificationCount = 0;
			let lastValue: Tab = 'chat';

			const unsubscribe = activeTab.subscribe((value) => {
				notificationCount++;
				lastValue = value;
			});

			// Initial subscription triggers once
			expect(notificationCount).toBe(1);
			expect(lastValue).toBe('chat');

			// Change tab
			activeTab.setTab('documents');
			expect(notificationCount).toBe(2);
			expect(lastValue).toBe('documents');

			// Change again
			activeTab.setTab('settings');
			expect(notificationCount).toBe(3);
			expect(lastValue).toBe('settings');

			unsubscribe();
		});

		it('should notify subscribers on reset', () => {
			let notificationCount = 0;

			const unsubscribe = activeTab.subscribe(() => {
				notificationCount++;
			});

			// Initial: 1
			// setTab: 2
			// reset: 3
			activeTab.setTab('documents');
			activeTab.reset();

			expect(notificationCount).toBe(3);

			unsubscribe();
		});
	});
});
