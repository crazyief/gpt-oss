<script lang="ts">
	/**
	 * Root layout component
	 *
	 * Purpose: Global layout wrapper for all pages
	 *
	 * Responsibilities:
	 * - Import global styles (TailwindCSS)
	 * - Error boundary for unhandled errors
	 * - Toast notifications (global)
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
	
	// Import toast notification component
	import { SvelteToast } from '@zerodevx/svelte-toast';
</script>

<!--
Global layout wrapper with error boundary and toast notifications

Provides consistent structure, error handling, and notifications across all pages
-->
<ErrorBoundary>
	<div class="app">
		<!-- Page content slot (SvelteKit renders page components here) -->
		<slot />
	</div>
	
	<!-- Toast notification container (positioned top-right) -->
	<SvelteToast options={{ reversed: true, intro: { y: -64 } }} />
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

		/* Allow text selection for messages but not UI elements */
		/* Removed global user-select: none to allow message copying */

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
	
	/**
	 * Toast notification styling
	 *
	 * Position toasts at top-right with proper spacing
	 */
	:global(._toastContainer) {
		top: 1rem;
		right: 1rem;
		bottom: auto;
		left: auto;
	}
	
	:global(._toastItem) {
		border-radius: 0.5rem;
		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
		font-family: inherit;
		font-size: 0.875rem;
		line-height: 1.25rem;
		padding: 0.75rem 1rem;
		min-width: 300px;
		max-width: 500px;
	}
	
	:global(._toastMsg) {
		padding: 0;
	}
	
	:global(._toastBtn) {
		font-weight: 600;
		opacity: 0.8;
	}
	
	:global(._toastBtn:hover) {
		opacity: 1;
	}
</style>
