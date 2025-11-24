/**
 * Unit tests for projects.ts - Projects API client
 *
 * Test coverage:
 * - createProject function (5 tests)
 * - fetchProjects function (4 tests)
 * - fetchProject function (4 tests)
 * - updateProject function (5 tests)
 * - deleteProject function (4 tests)
 * - getProjectStats function (3 tests)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
	createProject,
	fetchProjects,
	fetchProject,
	updateProject,
	deleteProject,
	getProjectStats,
	type ProjectStats
} from './projects';
import { API_ENDPOINTS } from '$lib/config';
import type { Project, ProjectListResponse } from '$lib/types';
import * as toastStore from '$lib/stores/toast';

// Mock dependencies
vi.mock('./base', () => ({
	apiRequest: vi.fn()
}));

vi.mock('$lib/stores/toast', () => ({
	toast: {
		error: vi.fn(),
		success: vi.fn(),
		info: vi.fn()
	}
}));

import { apiRequest } from './base';

describe('projects.ts - createProject', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('sends POST request to /api/projects/create', async () => {
		const mockProject: Project = {
			id: 1,
			name: 'Test Project',
			description: null,
			created_at: '2025-11-24T00:00:00Z',
			updated_at: '2025-11-24T00:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockProject);

		await createProject('Test Project');

		expect(apiRequest).toHaveBeenCalledWith(API_ENDPOINTS.projects.create, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				name: 'Test Project',
				description: null
			})
		});
	});

	it('includes name in request body', async () => {
		const mockProject: Project = {
			id: 1,
			name: 'IEC 62443 Analysis',
			description: null,
			created_at: '2025-11-24T00:00:00Z',
			updated_at: '2025-11-24T00:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockProject);

		await createProject('IEC 62443 Analysis');

		const callArgs = vi.mocked(apiRequest).mock.calls[0];
		const body = JSON.parse(callArgs[1]?.body as string);
		expect(body.name).toBe('IEC 62443 Analysis');
	});

	it('includes optional description in request body', async () => {
		const mockProject: Project = {
			id: 1,
			name: 'Test Project',
			description: 'Security standards review',
			created_at: '2025-11-24T00:00:00Z',
			updated_at: '2025-11-24T00:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockProject);

		await createProject('Test Project', 'Security standards review');

		const callArgs = vi.mocked(apiRequest).mock.calls[0];
		const body = JSON.parse(callArgs[1]?.body as string);
		expect(body.description).toBe('Security standards review');
	});

	it('returns created project data', async () => {
		const mockProject: Project = {
			id: 123,
			name: 'New Project',
			description: 'Test description',
			created_at: '2025-11-24T12:00:00Z',
			updated_at: '2025-11-24T12:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockProject);

		const result = await createProject('New Project', 'Test description');

		expect(result).toEqual(mockProject);
		expect(result.id).toBe(123);
		expect(result.name).toBe('New Project');
	});

	it('shows success toast after creation', async () => {
		const mockProject: Project = {
			id: 1,
			name: 'Test Project',
			description: null,
			created_at: '2025-11-24T00:00:00Z',
			updated_at: '2025-11-24T00:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockProject);

		await createProject('Test Project');

		expect(toastStore.toast.success).toHaveBeenCalledWith('Project created successfully');
	});
});

describe('projects.ts - fetchProjects', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('sends GET request to /api/projects', async () => {
		const mockResponse: ProjectListResponse = {
			projects: [],
			total_count: 0
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockResponse);

		await fetchProjects();

		expect(apiRequest).toHaveBeenCalledWith(API_ENDPOINTS.projects.list);
	});

	it('returns array of projects', async () => {
		const mockProjects: Project[] = [
			{
				id: 1,
				name: 'Project 1',
				description: null,
				created_at: '2025-11-24T00:00:00Z',
				updated_at: '2025-11-24T00:00:00Z',
				conversation_count: 5
			},
			{
				id: 2,
				name: 'Project 2',
				description: 'Description 2',
				created_at: '2025-11-24T01:00:00Z',
				updated_at: '2025-11-24T01:00:00Z',
				conversation_count: 3
			}
		];

		const mockResponse: ProjectListResponse = {
			projects: mockProjects,
			total_count: 2
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockResponse);

		const result = await fetchProjects();

		expect(result.projects).toHaveLength(2);
		expect(result.projects[0].name).toBe('Project 1');
		expect(result.total_count).toBe(2);
	});

	it('returns empty array when no projects', async () => {
		const mockResponse: ProjectListResponse = {
			projects: [],
			total_count: 0
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockResponse);

		const result = await fetchProjects();

		expect(result.projects).toEqual([]);
		expect(result.total_count).toBe(0);
	});

	it('throws error on API failure', async () => {
		vi.mocked(apiRequest).mockRejectedValueOnce(new Error('Network error'));

		await expect(fetchProjects()).rejects.toThrow('Network error');
	});
});

describe('projects.ts - fetchProject', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('sends GET request to /api/projects/{id}', async () => {
		const mockProject: Project = {
			id: 123,
			name: 'Test Project',
			description: null,
			created_at: '2025-11-24T00:00:00Z',
			updated_at: '2025-11-24T00:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockProject);

		await fetchProject(123);

		expect(apiRequest).toHaveBeenCalledWith(API_ENDPOINTS.projects.get(123));
	});

	it('returns single project data', async () => {
		const mockProject: Project = {
			id: 456,
			name: 'IEC 62443 Project',
			description: 'Security standards analysis',
			created_at: '2025-11-24T10:00:00Z',
			updated_at: '2025-11-24T12:00:00Z',
			conversation_count: 15
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockProject);

		const result = await fetchProject(456);

		expect(result).toEqual(mockProject);
		expect(result.id).toBe(456);
		expect(result.name).toBe('IEC 62443 Project');
	});

	it('throws error on 404 Not Found', async () => {
		vi.mocked(apiRequest).mockRejectedValueOnce(new Error('Resource not found'));

		await expect(fetchProject(999)).rejects.toThrow('Resource not found');
	});

	it('throws error on API failure', async () => {
		vi.mocked(apiRequest).mockRejectedValueOnce(new Error('Server error'));

		await expect(fetchProject(123)).rejects.toThrow('Server error');
	});
});

describe('projects.ts - updateProject', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('sends PATCH request to /api/projects/{id}', async () => {
		const mockProject: Project = {
			id: 123,
			name: 'Updated Project',
			description: null,
			created_at: '2025-11-24T00:00:00Z',
			updated_at: '2025-11-24T12:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockProject);

		await updateProject(123, { name: 'Updated Project' });

		expect(apiRequest).toHaveBeenCalledWith(API_ENDPOINTS.projects.get(123), {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ name: 'Updated Project' })
		});
	});

	it('includes updated name in request body', async () => {
		const mockProject: Project = {
			id: 123,
			name: 'New Name',
			description: null,
			created_at: '2025-11-24T00:00:00Z',
			updated_at: '2025-11-24T12:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockProject);

		await updateProject(123, { name: 'New Name' });

		const callArgs = vi.mocked(apiRequest).mock.calls[0];
		const body = JSON.parse(callArgs[1]?.body as string);
		expect(body.name).toBe('New Name');
	});

	it('includes updated description in request body', async () => {
		const mockProject: Project = {
			id: 123,
			name: 'Project Name',
			description: 'New description',
			created_at: '2025-11-24T00:00:00Z',
			updated_at: '2025-11-24T12:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockProject);

		await updateProject(123, { description: 'New description' });

		const callArgs = vi.mocked(apiRequest).mock.calls[0];
		const body = JSON.parse(callArgs[1]?.body as string);
		expect(body.description).toBe('New description');
	});

	it('returns updated project data', async () => {
		const mockProject: Project = {
			id: 123,
			name: 'Updated Project',
			description: 'Updated description',
			created_at: '2025-11-24T00:00:00Z',
			updated_at: '2025-11-24T12:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockProject);

		const result = await updateProject(123, {
			name: 'Updated Project',
			description: 'Updated description'
		});

		expect(result).toEqual(mockProject);
		expect(result.name).toBe('Updated Project');
		expect(result.description).toBe('Updated description');
	});

	it('shows success toast after update', async () => {
		const mockProject: Project = {
			id: 123,
			name: 'Updated Project',
			description: null,
			created_at: '2025-11-24T00:00:00Z',
			updated_at: '2025-11-24T12:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockProject);

		await updateProject(123, { name: 'Updated Project' });

		expect(toastStore.toast.success).toHaveBeenCalledWith('Project updated successfully');
	});
});

describe('projects.ts - deleteProject', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('sends DELETE request to /api/projects/{id}', async () => {
		vi.mocked(apiRequest).mockResolvedValueOnce(undefined);

		await deleteProject(123);

		expect(apiRequest).toHaveBeenCalledWith(API_ENDPOINTS.projects.delete(123), {
			method: 'DELETE'
		});
	});

	it('shows success toast after deletion', async () => {
		vi.mocked(apiRequest).mockResolvedValueOnce(undefined);

		await deleteProject(123);

		expect(toastStore.toast.success).toHaveBeenCalledWith('Project deleted successfully');
	});

	it('throws error on 404 Not Found', async () => {
		vi.mocked(apiRequest).mockRejectedValueOnce(new Error('Resource not found'));

		await expect(deleteProject(999)).rejects.toThrow('Resource not found');
	});

	it('throws error on API failure', async () => {
		vi.mocked(apiRequest).mockRejectedValueOnce(new Error('Server error'));

		await expect(deleteProject(123)).rejects.toThrow('Server error');
	});
});

describe('projects.ts - getProjectStats', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('sends GET request to /api/projects/{id}/stats', async () => {
		const mockStats: ProjectStats = {
			project_id: 123,
			document_count: 10,
			conversation_count: 5,
			message_count: 50,
			total_tokens: 1000
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockStats);

		await getProjectStats(123);

		expect(apiRequest).toHaveBeenCalledWith('/api/projects/123/stats');
	});

	it('returns project statistics', async () => {
		const mockStats: ProjectStats = {
			project_id: 456,
			document_count: 25,
			conversation_count: 12,
			message_count: 150,
			total_tokens: 50000
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockStats);

		const result = await getProjectStats(456);

		expect(result).toEqual(mockStats);
		expect(result.project_id).toBe(456);
		expect(result.document_count).toBe(25);
		expect(result.message_count).toBe(150);
		expect(result.total_tokens).toBe(50000);
	});

	it('throws error on API failure', async () => {
		vi.mocked(apiRequest).mockRejectedValueOnce(new Error('Project not found'));

		await expect(getProjectStats(999)).rejects.toThrow('Project not found');
	});
});
