<script lang="ts">
	/**
	 * Root layout component
	 *
	 * Purpose: Global layout wrapper for all pages
	 *
	 * Responsibilities:
	 * - Import global styles (TailwindCSS)
	 * - Initialize theme system
	 * - Error boundary for unhandled errors
	 * - Toast notifications (global)
	 * - Preload CSRF token (security)
	 * - Render page content via <slot />
	 */

	import { onMount } from 'svelte';

	// Import global TailwindCSS styles
	import '../app.css';
	import ErrorBoundary from '$lib/components/ErrorBoundary.svelte';

	// Import toast notification component
	import { SvelteToast } from '@zerodevx/svelte-toast';

	// Import CSRF preload utility
	import { preloadCsrfToken } from '$lib/utils/csrf-preload';

	// Import theme store
	import { theme } from '$lib/stores/theme';

	/**
	 * SvelteKit internal props handling
	 *
	 * SvelteKit passes various props to layout/page components.
	 * Using $$restProps allows us to accept any prop without warnings.
	 *
	 * Standard SvelteKit props:
	 * - data: From load functions (+layout.ts/+page.ts)
	 * - form: From form actions (+page.server.ts)
	 *
	 * Note: $$restProps is used implicitly in templates to capture unknown props.
	 * We export `data` and `form` explicitly for type safety.
	 *
	 * See: https://svelte.dev/docs/basic-markup#attributes-and-props
	 */
	// eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
	export let data: any = undefined;
	// eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
	export let form: any = undefined;

	// Capture any additional props SvelteKit might pass (prevents "unknown prop" warnings)
	// This pattern is recommended for SvelteKit 2.x layouts
	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	export let params: any = undefined; // BUG-006 FIX: SvelteKit 2.x passes params

	onMount(async () => {
		// Initialize theme system (applies saved theme from localStorage)
		theme.initialize();

		// Preload CSRF token in background (non-blocking)
		preloadCsrfToken();
	});
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
	<SvelteToast options={{ reversed: true, intro: { y: -64 }, duration: 3000, dismissable: true }} />
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
	 * Reset default body styles (theme-aware)
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
		background-color: var(--bg-primary);
		color: var(--text-primary);
		transition: background-color 0.3s ease, color 0.3s ease;
	}

	/**
	 * Scrollbar styling (theme-aware)
	 */
	:global(::-webkit-scrollbar) {
		width: 8px;
		height: 8px;
	}

	:global(::-webkit-scrollbar-track) {
		background: var(--scrollbar-track);
	}

	:global(::-webkit-scrollbar-thumb) {
		background: var(--scrollbar-thumb);
		border-radius: 4px;
	}

	:global(::-webkit-scrollbar-thumb:hover) {
		background: var(--accent);
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
