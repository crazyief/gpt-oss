/**
 * Unit tests for theme store
 *
 * Tests: Theme switching, cycling, localStorage persistence (mocked)
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

// Mock document.documentElement.setAttribute
const mockSetAttribute = vi.fn();
Object.defineProperty(global, 'document', {
	value: {
		documentElement: {
			setAttribute: mockSetAttribute
		}
	},
	writable: true
});

// Import after mocks are set up
import { theme, themeNames, themeIcons, type Theme } from './theme';

describe('theme store', () => {
	beforeEach(() => {
		localStorageMock.clear();
		mockSetAttribute.mockClear();
		theme.setTheme('dark'); // Reset to default
	});

	describe('initial state', () => {
		it('should start with dark theme by default', () => {
			const currentTheme = get(theme);
			expect(currentTheme).toBe('dark');
		});

		it('should load theme from localStorage if available', () => {
			localStorageMock.setItem('gpt-oss-theme', 'matrix');
			theme.setTheme('matrix');

			const currentTheme = get(theme);
			expect(currentTheme).toBe('matrix');
		});
	});

	describe('setTheme', () => {
		it('should set dark theme', () => {
			theme.setTheme('dark');
			const currentTheme = get(theme);
			expect(currentTheme).toBe('dark');
		});

		it('should set matrix theme', () => {
			theme.setTheme('matrix');
			const currentTheme = get(theme);
			expect(currentTheme).toBe('matrix');
		});

		it('should set light theme', () => {
			theme.setTheme('light');
			const currentTheme = get(theme);
			expect(currentTheme).toBe('light');
		});

		it('should persist theme to localStorage', () => {
			theme.setTheme('matrix');
			const stored = localStorageMock.getItem('gpt-oss-theme');
			expect(stored).toBe('matrix');
		});

		it('should apply theme to document element', () => {
			theme.setTheme('light');
			expect(mockSetAttribute).toHaveBeenCalledWith('data-theme', 'light');
		});

		it('should update localStorage when switching themes', () => {
			theme.setTheme('dark');
			expect(localStorageMock.getItem('gpt-oss-theme')).toBe('dark');

			theme.setTheme('matrix');
			expect(localStorageMock.getItem('gpt-oss-theme')).toBe('matrix');

			theme.setTheme('light');
			expect(localStorageMock.getItem('gpt-oss-theme')).toBe('light');
		});
	});

	describe('cycle', () => {
		it('should cycle from dark to matrix', () => {
			theme.setTheme('dark');
			theme.cycle();

			const currentTheme = get(theme);
			expect(currentTheme).toBe('matrix');
		});

		it('should cycle from matrix to light', () => {
			theme.setTheme('matrix');
			theme.cycle();

			const currentTheme = get(theme);
			expect(currentTheme).toBe('light');
		});

		it('should cycle from light to dark (wrap around)', () => {
			theme.setTheme('light');
			theme.cycle();

			const currentTheme = get(theme);
			expect(currentTheme).toBe('dark');
		});

		it('should cycle through all themes in order', () => {
			theme.setTheme('dark');

			theme.cycle();
			expect(get(theme)).toBe('matrix');

			theme.cycle();
			expect(get(theme)).toBe('light');

			theme.cycle();
			expect(get(theme)).toBe('dark');
		});

		it('should persist cycled theme to localStorage', () => {
			theme.setTheme('dark');
			theme.cycle();

			const stored = localStorageMock.getItem('gpt-oss-theme');
			expect(stored).toBe('matrix');
		});

		it('should apply cycled theme to document element', () => {
			mockSetAttribute.mockClear();
			theme.setTheme('dark');
			theme.cycle();

			expect(mockSetAttribute).toHaveBeenCalledWith('data-theme', 'matrix');
		});
	});

	describe('initialize', () => {
		it('should initialize theme from default', () => {
			theme.initialize();
			const currentTheme = get(theme);
			expect(['dark', 'matrix', 'light']).toContain(currentTheme);
		});

		it('should apply theme to document element on initialize', () => {
			mockSetAttribute.mockClear();
			theme.initialize();

			expect(mockSetAttribute).toHaveBeenCalled();
			expect(mockSetAttribute.mock.calls[0][0]).toBe('data-theme');
		});
	});

	describe('themeNames', () => {
		it('should have display name for dark theme', () => {
			expect(themeNames.dark).toBe('Dark');
		});

		it('should have display name for matrix theme', () => {
			expect(themeNames.matrix).toBe('Matrix');
		});

		it('should have display name for light theme', () => {
			expect(themeNames.light).toBe('Light');
		});

		it('should have names for all themes', () => {
			const themes: Theme[] = ['dark', 'matrix', 'light'];
			themes.forEach((t) => {
				expect(themeNames[t]).toBeTruthy();
			});
		});
	});

	describe('themeIcons', () => {
		it('should have icon for dark theme', () => {
			expect(themeIcons.dark).toBe('🌙');
		});

		it('should have icon for matrix theme', () => {
			expect(themeIcons.matrix).toBe('💚');
		});

		it('should have icon for light theme', () => {
			expect(themeIcons.light).toBe('☀️');
		});

		it('should have icons for all themes', () => {
			const themes: Theme[] = ['dark', 'matrix', 'light'];
			themes.forEach((t) => {
				expect(themeIcons[t]).toBeTruthy();
			});
		});
	});

	describe('localStorage persistence', () => {
		it('should save theme when setting', () => {
			theme.setTheme('matrix');
			expect(localStorageMock.getItem('gpt-oss-theme')).toBe('matrix');
		});

		it('should save theme when cycling', () => {
			theme.setTheme('dark');
			theme.cycle();
			expect(localStorageMock.getItem('gpt-oss-theme')).toBe('matrix');
		});

		it('should update localStorage on every theme change', () => {
			theme.setTheme('dark');
			expect(localStorageMock.getItem('gpt-oss-theme')).toBe('dark');

			theme.setTheme('matrix');
			expect(localStorageMock.getItem('gpt-oss-theme')).toBe('matrix');

			theme.setTheme('light');
			expect(localStorageMock.getItem('gpt-oss-theme')).toBe('light');
		});
	});

	describe('document element updates', () => {
		it('should apply data-theme attribute when setting theme', () => {
			mockSetAttribute.mockClear();
			theme.setTheme('dark');

			expect(mockSetAttribute).toHaveBeenCalledWith('data-theme', 'dark');
		});

		it('should update data-theme attribute on every theme change', () => {
			mockSetAttribute.mockClear();

			theme.setTheme('dark');
			expect(mockSetAttribute).toHaveBeenCalledWith('data-theme', 'dark');

			theme.setTheme('matrix');
			expect(mockSetAttribute).toHaveBeenCalledWith('data-theme', 'matrix');

			theme.setTheme('light');
			expect(mockSetAttribute).toHaveBeenCalledWith('data-theme', 'light');
		});
	});

	describe('reactive updates', () => {
		it('should notify subscribers when theme changes', () => {
			let notificationCount = 0;
			let lastValue: Theme = 'dark';

			const unsubscribe = theme.subscribe((value) => {
				notificationCount++;
				lastValue = value;
			});

			const initialCount = notificationCount;

			theme.setTheme('matrix');
			expect(notificationCount).toBe(initialCount + 1);
			expect(lastValue).toBe('matrix');

			unsubscribe();
		});

		it('should notify subscribers when cycling', () => {
			let notificationCount = 0;

			const unsubscribe = theme.subscribe(() => {
				notificationCount++;
			});

			const initialCount = notificationCount;

			theme.cycle();
			expect(notificationCount).toBe(initialCount + 1);

			unsubscribe();
		});
	});
});
