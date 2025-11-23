<script lang="ts">
/**
 * SearchInput component
 *
 * Purpose: Debounced search input for filtering conversations
 *
 * Features:
 * - Real-time filtering with 300ms debounce
 * - Clear button when input has value
 * - Accessible keyboard navigation
 * - Focus on Cmd/Ctrl+K shortcut (common search pattern)
 *
 * Design decisions:
 * - Debounce prevents excessive filtering on every keystroke
 * - 300ms delay balances responsiveness vs. performance
 * - Clear button improves UX (faster than backspace)
 * - Keyboard shortcut matches familiar patterns (VSCode, Slack, etc.)
 *
 * WHY debounce in component instead of store:
 * - UI concern: Debounce is about input delay, not data filtering
 * - Reusability: Can reuse SearchInput with different stores
 * - Testing: Easier to test debounce logic in isolation
 */

import { onMount, onDestroy } from 'svelte';
import { browser } from '$app/environment';
import { conversations } from '$lib/stores/conversations';
import { APP_CONFIG } from '$lib/config';

// Local state for input value (separate from store for debouncing)
let inputValue = '';
let inputElement: HTMLInputElement;
let debounceTimer: ReturnType<typeof setTimeout> | null = null;

/**
 * Handle input change with debounce
 *
 * WHY debounce search instead of instant filtering:
 * - Performance: Prevents re-rendering list on every keystroke
 * - User experience: User expects slight delay (feels more responsive than instant)
 * - Network efficiency: If backend search, reduces API calls (50 chars = 50 calls vs 1 call)
 *
 * WHY 300ms specifically:
 * - Research: Average typing speed = ~200ms per character
 * - UX studies: 300ms feels instant while avoiding premature filtering
 * - Common pattern: Google search, VSCode use similar delays
 *
 * Implementation: Clear existing timer, start new one (debounce pattern)
 */
function handleInput(event: Event) {
	const target = event.target as HTMLInputElement;
	inputValue = target.value;

	// Clear existing debounce timer
	if (debounceTimer) {
		clearTimeout(debounceTimer);
	}

	// Set new debounce timer
	debounceTimer = setTimeout(() => {
		conversations.setSearchQuery(inputValue);
	}, APP_CONFIG.sidebar.searchDebounceMs);
}

/**
 * Clear search input and reset filter
 *
 * WHY separate clear function instead of just setting inputValue = '':
 * - Immediate feedback: Updates store without debounce delay
 * - Focus management: Keeps input focused after clearing
 * - Analytics: Could track "clear" as distinct user action
 */
function clearSearch() {
	inputValue = '';
	conversations.setSearchQuery('');
	inputElement?.focus(); // Keep focus in input for continued typing
}

/**
 * Global keyboard shortcut handler
 *
 * WHY Cmd/Ctrl+K for search:
 * - Industry standard: VSCode, Slack, Discord, Linear all use Cmd+K
 * - Muscle memory: Users expect this shortcut
 * - Accessibility: Keyboard-only navigation support
 *
 * WHY check metaKey || ctrlKey:
 * - macOS: Cmd key (metaKey)
 * - Windows/Linux: Ctrl key (ctrlKey)
 * - Cross-platform UX consistency
 */
function handleKeydown(event: KeyboardEvent) {
	if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
		event.preventDefault(); // Prevent browser default (sometimes opens search bar)
		inputElement?.focus();
	}
}

// Register keyboard shortcut on mount
// WHY browser check: window doesn't exist during SSR (server-side rendering)
// Only add event listener when running in browser
onMount(() => {
	if (browser) {
		window.addEventListener('keydown', handleKeydown);
	}
});

// Cleanup: Clear debounce timer and keyboard listener
onDestroy(() => {
	if (debounceTimer) {
		clearTimeout(debounceTimer);
	}
	if (browser) {
		window.removeEventListener('keydown', handleKeydown);
	}
});
</script>

<div class="search-input-container">
	<!-- Search icon (visual indicator of search functionality) -->
	<svg
		class="search-icon"
		width="20"
		height="20"
		viewBox="0 0 20 20"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		aria-hidden="true"
	>
		<path
			d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM19 19l-4.35-4.35"
			stroke="currentColor"
			stroke-width="2"
			stroke-linecap="round"
			stroke-linejoin="round"
		/>
	</svg>

	<!-- Search input field -->
	<input
		bind:this={inputElement}
		type="text"
		placeholder="Search conversations... (⌘K)"
		value={inputValue}
		on:input={handleInput}
		class="search-input"
		aria-label="Search conversations"
	/>

	<!-- Clear button (only show when input has value) -->
	{#if inputValue}
		<button
			type="button"
			on:click={clearSearch}
			class="clear-button"
			aria-label="Clear search"
		>
			<svg
				width="16"
				height="16"
				viewBox="0 0 16 16"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M12 4L4 12M4 4l8 8"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
				/>
			</svg>
		</button>
	{/if}
</div>

<style>
	/**
	 * Search input container
	 *
	 * Layout: Flexbox with icon + input + clear button
	 * WHY relative positioning: Allows absolute positioning of icons inside
	 */
	.search-input-container {
		position: relative;
		display: flex;
		align-items: center;
		padding: 0.5rem 0.75rem;
	}

	/**
	 * Search icon
	 *
	 * WHY absolute positioning instead of flexbox:
	 * - Fixed position: Icon doesn't shift when input value changes
	 * - Input padding: Can adjust text padding without affecting icon
	 * - Common pattern: Google, GitHub, etc. use this layout
	 */
	.search-icon {
		position: absolute;
		left: 1rem;
		color: #6b7280; /* Gray 500 */
		pointer-events: none; /* Allow clicks to pass through to input */
	}

	/**
	 * Search input field
	 *
	 * Styling: Rounded border, padding for icon/clear button
	 * WHY specific padding values:
	 * - Left: 2.5rem = space for search icon (20px icon + 12px padding)
	 * - Right: 2rem = space for clear button when visible
	 */
	.search-input {
		width: 100%;
		padding: 0.5rem 2rem 0.5rem 2.5rem;
		border: 1px solid #e5e7eb; /* Gray 200 */
		border-radius: 0.5rem;
		font-size: 0.875rem;
		background-color: #f9fafb; /* Gray 50 */
		transition: all 0.2s ease;
	}

	/**
	 * Input focus state
	 *
	 * WHY blue ring instead of default browser outline:
	 * - Consistent: Matches Tailwind/modern UI libraries
	 * - Visible: More obvious than browser default
	 * - Accessible: Meets WCAG 2.1 AA contrast requirements
	 */
	.search-input:focus {
		outline: none;
		border-color: #3b82f6; /* Blue 500 */
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
		background-color: white;
	}

	/**
	 * Clear button
	 *
	 * WHY absolute positioning:
	 * - Fixed position: Doesn't shift input text
	 * - Animation: Can fade in/out smoothly (future enhancement)
	 */
	.clear-button {
		position: absolute;
		right: 1rem;
		padding: 0.25rem;
		color: #6b7280;
		background: none;
		border: none;
		cursor: pointer;
		border-radius: 0.25rem;
		transition: all 0.2s ease;
	}

	/**
	 * Clear button hover state
	 *
	 * WHY gray background on hover:
	 * - Affordance: Signals button is clickable
	 * - Common pattern: macOS, iOS use this style
	 */
	.clear-button:hover {
		color: #374151; /* Gray 700 */
		background-color: #e5e7eb; /* Gray 200 */
	}

	/**
	 * Clear button focus state
	 *
	 * Accessibility: Keyboard navigation support
	 */
	.clear-button:focus {
		outline: 2px solid #3b82f6;
		outline-offset: 2px;
	}
</style>
