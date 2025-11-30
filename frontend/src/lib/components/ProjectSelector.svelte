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
import { API_ENDPOINTS } from '$lib/config';
import { logger } from '$lib/utils/logger';

// Component state
let projects: Project[] = [];
let isLoading = true;
let error: string | null = null;
let unsubscribe: Unsubscriber;

// Refresh projects when currentProjectId changes to a project not in our list
// This handles the case when a new project is created externally
$: if ($currentProjectId !== null && !isLoading && projects.length > 0) {
	const projectExists = projects.some(p => p.id === $currentProjectId);
	if (!projectExists) {
		loadProjects();
	}
}

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

		// Get default project and select it
		// WHY default project instead of "All Projects":
		// - User can immediately create new chats
		// - Matches ChatGPT/Claude UX where you're always in a workspace
		// - "All Projects" is a filter view, not the default working context
		const defaultProject = await projectsApi.fetchDefaultProject();
		currentProjectId.set(defaultProject.id);

		// Load conversations for default project
		await loadConversations(defaultProject.id);
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
		<!-- Project selector -->
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
	{/if}
</div>

<style>
	/* Container: fills available space in project-row */
	.project-selector-container {
		flex: 1;
		min-width: 0;
	}

	/* Select: theme-aware, full width */
	.project-select {
		width: 100%;
		height: 2.5rem;
		padding: 0.5rem 0.75rem;
		border: 1px solid var(--border-primary);
		border-radius: 0.5rem;
		font-size: 0.875rem;
		background-color: var(--bg-tertiary);
		color: var(--text-primary);
		cursor: pointer;
		transition: all 0.2s ease;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.project-select:focus {
		outline: none;
		border-color: var(--accent);
		box-shadow: 0 0 0 3px var(--accent-muted);
		background-color: var(--bg-input);
	}

	.project-select:hover {
		background-color: var(--bg-hover);
		border-color: var(--accent);
	}

	.project-select option {
		background-color: var(--bg-secondary);
		color: var(--text-primary);
	}

	/* Loading skeleton */
	.loading-skeleton {
		width: 100%;
		height: 2.5rem;
		background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-secondary) 50%, var(--bg-tertiary) 75%);
		background-size: 200% 100%;
		animation: loading 1.5s ease-in-out infinite;
		border-radius: 0.5rem;
	}

	@keyframes loading {
		0% { background-position: 200% 0; }
		100% { background-position: -200% 0; }
	}

	/* Error message */
	.error-message {
		padding: 0.5rem;
		background-color: rgba(239, 68, 68, 0.1);
		color: var(--error);
		border-radius: 0.375rem;
		font-size: 0.75rem;
		border: 1px solid var(--error);
	}
</style>
