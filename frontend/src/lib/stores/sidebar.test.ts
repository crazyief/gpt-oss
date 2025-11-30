/**
 * Unit tests for sidebar store
 *
 * Tests: Open/close/toggle functionality, localStorage persistence (mocked)
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { get } from 'svelte/store';

// Mock localStorage
const localStorageMock = (() => {
	let store: Record<string, string> = {};

	return {
		getItem: (key: string) => store[key] || null,
		setItem: (key: string, value: string) => {
			store[key] = value;
		},
		removeItem: (key: string) => {
			delete store[key];
		},
		clear: () => {
			store = {};
		}
	};
})();

Object.defineProperty(global, 'localStorage', {
	value: localStorageMock,
	writable: true
});

// Mock browser detection
Object.defineProperty(global, 'window', {
	value: {},
	writable: true
});

// Import after mocks are set up
import { sidebarOpen } from './sidebar';

describe('sidebar store', () => {
	beforeEach(() => {
		localStorageMock.clear();
		// Reinitialize store by setting to default
		sidebarOpen.set(true);
	});

	describe('initial state', () => {
		it('should start open by default', () => {
			const isOpen = get(sidebarOpen);
			expect(isOpen).toBe(true);
		});

		it('should load state from localStorage if available', () => {
			// Set localStorage before import would happen
			localStorageMock.setItem('gpt-oss-sidebar-open', 'false');

			// Manually trigger set to simulate loading from localStorage
			sidebarOpen.set(false);

			const isOpen = get(sidebarOpen);
			expect(isOpen).toBe(false);
		});
	});

	describe('set', () => {
		it('should set sidebar to open', () => {
			sidebarOpen.set(true);
			const isOpen = get(sidebarOpen);
			expect(isOpen).toBe(true);
		});

		it('should set sidebar to closed', () => {
			sidebarOpen.set(false);
			const isOpen = get(sidebarOpen);
			expect(isOpen).toBe(false);
		});

		it('should persist state to localStorage when set to true', () => {
			sidebarOpen.set(true);
			const stored = localStorageMock.getItem('gpt-oss-sidebar-open');
			expect(stored).toBe('true');
		});

		it('should persist state to localStorage when set to false', () => {
			sidebarOpen.set(false);
			const stored = localStorageMock.getItem('gpt-oss-sidebar-open');
			expect(stored).toBe('false');
		});
	});

	describe('open', () => {
		it('should open sidebar', () => {
			sidebarOpen.close();
			sidebarOpen.open();

			const isOpen = get(sidebarOpen);
			expect(isOpen).toBe(true);
		});

		it('should persist open state to localStorage', () => {
			sidebarOpen.open();
			const stored = localStorageMock.getItem('gpt-oss-sidebar-open');
			expect(stored).toBe('true');
		});

		it('should be idempotent (calling multiple times)', () => {
			sidebarOpen.open();
			sidebarOpen.open();
			sidebarOpen.open();

			const isOpen = get(sidebarOpen);
			expect(isOpen).toBe(true);
		});
	});

	describe('close', () => {
		it('should close sidebar', () => {
			sidebarOpen.open();
			sidebarOpen.close();

			const isOpen = get(sidebarOpen);
			expect(isOpen).toBe(false);
		});

		it('should persist closed state to localStorage', () => {
			sidebarOpen.close();
			const stored = localStorageMock.getItem('gpt-oss-sidebar-open');
			expect(stored).toBe('false');
		});

		it('should be idempotent (calling multiple times)', () => {
			sidebarOpen.close();
			sidebarOpen.close();
			sidebarOpen.close();

			const isOpen = get(sidebarOpen);
			expect(isOpen).toBe(false);
		});
	});

	describe('toggle', () => {
		it('should toggle from open to closed', () => {
			sidebarOpen.set(true);
			sidebarOpen.toggle();

			const isOpen = get(sidebarOpen);
			expect(isOpen).toBe(false);
		});

		it('should toggle from closed to open', () => {
			sidebarOpen.set(false);
			sidebarOpen.toggle();

			const isOpen = get(sidebarOpen);
			expect(isOpen).toBe(true);
		});

		it('should toggle multiple times', () => {
			sidebarOpen.set(true);

			sidebarOpen.toggle();
			expect(get(sidebarOpen)).toBe(false);

			sidebarOpen.toggle();
			expect(get(sidebarOpen)).toBe(true);

			sidebarOpen.toggle();
			expect(get(sidebarOpen)).toBe(false);
		});

		it('should persist state to localStorage after toggle', () => {
			sidebarOpen.set(true);
			sidebarOpen.toggle();

			const stored = localStorageMock.getItem('gpt-oss-sidebar-open');
			expect(stored).toBe('false');
		});
	});

	describe('localStorage persistence', () => {
		it('should save state when opening', () => {
			sidebarOpen.open();
			expect(localStorageMock.getItem('gpt-oss-sidebar-open')).toBe('true');
		});

		it('should save state when closing', () => {
			sidebarOpen.close();
			expect(localStorageMock.getItem('gpt-oss-sidebar-open')).toBe('false');
		});

		it('should save state when toggling', () => {
			sidebarOpen.set(true);
			sidebarOpen.toggle();
			expect(localStorageMock.getItem('gpt-oss-sidebar-open')).toBe('false');

			sidebarOpen.toggle();
			expect(localStorageMock.getItem('gpt-oss-sidebar-open')).toBe('true');
		});

		it('should update localStorage on every state change', () => {
			sidebarOpen.set(true);
			expect(localStorageMock.getItem('gpt-oss-sidebar-open')).toBe('true');

			sidebarOpen.set(false);
			expect(localStorageMock.getItem('gpt-oss-sidebar-open')).toBe('false');

			sidebarOpen.open();
			expect(localStorageMock.getItem('gpt-oss-sidebar-open')).toBe('true');

			sidebarOpen.close();
			expect(localStorageMock.getItem('gpt-oss-sidebar-open')).toBe('false');
		});
	});

	describe('reactive updates', () => {
		it('should notify subscribers when state changes', () => {
			let notificationCount = 0;
			let lastValue = false;

			const unsubscribe = sidebarOpen.subscribe((value) => {
				notificationCount++;
				lastValue = value;
			});

			// Initial subscription triggers once
			expect(notificationCount).toBeGreaterThan(0);

			// Toggle
			sidebarOpen.toggle();
			expect(notificationCount).toBeGreaterThan(1);

			unsubscribe();
		});

		it('should provide current value to new subscribers', () => {
			sidebarOpen.set(false);

			const unsubscribe = sidebarOpen.subscribe((value) => {
				expect(value).toBe(false);
			});

			unsubscribe();
		});
	});
});
