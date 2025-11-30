/**
 * Projects API client
 *
 * Handles all project-related API operations (CRUD + statistics).
 * All functions use shared apiRequest wrapper with automatic error handling.
 */

import { apiRequest } from './base';
import { API_ENDPOINTS } from '$lib/config';
import { toast } from '$lib/stores/toast';
import type { Project, ProjectListResponse, ProjectStats } from '$lib/types';

/**
 * Fetch all projects.
 *
 * @returns Promise<ProjectListResponse> - List of all projects with metadata
 * @throws Error if API call fails
 *
 * @example
 * const response = await fetchProjects();
 * console.log(`Found ${response.projects.length} projects`);
 */
export async function fetchProjects(): Promise<ProjectListResponse> {
	return apiRequest<ProjectListResponse>(API_ENDPOINTS.projects.list);
}

/**
 * Fetch the default project.
 *
 * Gets the oldest project or creates a "Default Project" if none exist.
 * Used on initial page load to ensure there's always a project selected.
 *
 * @returns Promise<Project> - The default project
 * @throws Error if API call fails
 *
 * @example
 * const defaultProject = await fetchDefaultProject();
 * currentProjectId.set(defaultProject.id);
 */
export async function fetchDefaultProject(): Promise<Project> {
	return apiRequest<Project>(API_ENDPOINTS.projects.default);
}

/**
 * Fetch single project by ID.
 *
 * @param id - Project ID
 * @returns Promise<Project> - The project data
 * @throws Error if project not found or API call fails
 *
 * @example
 * const project = await fetchProject(123);
 * console.log(project.name);
 */
export async function fetchProject(id: number): Promise<Project> {
	return apiRequest<Project>(API_ENDPOINTS.projects.get(id));
}

/**
 * Create new project.
 *
 * @param name - Project name (required)
 * @param description - Project description (optional)
 * @returns Promise<Project> - The created project
 * @throws Error if validation fails or API call fails
 *
 * @example
 * const project = await createProject('IEC 62443 Analysis', 'Security standards review');
 */
export async function createProject(name: string, description?: string): Promise<Project> {
	const project = await apiRequest<Project>(API_ENDPOINTS.projects.create, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			name,
			description: description || null
		})
	});

	// Show success toast
	toast.success('Project created successfully');

	return project;
}

/**
 * Update existing project.
 *
 * @param id - Project ID
 * @param data - Partial project data to update (name, description, color, icon)
 * @returns Promise<Project> - The updated project
 * @throws Error if project not found or API call fails
 *
 * @example
 * const project = await updateProject(123, { name: 'New Project Name', color: 'blue', icon: 'folder' });
 */
export async function updateProject(
	id: number,
	data: Partial<Pick<Project, 'name' | 'description' | 'color' | 'icon'>>
): Promise<Project> {
	const project = await apiRequest<Project>(API_ENDPOINTS.projects.update(id), {
		method: 'PATCH',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});

	// Show success toast
	toast.success('Project updated successfully');

	return project;
}

/**
 * Delete project by ID with action (move or delete).
 *
 * @param id - Project ID to delete
 * @param action - What to do with project data: 'move' (to Default) or 'delete' (permanently)
 * @returns Promise<void> - Resolves when deletion completes
 * @throws Error if project not found or API call fails
 *
 * @example
 * await deleteProject(123, 'move'); // Move data to Default project
 * await deleteProject(123, 'delete'); // Delete all data permanently
 */
export async function deleteProject(id: number, action: 'move' | 'delete' = 'move'): Promise<void> {
	await apiRequest<void>(`${API_ENDPOINTS.projects.delete(id)}?action=${action}`, {
		method: 'DELETE'
	});

	// Show success toast
	toast.success('Project deleted successfully');
}

/**
 * Get project statistics (document count, message count, etc.).
 *
 * @param id - Project ID
 * @returns Promise<ProjectStats> - Aggregated statistics for the project
 * @throws Error if project not found or API call fails
 *
 * @example
 * const stats = await getProjectStats(123);
 * console.log(`Documents: ${stats.document_count}, Messages: ${stats.message_count}`);
 */
export async function getProjectStats(id: number): Promise<ProjectStats> {
	return apiRequest<ProjectStats>(API_ENDPOINTS.projects.stats(id));
}

/**
 * Stage 3: Get project details (project + conversations + documents)
 *
 * @param id - Project ID
 * @returns Promise<ProjectDetails> - Project with conversations and documents
 * @throws Error if project not found or API call fails
 *
 * @example
 * const details = await getProjectDetails(123);
 * console.log(`Project has ${details.conversations.length} conversations`);
 */
export async function getProjectDetails(id: number): Promise<import('$types').ProjectDetails> {
	return apiRequest<import('$types').ProjectDetails>(API_ENDPOINTS.projects.details(id));
}

/**
 * Stage 3: Reorder projects
 *
 * @param projectIds - Array of project IDs in new order
 * @returns Promise<void>
 * @throws Error if API call fails
 *
 * @example
 * await reorderProjects([3, 1, 2]); // Reorder projects
 */
export async function reorderProjects(projectIds: number[]): Promise<void> {
	await apiRequest<void>(API_ENDPOINTS.projects.reorder, {
		method: 'PATCH',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ project_ids: projectIds })
	});
}
