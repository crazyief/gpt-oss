/**
 * Projects store
 *
 * Purpose: Manage project list state, selected project, and project details
 *
 * State management strategy:
 * - Writable store for project list
 * - Selected project ID for active project
 * - Project details (conversations + documents)
 * - Helper functions for CRUD operations
 *
 * Usage:
 * import { projects, loadProjects, selectProject } from '$stores/projects';
 * await loadProjects(); // Fetch from API
 * $projects // Access reactive state in components
 */

import { writable, derived, type Readable } from 'svelte/store';
import type { Project, ProjectDetails } from '$types';
import { fetchProjects } from '$lib/services/api/projects';

/**
 * Projects store state
 *
 * Stores array of projects, selected project, and loading state
 */
interface ProjectsState {
	items: Project[];
	selectedProjectId: number | null;
	projectDetails: ProjectDetails | null;
	isLoading: boolean;
	error: string | null;
}

/**
 * Initial state for projects store
 */
const initialState: ProjectsState = {
	items: [],
	selectedProjectId: null,
	projectDetails: null,
	isLoading: false,
	error: null
};

/**
 * Writable projects store
 *
 * Core store for project list state management
 */
function createProjectsStore() {
	const { subscribe, set, update } = writable<ProjectsState>(initialState);

	return {
		subscribe,

		/**
		 * Set loading state
		 *
		 * Called when starting API request
		 */
		setLoading: (isLoading: boolean) => {
			update((state) => ({ ...state, isLoading }));
		},

		/**
		 * Set projects list
		 *
		 * Called after successful API fetch
		 *
		 * @param projects - Array of projects from API
		 */
		setProjects: (projects: Project[]) => {
			update((state) => ({ ...state, items: projects, isLoading: false, error: null }));
		},

		/**
		 * Select a project
		 *
		 * Sets the selected project ID (used for ProjectsTab UI)
		 *
		 * @param projectId - ID of project to select (or null to deselect)
		 */
		selectProject: (projectId: number | null) => {
			update((state) => ({ ...state, selectedProjectId: projectId, projectDetails: null }));
			// Sync with currentProjectId for global project consistency
			currentProjectId.set(projectId);
		},

		/**
		 * Set project details
		 *
		 * Called after fetching project details (conversations + documents)
		 *
		 * @param details - Project details from API
		 */
		setProjectDetails: (details: ProjectDetails | null) => {
			update((state) => ({ ...state, projectDetails: details }));
		},

		/**
		 * Add new project to list
		 *
		 * Called after successful project creation
		 *
		 * WHY prepend instead of append:
		 * - New projects should appear at top of list (optimistic update UX pattern)
		 * - sortedProjects derived store will re-sort automatically anyway
		 * - Prepending gives immediate visual feedback before sort runs
		 *
		 * WHY optimistic update (add before API confirms):
		 * - Faster perceived performance: UI updates instantly
		 * - If API fails, calling component should removeProject() to rollback
		 * - Trade-off: Better UX vs. potential inconsistency on failure
		 *
		 * @param project - Newly created project
		 */
		addProject: (project: Project) => {
			update((state) => ({
				...state,
				items: [project, ...state.items] // Prepend new project
			}));
		},

		/**
		 * Update existing project
		 *
		 * Called after successful project update
		 *
		 * WHY use map() instead of finding and mutating:
		 * - Immutability: Creates new array, preserves original state
		 * - Svelte reactivity: New array reference triggers subscriber updates
		 * - Predictability: No side effects, easier to debug and test
		 *
		 * WHY Partial<Project> type:
		 * - Allows updating only changed fields (e.g., just title or description)
		 * - Prevents accidentally overwriting unrelated fields with undefined
		 * - Type safety: TypeScript ensures only valid Project fields are passed
		 *
		 * @param projectId - ID of project to update
		 * @param updates - Partial project data to merge
		 */
		updateProject: (projectId: number, updates: Partial<Project>) => {
			update((state) => ({
				...state,
				items: state.items.map((p) => (p.id === projectId ? { ...p, ...updates } : p)),
				// Also update projectDetails if this is the selected project
				projectDetails:
					state.projectDetails && state.projectDetails.project.id === projectId
						? { ...state.projectDetails, project: { ...state.projectDetails.project, ...updates } }
						: state.projectDetails
			}));
		},

		/**
		 * Remove project from list
		 *
		 * Called after successful project deletion
		 *
		 * @param projectId - ID of project to remove
		 */
		removeProject: (projectId: number) => {
			update((state) => ({
				...state,
				items: state.items.filter((p) => p.id !== projectId),
				// Clear selection if deleted project was selected
				selectedProjectId: state.selectedProjectId === projectId ? null : state.selectedProjectId,
				projectDetails: state.selectedProjectId === projectId ? null : state.projectDetails
			}));
		},

		/**
		 * Reorder projects
		 *
		 * Updates the items array with new sort order
		 *
		 * @param orderedProjects - Projects in new order
		 */
		reorderProjects: (orderedProjects: Project[]) => {
			update((state) => ({ ...state, items: orderedProjects }));
		},

		/**
		 * Set error state
		 *
		 * Called when API request fails
		 *
		 * @param error - Error message
		 */
		setError: (error: string) => {
			update((state) => ({ ...state, error, isLoading: false }));
		},

		/**
		 * Clear error state
		 *
		 * Called to dismiss error message
		 */
		clearError: () => {
			update((state) => ({ ...state, error: null }));
		},

		/**
		 * Reset store to initial state
		 *
		 * Called on logout or navigation away
		 */
		reset: () => {
			set(initialState);
		}
	};
}

/**
 * Projects store instance
 *
 * Use this store in components for project state
 */
export const projects = createProjectsStore();

/**
 * Load projects from API into store
 *
 * Fetches project list and populates store. Called by components on mount.
 */
export async function loadProjects(): Promise<void> {
	projects.setLoading(true);
	try {
		const response = await fetchProjects();
		projects.setProjects(response.projects);
	} catch (error) {
		projects.setError(error instanceof Error ? error.message : 'Failed to load projects');
	}
}

/**
 * Derived store: sorted projects
 *
 * Returns projects sorted by last_used_at (most recent first), with Default project always last
 *
 * WHY use derived store instead of sorting manually:
 * - Automatic reactivity: Any change to $projects triggers re-sort automatically
 * - Prevents bugs: No need to remember to sort after addProject/updateProject/removeProject
 * - Performance: Svelte only recalculates when $projects.items changes (referential equality check)
 * - Separation of concerns: Components consume sorted data without managing sort logic
 *
 * WHY spread operator [...$projects.items]:
 * - Array.sort() mutates in place, spreading creates new array to preserve immutability
 * - Prevents unexpected side effects in components subscribed to $projects
 *
 * Usage:
 * import { sortedProjects } from '$stores/projects';
 * {#each $sortedProjects as project}...{/each}
 */
export const sortedProjects: Readable<Project[]> = derived(projects, ($projects) => {
	const items = [...$projects.items];

	// Separate default project from others
	const defaultProject = items.find((p) => p.is_default);
	const userProjects = items.filter((p) => !p.is_default);

	// Sort user projects by last_used_at (newest first) or created_at
	userProjects.sort((a, b) => {
		const aDate = a.last_used_at || a.created_at;
		const bDate = b.last_used_at || b.created_at;
		return new Date(bDate).getTime() - new Date(aDate).getTime();
	});

	// Return with Default project at the end
	return defaultProject ? [...userProjects, defaultProject] : userProjects;
});

/**
 * Current project ID store
 *
 * Purpose: Track currently selected project for filtering and new conversation creation
 *
 * null = "All Projects" (no filter)
 * number = Specific project selected
 *
 * WHY separate store instead of component state:
 * - Shared state: ProjectSelector and NewChatButton both need this value
 * - ProjectSelector updates it when user selects project
 * - NewChatButton reads it when creating new conversation
 * - Centralized: Single source of truth for selected project
 *
 * Usage:
 * import { currentProjectId } from '$stores/projects';
 * currentProjectId.set(5); // Select project 5
 * currentProjectId.set(null); // Select "All Projects"
 * $currentProjectId // Read current value in component
 */
export const currentProjectId = writable<number | null>(null);
