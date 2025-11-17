/**
 * Projects store
 *
 * Purpose: Manage project list state
 *
 * State management strategy:
 * - Writable store for project list
 * - Derived store for filtering/sorting
 * - Helper functions for CRUD operations
 *
 * Usage:
 * import { projects, loadProjects } from '$stores/projects';
 * await loadProjects(); // Fetch from API
 * $projects // Access reactive state in components
 */

import { writable, derived, type Readable } from 'svelte/store';
import type { Project } from '$types';

/**
 * Projects store state
 *
 * Stores array of projects and loading state
 */
interface ProjectsState {
	items: Project[];
	isLoading: boolean;
	error: string | null;
}

/**
 * Initial state for projects store
 */
const initialState: ProjectsState = {
	items: [],
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
			set({ items: projects, isLoading: false, error: null });
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
				items: state.items.map((p) => (p.id === projectId ? { ...p, ...updates } : p))
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
				items: state.items.filter((p) => p.id !== projectId)
			}));
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
 * Derived store: sorted projects
 *
 * Returns projects sorted by created_at (newest first)
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
export const sortedProjects: Readable<Project[]> = derived(projects, ($projects) =>
	[...$projects.items].sort(
		(a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
	)
);
