/**
 * Unit tests for projects store
 *
 * Tests: State mutations, CRUD operations, derived stores, error handling
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { projects, sortedProjects, currentProjectId } from './projects';
import type { Project } from '$lib/types';

describe('projects store', () => {
	beforeEach(() => {
		projects.reset();
		currentProjectId.set(null);
	});

	describe('initial state', () => {
		it('should start with empty items', () => {
			const state = get(projects);
			expect(state.items).toEqual([]);
		});

		it('should have loading = false initially', () => {
			const state = get(projects);
			expect(state.isLoading).toBe(false);
		});

		it('should have no error initially', () => {
			const state = get(projects);
			expect(state.error).toBeNull();
		});
	});

	describe('setLoading', () => {
		it('should set loading to true', () => {
			projects.setLoading(true);
			const state = get(projects);
			expect(state.isLoading).toBe(true);
		});

		it('should set loading to false', () => {
			projects.setLoading(true);
			projects.setLoading(false);
			const state = get(projects);
			expect(state.isLoading).toBe(false);
		});
	});

	describe('setProjects', () => {
		it('should set projects array', () => {
			const testProjects: Project[] = [
				{
					id: 1,
					name: 'Test Project',
					description: 'Description',
					created_at: '2025-01-01T00:00:00Z',
					updated_at: '2025-01-01T00:00:00Z',
					conversation_count: 0,
					document_count: 0
				}
			];

			projects.setProjects(testProjects);
			const state = get(projects);
			expect(state.items).toEqual(testProjects);
		});

		it('should clear loading and error when setting projects', () => {
			projects.setLoading(true);
			projects.setError('Test error');

			const testProjects: Project[] = [];
			projects.setProjects(testProjects);

			const state = get(projects);
			expect(state.isLoading).toBe(false);
			expect(state.error).toBeNull();
		});
	});

	describe('addProject', () => {
		it('should add project to items', () => {
			const project: Project = {
				id: 1,
				name: 'New Project',
				description: 'Description',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			projects.addProject(project);
			const state = get(projects);
			expect(state.items).toHaveLength(1);
			expect(state.items[0]).toEqual(project);
		});

		it('should prepend new project (optimistic update pattern)', () => {
			const project1: Project = {
				id: 1,
				name: 'First',
				description: '',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			const project2: Project = {
				id: 2,
				name: 'Second',
				description: '',
				created_at: '2025-01-01T01:00:00Z',
				updated_at: '2025-01-01T01:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			projects.addProject(project1);
			projects.addProject(project2);

			const state = get(projects);
			expect(state.items).toHaveLength(2);
			expect(state.items[0]).toEqual(project2); // Latest first
		});
	});

	describe('updateProject', () => {
		it('should update project by id', () => {
			const project: Project = {
				id: 1,
				name: 'Original Name',
				description: 'Original Description',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			projects.addProject(project);
			projects.updateProject(1, { name: 'Updated Name' });

			const state = get(projects);
			expect(state.items[0].name).toBe('Updated Name');
			expect(state.items[0].description).toBe('Original Description'); // Other fields unchanged
		});

		it('should not update projects with different id', () => {
			const project: Project = {
				id: 1,
				name: 'Test Project',
				description: 'Description',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			projects.addProject(project);
			projects.updateProject(999, { name: 'Should Not Update' });

			const state = get(projects);
			expect(state.items[0].name).toBe('Test Project');
		});
	});

	describe('removeProject', () => {
		it('should remove project by id', () => {
			const project: Project = {
				id: 1,
				name: 'To Remove',
				description: '',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			projects.addProject(project);
			projects.removeProject(1);

			const state = get(projects);
			expect(state.items).toHaveLength(0);
		});

		it('should not remove projects with different id', () => {
			const project: Project = {
				id: 1,
				name: 'Keep Me',
				description: '',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			projects.addProject(project);
			projects.removeProject(999);

			const state = get(projects);
			expect(state.items).toHaveLength(1);
		});
	});

	describe('error handling', () => {
		it('should set error message', () => {
			projects.setError('Test error');

			const state = get(projects);
			expect(state.error).toBe('Test error');
			expect(state.isLoading).toBe(false);
		});

		it('should clear error message', () => {
			projects.setError('Test error');
			projects.clearError();

			const state = get(projects);
			expect(state.error).toBeNull();
		});
	});

	describe('reset', () => {
		it('should reset to initial state', () => {
			const project: Project = {
				id: 1,
				name: 'Test',
				description: '',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			projects.addProject(project);
			projects.setLoading(true);
			projects.setError('Error');

			projects.reset();

			const state = get(projects);
			expect(state.items).toEqual([]);
			expect(state.isLoading).toBe(false);
			expect(state.error).toBeNull();
		});
	});

	describe('sortedProjects derived store', () => {
		it('should sort projects by created_at (newest first)', () => {
			const project1: Project = {
				id: 1,
				name: 'Oldest',
				description: '',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			const project2: Project = {
				id: 2,
				name: 'Newest',
				description: '',
				created_at: '2025-01-03T00:00:00Z',
				updated_at: '2025-01-03T00:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			const project3: Project = {
				id: 3,
				name: 'Middle',
				description: '',
				created_at: '2025-01-02T00:00:00Z',
				updated_at: '2025-01-02T00:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			projects.addProject(project1);
			projects.addProject(project2);
			projects.addProject(project3);

			const sorted = get(sortedProjects);
			expect(sorted).toHaveLength(3);
			expect(sorted[0].name).toBe('Newest');
			expect(sorted[1].name).toBe('Middle');
			expect(sorted[2].name).toBe('Oldest');
		});

		it('should update automatically when projects change', () => {
			const project1: Project = {
				id: 1,
				name: 'First',
				description: '',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			projects.addProject(project1);
			let sorted = get(sortedProjects);
			expect(sorted).toHaveLength(1);

			const project2: Project = {
				id: 2,
				name: 'Second',
				description: '',
				created_at: '2025-01-02T00:00:00Z',
				updated_at: '2025-01-02T00:00:00Z',
				conversation_count: 0,
				document_count: 0
			};

			projects.addProject(project2);
			sorted = get(sortedProjects);
			expect(sorted).toHaveLength(2);
			expect(sorted[0].name).toBe('Second');
		});
	});

	describe('currentProjectId store', () => {
		it('should start as null', () => {
			const id = get(currentProjectId);
			expect(id).toBeNull();
		});

		it('should update when set', () => {
			currentProjectId.set(42);
			const id = get(currentProjectId);
			expect(id).toBe(42);
		});

		it('should support null (All Projects)', () => {
			currentProjectId.set(5);
			currentProjectId.set(null);
			const id = get(currentProjectId);
			expect(id).toBeNull();
		});
	});
});
