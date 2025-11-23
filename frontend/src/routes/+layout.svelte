<script lang="ts">
	/**
	 * Root layout component
	 *
	 * Purpose: Global layout wrapper for all pages
	 *
	 * Responsibilities:
	 * - Import global styles (TailwindCSS)
	 * - Error boundary for unhandled errors
	 * - Provide app-wide context (future: auth, theme)
	 * - Render page content via <slot />
	 *
	 * Layout hierarchy:
	 * +layout.svelte (this file)
	 *   └─ +page.svelte (project list)
	 *   └─ project/[id]/+page.svelte (chat interface)
	 */

	// Import global TailwindCSS styles
	import '../app.css';
	import ErrorBoundary from '$lib/components/ErrorBoundary.svelte';
</script>

<!--
Global layout wrapper with error boundary

Provides consistent structure and error handling across all pages
-->
<ErrorBoundary>
	<div class="app">
		<!-- Page content slot (SvelteKit renders page components here) -->
		<slot />
	</div>
</ErrorBoundary>

<style>
	/**
	 * Global app styles
	 *
	 * Base styles for app wrapper
	 */
	.app {
		/* Full viewport height */
		width: 100%;
		height: 100vh;
		overflow: hidden;

		/* Prevent text selection artifacts */
		user-select: none;

		/* Font smoothing for better readability */
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
	}

	/**
	 * Reset default body styles
	 *
	 * Remove margins and set base font
	 */
	:global(body) {
		margin: 0;
		padding: 0;
		font-family:
			system-ui,
			-apple-system,
			BlinkMacSystemFont,
			'Segoe UI',
			Roboto,
			'Helvetica Neue',
			Arial,
			sans-serif;
		background-color: #ffffff;
		color: #374151;
	}

	/**
	 * Scrollbar styling (WebKit browsers)
	 *
	 * Custom scrollbar for better aesthetics
	 */
	:global(::-webkit-scrollbar) {
		width: 8px;
		height: 8px;
	}

	:global(::-webkit-scrollbar-track) {
		background: #f3f4f6;
	}

	:global(::-webkit-scrollbar-thumb) {
		background: #d1d5db;
		border-radius: 4px;
	}

	:global(::-webkit-scrollbar-thumb:hover) {
		background: #9ca3af;
	}
</style>
