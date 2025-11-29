/**
 * Theme Store - Global theme management with localStorage persistence
 *
 * Themes:
 * - dark: Dark blue/slate theme (default)
 * - matrix: Black with neon green (Matrix style)
 * - light: White/light gray theme
 */

import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export type Theme = 'dark' | 'matrix' | 'light';

const STORAGE_KEY = 'gpt-oss-theme';
const DEFAULT_THEME: Theme = 'dark';

/**
 * Get initial theme from localStorage or default
 */
function getInitialTheme(): Theme {
	if (!browser) return DEFAULT_THEME;

	const stored = localStorage.getItem(STORAGE_KEY);
	if (stored === 'dark' || stored === 'matrix' || stored === 'light') {
		return stored;
	}
	return DEFAULT_THEME;
}

/**
 * Apply theme to document
 */
function applyTheme(theme: Theme): void {
	if (!browser) return;
	document.documentElement.setAttribute('data-theme', theme);
}

/**
 * Create theme store
 */
function createThemeStore() {
	const initial = getInitialTheme();
	const { subscribe, set, update } = writable<Theme>(initial);

	// Apply initial theme
	if (browser) {
		applyTheme(initial);
	}

	return {
		subscribe,

		/**
		 * Set specific theme
		 */
		setTheme: (theme: Theme) => {
			if (browser) {
				localStorage.setItem(STORAGE_KEY, theme);
				applyTheme(theme);
			}
			set(theme);
		},

		/**
		 * Cycle through themes: dark -> matrix -> light -> dark
		 */
		cycle: () => {
			update(current => {
				const themes: Theme[] = ['dark', 'matrix', 'light'];
				const currentIndex = themes.indexOf(current);
				const next = themes[(currentIndex + 1) % themes.length];

				if (browser) {
					localStorage.setItem(STORAGE_KEY, next);
					applyTheme(next);
				}

				return next;
			});
		},

		/**
		 * Initialize theme on mount (for SSR hydration)
		 */
		initialize: () => {
			const theme = getInitialTheme();
			applyTheme(theme);
			set(theme);
		}
	};
}

export const theme = createThemeStore();

/**
 * Theme display names for UI
 */
export const themeNames: Record<Theme, string> = {
	dark: 'Dark',
	matrix: 'Matrix',
	light: 'Light'
};

/**
 * Theme icons for UI
 */
export const themeIcons: Record<Theme, string> = {
	dark: '🌙',
	matrix: '💚',
	light: '☀️'
};
