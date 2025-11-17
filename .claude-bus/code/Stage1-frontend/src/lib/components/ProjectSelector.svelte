<script lang="ts">
/**
 * ProjectSelector component
 *
 * Purpose: Dropdown to select current project and filter conversations
 *
 * Features:
 * - Dropdown showing all projects
 * - "All Projects" option to show unfiltered conversation list
 * - Auto-load conversations when project changes
 * - Loading state during initial project fetch
 *
 * Design decisions:
 * - Simple select dropdown (not custom dropdown component)
 * - "All Projects" as default selection
 * - Auto-fetch conversations on change (immediate feedback)
 *
 * WHY native select instead of custom dropdown:
 * - Accessibility: Native select has built-in keyboard navigation, screen reader support
 * - Mobile UX: Native select uses OS picker on mobile (better UX)
 * - Simplicity: Less code, fewer bugs
 * - Performance: No JS overhead for dropdown state management
 * - Future upgrade: Can replace with custom component later if needed
 */

import { onMount } from 'svelte';
import { writable } from 'svelte/store';
import type { Project } from '$lib/types';
import { conversations } from '$lib/stores/conversations';
import { fetchProjects, fetchConversations } from '$lib/services/api-client';

// Component state
let projects: Project[] = [];
let selectedProjectId: number | null = null; // null = "All Projects"
let isLoading = true;
let error: string | null = null;

/**
 * Load projects on component mount
 *
 * WHY fetch on mount instead of parent passing projects as prop:
 * - Self-contained: Component manages its own data (encapsulation)
 * - Reusability: Can use ProjectSelector anywhere without setup
 * - Simplicity: No need to coordinate parent/child state
 *
 * Trade-off: Multiple instances would duplicate fetch
 * - Acceptable for Stage 1: Only one ProjectSelector in sidebar
 * - Future: Move to global store if needed elsewhere
 */
onMount(async () => {
	try {
		const response = await fetchProjects();
		projects = response.projects;

		// Load all conversations by default (selectedProjectId = null)
		await loadConversations(null);
	} catch (err) {
		error = err instanceof Error ? err.message : 'Failed to load projects';
		console.error('Failed to load projects:', err);
	} finally {
		isLoading = false;
	}
});

/**
 * Load conversations for selected project
 *
 * WHY filter conversations in API call instead of client-side:
 * - Scalability: User with 1000+ conversations shouldn't load all to show 10
 * - Performance: Backend pagination reduces network transfer
 * - Future-proof: Backend can optimize with database indexes
 *
 * WHY clear conversations.setConversations() before fetch:
 * - Loading state: Shows empty list while fetching (prevents stale data confusion)
 * - Immediate feedback: User sees their selection had effect
 * - Prevent flicker: Alternative (show old list while loading) is jarring
 *
 * @param projectId - Project ID to filter by (null = all projects)
 */
async function loadConversations(projectId: number | null) {
	try {
		conversations.setLoading(true);
		conversations.setConversations([]); // Clear existing

		const response = await fetchConversations(projectId === null ? undefined : projectId);
		conversations.setConversations(response.conversations);
	} catch (err) {
		const errorMsg = err instanceof Error ? err.message : 'Failed to load conversations';
		conversations.setError(errorMsg);
		console.error('Failed to load conversations:', err);
	} finally {
		conversations.setLoading(false);
	}
}

/**
 * Handle project selection change
 *
 * WHY async handler instead of reactive statement:
 * - User action: Change is triggered by explicit user selection
 * - Error handling: Can catch and display errors from loadConversations
 * - Control: Prevents accidental re-fetches from other reactive updates
 */
async function handleProjectChange(event: Event) {
	const target = event.target as HTMLSelectElement;
	const value = target.value;

	// Convert "all" to null, otherwise parse as number
	selectedProjectId = value === 'all' ? null : parseInt(value, 10);

	// Load conversations for selected project
	await loadConversations(selectedProjectId);
}
</script>

<div class="project-selector-container">
	{#if isLoading}
		<!-- Loading state -->
		<div class="loading-skeleton"></div>
	{:else if error}
		<!-- Error state -->
		<div class="error-message" role="alert">
			{error}
		</div>
	{:else}
		<!-- Project selector dropdown -->
		<select
			value={selectedProjectId === null ? 'all' : selectedProjectId}
			on:change={handleProjectChange}
			class="project-select"
			aria-label="Select project"
		>
			<!-- "All Projects" option (default) -->
			<option value="all">All Projects</option>

			<!-- Individual projects -->
			{#each projects as project (project.id)}
				<option value={project.id}>
					{project.name}
					{#if project.conversation_count !== undefined}
						({project.conversation_count})
					{/if}
				</option>
			{/each}
		</select>
	{/if}
</div>

<style>
	/**
	 * Container styling
	 *
	 * WHY padding on container instead of select:
	 * - Consistent spacing: Matches other sidebar sections
	 * - Error message alignment: Error appears in same horizontal space
	 */
	.project-selector-container {
		padding: 0.5rem 0.75rem;
	}

	/**
	 * Project select dropdown
	 *
	 * Styling: Matches search input for visual consistency
	 * WHY specific height (2.5rem):
	 * - Consistent: Matches search input, new chat button
	 * - Touch-friendly: Meets minimum 44px touch target (iOS guidelines)
	 */
	.project-select {
		width: 100%;
		height: 2.5rem;
		padding: 0.5rem 0.75rem;
		border: 1px solid #e5e7eb; /* Gray 200 */
		border-radius: 0.5rem;
		font-size: 0.875rem;
		background-color: #f9fafb; /* Gray 50 */
		color: #111827; /* Gray 900 */
		cursor: pointer;
		transition: all 0.2s ease;
	}

	/**
	 * Select focus state
	 *
	 * Accessibility: Clear focus indicator for keyboard navigation
	 */
	.project-select:focus {
		outline: none;
		border-color: #3b82f6; /* Blue 500 */
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
		background-color: white;
	}

	/**
	 * Select hover state
	 *
	 * WHY subtle hover effect:
	 * - Affordance: Signals dropdown is interactive
	 * - Not too strong: Select already has visual cues (arrow icon)
	 */
	.project-select:hover {
		background-color: white;
		border-color: #d1d5db; /* Gray 300 */
	}

	/**
	 * Loading skeleton
	 *
	 * WHY skeleton instead of spinner:
	 * - Layout stability: Prevents layout shift when content loads
	 * - Better UX: Shows expected shape/size of content
	 * - Modern pattern: Facebook, LinkedIn use skeletons
	 */
	.loading-skeleton {
		width: 100%;
		height: 2.5rem;
		background: linear-gradient(
			90deg,
			#f3f4f6 25%,
			#e5e7eb 50%,
			#f3f4f6 75%
		); /* Animated gradient */
		background-size: 200% 100%;
		animation: loading 1.5s ease-in-out infinite;
		border-radius: 0.5rem;
	}

	/**
	 * Loading animation
	 *
	 * WHY animated gradient instead of static placeholder:
	 * - Feedback: User knows something is happening
	 * - Perceived performance: Feels faster than static skeleton
	 */
	@keyframes loading {
		0% {
			background-position: 200% 0;
		}
		100% {
			background-position: -200% 0;
		}
	}

	/**
	 * Error message styling
	 *
	 * WHY same styling as NewChatButton error:
	 * - Consistency: All errors look similar
	 * - Reusability: Could extract to shared component later
	 */
	.error-message {
		padding: 0.5rem;
		background-color: #fef2f2; /* Red 50 */
		color: #dc2626; /* Red 600 */
		border-radius: 0.375rem;
		font-size: 0.75rem;
		border: 1px solid #fecaca; /* Red 200 */
	}
</style>
