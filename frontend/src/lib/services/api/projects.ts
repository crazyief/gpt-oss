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
 * @param data - Partial project data to update (name and/or description)
 * @returns Promise<Project> - The updated project
 * @throws Error if project not found or API call fails
 *
 * @example
 * const project = await updateProject(123, { name: 'New Project Name' });
 */
export async function updateProject(
	id: number,
	data: Partial<Pick<Project, 'name' | 'description'>>
): Promise<Project> {
	const project = await apiRequest<Project>(API_ENDPOINTS.projects.get(id), {
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
 * Delete project by ID (cascade deletes conversations/messages).
 *
 * @param id - Project ID to delete
 * @returns Promise<void> - Resolves when deletion completes
 * @throws Error if project not found or API call fails
 *
 * @example
 * await deleteProject(123);
 */
export async function deleteProject(id: number): Promise<void> {
	await apiRequest<void>(API_ENDPOINTS.projects.delete(id), {
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
