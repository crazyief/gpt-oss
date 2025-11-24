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

import { onMount, onDestroy } from 'svelte';
import { writable, type Unsubscriber } from 'svelte/store';
import type { Project } from '$lib/types';
import { conversations } from '$lib/stores/conversations';
import { currentProjectId } from '$lib/stores/projects';
import { projects as projectsApi, conversations as conversationsApi } from '$lib/services/api';
import { logger } from '$lib/utils/logger';

// Component state
let projects: Project[] = [];
let isLoading = true;
let error: string | null = null;
let unsubscribe: Unsubscriber;
let deletingProjectId: number | null = null;
let showDeleteConfirm = false;

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
/**
 * Load projects from API
 *
 * WHY separate function instead of inline in onMount:
 * - Reusability: Can refresh projects after conversation changes
 * - Testability: Easier to test
 */
async function loadProjects() {
	try {
		const response = await projectsApi.fetchProjects();
		projects = response.projects;
	} catch (err) {
		error = err instanceof Error ? err.message : 'Failed to load projects';
		logger.error('Failed to load projects', { error: err });
	}
}

onMount(async () => {
	try {
		isLoading = true;
		await loadProjects();

		// Load all conversations by default (selectedProjectId = null)
		await loadConversations(null);
	} catch (err) {
		error = err instanceof Error ? err.message : 'Failed to load projects';
		logger.error('Failed to load projects on mount', { error: err });
	} finally {
		isLoading = false;
	}
});

/**
 * Refresh projects when conversation count changes
 *
 * WHY subscribe to conversations store:
 * - Auto-update: Project conversation counts update when conversations added/deleted
 * - No manual refresh: User doesn't have to reload page
 * - Consistency: UI always shows accurate counts
 *
 * WHY track previousCount:
 * - Prevents infinite loop: Only refresh when count actually changes
 * - Performance: Avoid unnecessary API calls
 */
let previousConversationCount = 0;
unsubscribe = conversations.subscribe((state) => {
	const currentCount = state.items.length;

	// Refresh project list when conversation count changes
	// Skip during initial load (isLoading = true)
	if (!isLoading && projects.length > 0 && currentCount !== previousConversationCount) {
		previousConversationCount = currentCount;
		loadProjects();
	}
});

/**
 * Cleanup subscription on component destroy
 *
 * WHY necessary:
 * - Memory leak prevention: Unsubscribe to avoid keeping component in memory
 * - Svelte best practice: Always clean up subscriptions
 */
onDestroy(() => {
	if (unsubscribe) {
		unsubscribe();
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

		if (projectId !== null) {
			const convList = await conversationsApi.getConversations(projectId);
			conversations.setConversations(convList);
		}
	} catch (err) {
		const errorMsg = err instanceof Error ? err.message : 'Failed to load conversations';
		conversations.setError(errorMsg);
		logger.error('Failed to load conversations', { projectId, error: err });
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
 *
 * WHY update currentProjectId store:
 * - Shared state: NewChatButton needs to know selected project
 * - Creates conversation in correct project
 * - Single source of truth: Store persists across component updates
 */
async function handleProjectChange(event: Event) {
	const target = event.target as HTMLSelectElement;
	const value = target.value;

	// Convert "all" to null, otherwise parse as number
	const projectId = value === 'all' ? null : parseInt(value, 10);

	// Update global store (used by NewChatButton)
	currentProjectId.set(projectId);

	// Load conversations for selected project
	await loadConversations(projectId);
}

/**
 * Handle project deletion
 *
 * WHY confirmation required:
 * - Destructive action: Cannot be undone
 * - Data safety: Prevents accidental deletion
 * - User intent: Requires explicit confirmation
 *
 * @param projectId - Project ID to delete
 */
async function handleDeleteProject(projectId: number) {
	const project = projects.find((p) => p.id === projectId);
	if (!project) return;

	// Show confirmation
	const confirmed = confirm(`Are you sure you want to delete project "${project.name}"?\n\nThis will NOT delete the conversations in this project, but they will be moved to the default project.`);

	if (!confirmed) return;

	try {
		deletingProjectId = projectId;

		// Delete project via API
		await projectsApi.deleteProject(projectId);

		// If currently viewing this project, switch to "All Projects"
		if ($currentProjectId === projectId) {
			currentProjectId.set(null);
			await loadConversations(null);
		}

		// Refresh project list
		await loadProjects();

		logger.info('Project deleted successfully', { projectId });
	} catch (err) {
		logger.error('Failed to delete project', { projectId, error: err });
		error = err instanceof Error ? err.message : 'Failed to delete project';

		// Clear error after 3 seconds
		setTimeout(() => {
			error = null;
		}, 3000);
	} finally {
		deletingProjectId = null;
	}
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
		<!-- Project selector with delete button -->
		<div class="project-selector-row">
			<select
				value={$currentProjectId === null ? 'all' : $currentProjectId}
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

			<!-- Delete button (only show when specific project selected) -->
			{#if $currentProjectId !== null}
				<button
					type="button"
					on:click={() => handleDeleteProject($currentProjectId)}
					disabled={deletingProjectId !== null}
					class="delete-project-button"
					aria-label="Delete current project"
					title="Delete project"
				>
					{#if deletingProjectId === $currentProjectId}
						<!-- Loading spinner -->
						<svg class="spinner" width="16" height="16" viewBox="0 0 16 16">
							<circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="30" stroke-linecap="round">
								<animateTransform attributeName="transform" type="rotate" from="0 8 8" to="360 8 8" dur="1s" repeatCount="indefinite"/>
							</circle>
						</svg>
					{:else}
						<!-- Trash icon -->
						<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M3 4h10M6 4V3a1 1 0 011-1h2a1 1 0 011 1v1M5 7v5M8 7v5M11 7v5M4 4h8v9a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					{/if}
				</button>
			{/if}
		</div>
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
	 * Project selector row (select + delete button)
	 *
	 * WHY flexbox layout:
	 * - Side-by-side: Select and delete button in same row
	 * - Flexible: Select grows to fill space, button stays fixed
	 */
	.project-selector-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
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
		flex: 1;
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
	 * Delete project button
	 *
	 * WHY red color:
	 * - Destructive action: Indicates dangerous operation
	 * - Attention: User notices before clicking
	 * - Convention: Delete buttons typically red
	 */
	.delete-project-button {
		flex-shrink: 0;
		width: 2.5rem;
		height: 2.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0;
		border: 1px solid #fecaca; /* Red 200 */
		border-radius: 0.5rem;
		background-color: #fee2e2; /* Red 100 */
		color: #dc2626; /* Red 600 */
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.delete-project-button:hover:not(:disabled) {
		background-color: #fecaca; /* Red 200 */
		border-color: #fca5a5; /* Red 300 */
		transform: scale(1.05);
	}

	.delete-project-button:active:not(:disabled) {
		transform: scale(0.95);
	}

	.delete-project-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.delete-project-button .spinner {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
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
