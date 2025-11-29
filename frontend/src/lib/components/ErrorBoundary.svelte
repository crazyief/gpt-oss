<script lang="ts">
/**
 * Error Boundary Component
 *
 * Purpose: Catch unhandled errors and display user-friendly error page
 *
 * Features:
 * - Global error handler for runtime errors
 * - Promise rejection handler for async errors
 * - Error details display (development only)
 * - Reload button to recover
 * - Automatic error logging
 *
 * WHY error boundaries:
 * - Graceful degradation: One component crash doesn't kill entire app
 * - Better UX: User sees error page instead of blank screen
 * - Debugging: Error details help developers diagnose issues
 * - Recovery: User can reload without losing work
 *
 * WHY global handlers instead of component-level try/catch:
 * - Comprehensive: Catches errors from all components
 * - Minimal boilerplate: No need to wrap every component
 * - Last resort: Component-level handlers can still catch specific errors
 *
 * Svelte limitation: No built-in error boundaries like React
 * Solution: Use global window error handlers
 */

import { onMount } from 'svelte';
import { logger } from '$lib/utils/logger';

// Error state
let hasError = false;
let errorMessage = '';
let errorStack = '';
let isDevelopment = import.meta.env.DEV;

/**
 * Initialize global error handlers on mount
 *
 * WHY onMount instead of top-level:
 * - SSR compatibility: window is undefined during SSR
 * - Cleanup: Can remove handlers on unmount
 * - Lifecycle: Matches Svelte component lifecycle
 */
onMount(() => {
	/**
	 * Handle runtime errors
	 *
	 * WHY ErrorEvent:
	 * - Standard browser event for uncaught exceptions
	 * - Includes message, filename, line number, stack trace
	 *
	 * WHY preventDefault:
	 * - Suppress default browser error display (red text in console)
	 * - We show our own error UI
	 */
	const handleError = (event: ErrorEvent) => {
		hasError = true;
		errorMessage = event.message;
		errorStack = event.error?.stack || '';

		// Log error for debugging
		logger.error('Unhandled error', {
			message: event.message,
			filename: event.filename,
			lineno: event.lineno,
			colno: event.colno,
			stack: errorStack
		});

		// Prevent default browser error display
		event.preventDefault();
	};

	/**
	 * Handle unhandled promise rejections
	 *
	 * WHY separate handler:
	 * - Promises throw different event type (PromiseRejectionEvent)
	 * - Common source of errors (async/await, fetch, etc.)
	 * - Browser shows "Uncaught (in promise)" by default
	 *
	 * WHY preventDefault:
	 * - Same as handleError, suppress default display
	 */
	const handleRejection = (event: PromiseRejectionEvent) => {
		hasError = true;
		errorMessage = event.reason?.message || 'Promise rejection';
		errorStack = event.reason?.stack || '';

		// Log error for debugging
		logger.error('Unhandled promise rejection', {
			reason: event.reason,
			promise: event.promise
		});

		// Prevent default browser error display
		event.preventDefault();
	};

	// Register global error handlers
	window.addEventListener('error', handleError);
	window.addEventListener('unhandledrejection', handleRejection);

	// Cleanup: Remove handlers on unmount
	return () => {
		window.removeEventListener('error', handleError);
		window.removeEventListener('unhandledrejection', handleRejection);
	};
});

/**
 * Reload application
 *
 * WHY location.reload instead of router navigation:
 * - Fresh start: Clears all JavaScript state
 * - Simple recovery: Most errors resolve with reload
 * - No state preservation: Intentional, state might be corrupted
 */
function handleReload() {
	window.location.reload();
}
</script>

{#if hasError}
	<!-- Error state: Show error page -->
	<div class="error-boundary" data-testid="error-boundary">
		<div class="error-content" data-testid="error-content">
			<div class="error-icon" data-testid="error-icon">
				<svg
					width="64"
					height="64"
					viewBox="0 0 64 64"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<circle cx="32" cy="32" r="30" stroke="#dc2626" stroke-width="2" />
					<path d="M32 16v24M32 48h.01" stroke="#dc2626" stroke-width="2" stroke-linecap="round" />
				</svg>
			</div>

			<h1>Something went wrong</h1>
			<p>The application encountered an unexpected error. Please try reloading the page.</p>

			<!-- Error details (development only) -->
			{#if isDevelopment}
				<details class="error-details" data-testid="error-details">
					<summary>Error details (development only)</summary>
					<div class="error-info">
						<div class="error-section">
							<h3>Message</h3>
							<pre data-testid="error-message">{errorMessage}</pre>
						</div>
						{#if errorStack}
							<div class="error-section">
								<h3>Stack trace</h3>
								<pre data-testid="error-stack">{errorStack}</pre>
							</div>
						{/if}
					</div>
				</details>
			{/if}

			<button on:click={handleReload} class="reload-button" data-testid="reload-button">Reload Application</button>
		</div>
	</div>
{:else}
	<!-- Normal state: Render children -->
	<slot />
{/if}

<style>
	/**
	 * Error boundary container
	 *
	 * WHY full viewport:
	 * - Replace entire app with error page
	 * - No partial rendering (prevents layout shifts)
	 * - Clear visual signal: something is wrong
	 */
	.error-boundary {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		padding: 2rem;
		background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
	}

	/**
	 * Error content card
	 *
	 * WHY card design:
	 * - Focus: Draw attention to error message
	 * - Contrast: White card on red background
	 * - Accessibility: High contrast for readability
	 */
	.error-content {
		max-width: 600px;
		padding: 2rem;
		background: white;
		border-radius: 8px;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
		text-align: center;
	}

	/**
	 * Error icon
	 *
	 * WHY icon:
	 * - Visual cue: Immediate recognition of error state
	 * - Professional: Better than plain text
	 * - Accessibility: Supplement with text for screen readers
	 */
	.error-icon {
		display: flex;
		justify-content: center;
		margin-bottom: 1.5rem;
	}

	.error-content h1 {
		margin: 0 0 1rem;
		font-size: 1.5rem;
		font-weight: 600;
		color: #111827;
	}

	.error-content p {
		margin: 0 0 1.5rem;
		color: #6b7280;
		line-height: 1.5;
	}

	/**
	 * Reload button
	 *
	 * WHY prominent button:
	 * - Primary action: Most common recovery action
	 * - Easy to find: Large, centered, high contrast
	 * - Clear purpose: "Reload" is self-explanatory
	 */
	.reload-button {
		padding: 0.75rem 1.5rem;
		background: #3b82f6;
		color: white;
		border: none;
		border-radius: 6px;
		font-size: 1rem;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.2s ease;
	}

	.reload-button:hover {
		background: #2563eb;
	}

	.reload-button:active {
		background: #1d4ed8;
	}

	/**
	 * Error details (development only)
	 *
	 * WHY collapsible:
	 * - Progressive disclosure: Don't overwhelm user
	 * - Clean UI: Details hidden by default
	 * - Developer focused: Only show in development
	 */
	.error-details {
		margin: 1.5rem 0;
		padding: 1rem;
		background: #f9fafb;
		border: 1px solid #e5e7eb;
		border-radius: 6px;
		text-align: left;
	}

	.error-details summary {
		cursor: pointer;
		font-weight: 500;
		color: #374151;
		user-select: none;
	}

	.error-details summary:hover {
		color: #111827;
	}

	.error-info {
		margin-top: 1rem;
	}

	.error-section {
		margin-bottom: 1rem;
	}

	.error-section h3 {
		margin: 0 0 0.5rem;
		font-size: 0.875rem;
		font-weight: 600;
		color: #374151;
	}

	.error-section pre {
		margin: 0;
		padding: 0.75rem;
		background: white;
		border: 1px solid #e5e7eb;
		border-radius: 4px;
		font-size: 0.8125rem;
		line-height: 1.5;
		overflow-x: auto;
		color: #dc2626;
		white-space: pre-wrap;
		word-wrap: break-word;
	}

	/**
	 * Responsive: Smaller padding on mobile
	 */
	@media (max-width: 640px) {
		.error-boundary {
			padding: 1rem;
		}

		.error-content {
			padding: 1.5rem;
		}

		.error-content h1 {
			font-size: 1.25rem;
		}
	}
</style>
