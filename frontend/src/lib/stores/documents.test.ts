/**
 * Unit tests for documents store
 *
 * Tests: State mutations, CRUD operations, derived stores, sorting, filtering
 *
 * NOTE: Store uses unified state { documents: [], isLoading: false, error: null }
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { get } from 'svelte/store';
import {
	documents,
	documentCount,
	totalStorageUsed,
	addDocument,
	addDocuments,
	removeDocument,
	clearDocuments,
	sortDocuments,
	filterDocuments,
	loadDocuments
} from './documents';
import type { Document } from '$lib/types';

// Mock the documents API
vi.mock('$lib/services/api', () => ({
	documents: {
		getDocuments: vi.fn()
	}
}));

// Mock the logger
vi.mock('$lib/utils/logger', () => ({
	logger: {
		info: vi.fn(),
		error: vi.fn(),
		debug: vi.fn(),
		warn: vi.fn()
	}
}));

describe('documents store', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		clearDocuments();
	});

	describe('initial state', () => {
		it('should start with empty documents', () => {
			const state = get(documents);
			expect(state.documents).toEqual([]);
		});

		it('should have loading = false initially', () => {
			const state = get(documents);
			expect(state.isLoading).toBe(false);
		});

		it('should have no error initially', () => {
			const state = get(documents);
			expect(state.error).toBeNull();
		});
	});

	describe('addDocument', () => {
		it('should add document to store', () => {
			const document: Document = {
				id: 1,
				project_id: 1,
				original_filename: 'test.pdf',
				stored_filename: 'test-123.pdf',
				mime_type: 'application/pdf',
				file_size: 1024,
				uploaded_at: '2025-01-01T00:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			};

			addDocument(document);
			const state = get(documents);
			expect(state.documents).toHaveLength(1);
			expect(state.documents[0]).toEqual(document);
		});

		it('should append to existing documents', () => {
			const doc1: Document = {
				id: 1,
				project_id: 1,
				original_filename: 'first.pdf',
				stored_filename: 'first-123.pdf',
				mime_type: 'application/pdf',
				file_size: 1024,
				uploaded_at: '2025-01-01T00:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			};

			const doc2: Document = {
				id: 2,
				project_id: 1,
				original_filename: 'second.pdf',
				stored_filename: 'second-456.pdf',
				mime_type: 'application/pdf',
				file_size: 2048,
				uploaded_at: '2025-01-01T01:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			};

			addDocument(doc1);
			addDocument(doc2);

			const state = get(documents);
			expect(state.documents).toHaveLength(2);
			expect(state.documents[1]).toEqual(doc2);
		});
	});

	describe('addDocuments', () => {
		it('should add multiple documents at once', () => {
			const newDocs: Document[] = [
				{
					id: 1,
					project_id: 1,
					original_filename: 'first.pdf',
					stored_filename: 'first-123.pdf',
					mime_type: 'application/pdf',
					file_size: 1024,
					uploaded_at: '2025-01-01T00:00:00Z',
					parsed_at: null,
					status: 'uploaded',
					error_message: null
				},
				{
					id: 2,
					project_id: 1,
					original_filename: 'second.pdf',
					stored_filename: 'second-456.pdf',
					mime_type: 'application/pdf',
					file_size: 2048,
					uploaded_at: '2025-01-01T01:00:00Z',
					parsed_at: null,
					status: 'uploaded',
					error_message: null
				}
			];

			addDocuments(newDocs);
			const state = get(documents);
			expect(state.documents).toHaveLength(2);
		});
	});

	describe('removeDocument', () => {
		it('should remove document by id', () => {
			const document: Document = {
				id: 1,
				project_id: 1,
				original_filename: 'to-remove.pdf',
				stored_filename: 'to-remove-123.pdf',
				mime_type: 'application/pdf',
				file_size: 1024,
				uploaded_at: '2025-01-01T00:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			};

			addDocument(document);
			removeDocument(1);

			const state = get(documents);
			expect(state.documents).toHaveLength(0);
		});

		it('should not remove documents with different id', () => {
			const document: Document = {
				id: 1,
				project_id: 1,
				original_filename: 'keep-me.pdf',
				stored_filename: 'keep-me-123.pdf',
				mime_type: 'application/pdf',
				file_size: 1024,
				uploaded_at: '2025-01-01T00:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			};

			addDocument(document);
			removeDocument(999);

			const state = get(documents);
			expect(state.documents).toHaveLength(1);
		});
	});

	describe('clearDocuments', () => {
		it('should clear all documents', () => {
			const document: Document = {
				id: 1,
				project_id: 1,
				original_filename: 'test.pdf',
				stored_filename: 'test-123.pdf',
				mime_type: 'application/pdf',
				file_size: 1024,
				uploaded_at: '2025-01-01T00:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			};

			addDocument(document);
			clearDocuments();

			const state = get(documents);
			expect(state.documents).toEqual([]);
		});

		it('should reset error when clearing documents', () => {
			// Set error state first via update
			documents.update((s) => ({ ...s, error: 'Test error' }));
			clearDocuments();

			const state = get(documents);
			expect(state.error).toBeNull();
		});
	});

	describe('derived stores', () => {
		it('documentCount should return document count', () => {
			expect(get(documentCount)).toBe(0);

			const doc: Document = {
				id: 1,
				project_id: 1,
				original_filename: 'test.pdf',
				stored_filename: 'test-123.pdf',
				mime_type: 'application/pdf',
				file_size: 1024,
				uploaded_at: '2025-01-01T00:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			};

			addDocument(doc);
			expect(get(documentCount)).toBe(1);
		});

		it('totalStorageUsed should sum file sizes', () => {
			const doc1: Document = {
				id: 1,
				project_id: 1,
				original_filename: 'first.pdf',
				stored_filename: 'first-123.pdf',
				mime_type: 'application/pdf',
				file_size: 1000,
				uploaded_at: '2025-01-01T00:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			};

			const doc2: Document = {
				id: 2,
				project_id: 1,
				original_filename: 'second.pdf',
				stored_filename: 'second-456.pdf',
				mime_type: 'application/pdf',
				file_size: 2000,
				uploaded_at: '2025-01-01T01:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			};

			addDocument(doc1);
			addDocument(doc2);

			expect(get(totalStorageUsed)).toBe(3000);
		});
	});

	describe('sortDocuments', () => {
		const doc1: Document = {
			id: 1,
			project_id: 1,
			original_filename: 'zzz.pdf',
			stored_filename: 'zzz-123.pdf',
			mime_type: 'application/pdf',
			file_size: 1000,
			uploaded_at: '2025-01-01T00:00:00Z',
			parsed_at: null,
			status: 'uploaded',
			error_message: null
		};

		const doc2: Document = {
			id: 2,
			project_id: 1,
			original_filename: 'aaa.pdf',
			stored_filename: 'aaa-456.pdf',
			mime_type: 'application/pdf',
			file_size: 3000,
			uploaded_at: '2025-01-03T00:00:00Z',
			parsed_at: null,
			status: 'uploaded',
			error_message: null
		};

		const doc3: Document = {
			id: 3,
			project_id: 1,
			original_filename: 'mmm.pdf',
			stored_filename: 'mmm-789.pdf',
			mime_type: 'text/plain',
			file_size: 2000,
			uploaded_at: '2025-01-02T00:00:00Z',
			parsed_at: null,
			status: 'uploaded',
			error_message: null
		};

		beforeEach(() => {
			clearDocuments();
			addDocuments([doc1, doc2, doc3]);
		});

		it('should sort by name ascending', () => {
			sortDocuments('name', 'asc');
			const state = get(documents);
			expect(state.documents[0].original_filename).toBe('aaa.pdf');
			expect(state.documents[1].original_filename).toBe('mmm.pdf');
			expect(state.documents[2].original_filename).toBe('zzz.pdf');
		});

		it('should sort by name descending', () => {
			sortDocuments('name', 'desc');
			const state = get(documents);
			expect(state.documents[0].original_filename).toBe('zzz.pdf');
			expect(state.documents[2].original_filename).toBe('aaa.pdf');
		});

		it('should sort by date ascending', () => {
			sortDocuments('date', 'asc');
			const state = get(documents);
			expect(state.documents[0].id).toBe(1); // 2025-01-01
			expect(state.documents[1].id).toBe(3); // 2025-01-02
			expect(state.documents[2].id).toBe(2); // 2025-01-03
		});

		it('should sort by size ascending', () => {
			sortDocuments('size', 'asc');
			const state = get(documents);
			expect(state.documents[0].file_size).toBe(1000);
			expect(state.documents[1].file_size).toBe(2000);
			expect(state.documents[2].file_size).toBe(3000);
		});

		it('should sort by type ascending', () => {
			sortDocuments('type', 'asc');
			const state = get(documents);
			expect(state.documents[0].mime_type).toBe('application/pdf');
			expect(state.documents[2].mime_type).toBe('text/plain');
		});
	});

	describe('filterDocuments', () => {
		it('should filter by type', () => {
			const doc1: Document = {
				id: 1,
				project_id: 1,
				original_filename: 'file.pdf',
				stored_filename: 'file-123.pdf',
				mime_type: 'application/pdf',
				file_size: 1024,
				uploaded_at: '2025-01-01T00:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			};

			const doc2: Document = {
				id: 2,
				project_id: 1,
				original_filename: 'file.txt',
				stored_filename: 'file-456.txt',
				mime_type: 'text/plain',
				file_size: 512,
				uploaded_at: '2025-01-01T01:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			};

			addDocuments([doc1, doc2]);

			const pdfDocs = filterDocuments('pdf');
			expect(get(pdfDocs)).toHaveLength(1);
			expect(get(pdfDocs)[0].mime_type).toBe('application/pdf');
		});

		it('should return all documents when filter is null', () => {
			const doc: Document = {
				id: 1,
				project_id: 1,
				original_filename: 'file.pdf',
				stored_filename: 'file-123.pdf',
				mime_type: 'application/pdf',
				file_size: 1024,
				uploaded_at: '2025-01-01T00:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			};

			addDocument(doc);

			const allDocs = filterDocuments(null);
			expect(get(allDocs)).toHaveLength(1);
		});
	});

	describe('loadDocuments', () => {
		const mockDocuments: Document[] = [
			{
				id: 1,
				project_id: 1,
				original_filename: 'test1.pdf',
				stored_filename: 'test1-123.pdf',
				mime_type: 'application/pdf',
				file_size: 1024,
				uploaded_at: '2025-01-01T00:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			},
			{
				id: 2,
				project_id: 1,
				original_filename: 'test2.pdf',
				stored_filename: 'test2-456.pdf',
				mime_type: 'application/pdf',
				file_size: 2048,
				uploaded_at: '2025-01-02T00:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			}
		];

		it('should set isLoading to true while loading', async () => {
			const { documents: documentsApi } = await import('$lib/services/api');
			(documentsApi.getDocuments as ReturnType<typeof vi.fn>).mockImplementation(
				() => new Promise((resolve) => setTimeout(() => resolve({ documents: mockDocuments }), 100))
			);

			const loadPromise = loadDocuments(1);

			// Should be loading
			expect(get(documents).isLoading).toBe(true);

			await loadPromise;
		});

		it('should load documents successfully', async () => {
			const { documents: documentsApi } = await import('$lib/services/api');
			(documentsApi.getDocuments as ReturnType<typeof vi.fn>).mockResolvedValue({
				documents: mockDocuments
			});

			await loadDocuments(1);

			const state = get(documents);
			expect(state.documents).toHaveLength(2);
			expect(state.isLoading).toBe(false);
			expect(state.error).toBeNull();
		});

		it('should clear error on successful load', async () => {
			const { documents: documentsApi } = await import('$lib/services/api');

			// Set error state first
			documents.update((s) => ({ ...s, error: 'Previous error' }));

			(documentsApi.getDocuments as ReturnType<typeof vi.fn>).mockResolvedValue({
				documents: mockDocuments
			});

			await loadDocuments(1);

			const state = get(documents);
			expect(state.error).toBeNull();
		});

		it('should set error on API failure', async () => {
			const { documents: documentsApi } = await import('$lib/services/api');
			(documentsApi.getDocuments as ReturnType<typeof vi.fn>).mockRejectedValue(
				new Error('Network error')
			);

			await loadDocuments(1);

			const state = get(documents);
			expect(state.error).toBe('Network error');
			expect(state.isLoading).toBe(false);
		});

		it('should use default error message for non-Error rejections', async () => {
			const { documents: documentsApi } = await import('$lib/services/api');
			(documentsApi.getDocuments as ReturnType<typeof vi.fn>).mockRejectedValue('Unknown error');

			await loadDocuments(1);

			const state = get(documents);
			expect(state.error).toBe('Failed to load documents');
		});

		it('should handle AbortError gracefully', async () => {
			const { documents: documentsApi } = await import('$lib/services/api');
			const abortError = new Error('Aborted');
			abortError.name = 'AbortError';

			(documentsApi.getDocuments as ReturnType<typeof vi.fn>).mockRejectedValue(abortError);

			await loadDocuments(1);

			const state = get(documents);
			// Should not set error for abort
			expect(state.error).toBeNull();
			expect(state.isLoading).toBe(false);
		});

		it('should pass sort options to API', async () => {
			const { documents: documentsApi } = await import('$lib/services/api');
			(documentsApi.getDocuments as ReturnType<typeof vi.fn>).mockResolvedValue({
				documents: mockDocuments
			});

			await loadDocuments(1, { sortBy: 'name', sortOrder: 'desc' });

			expect(documentsApi.getDocuments).toHaveBeenCalledWith(1, {
				sortBy: 'name',
				sortOrder: 'desc'
			});
		});

		it('should pass filter options to API', async () => {
			const { documents: documentsApi } = await import('$lib/services/api');
			(documentsApi.getDocuments as ReturnType<typeof vi.fn>).mockResolvedValue({
				documents: mockDocuments
			});

			await loadDocuments(1, { filterType: 'pdf' });

			expect(documentsApi.getDocuments).toHaveBeenCalledWith(1, {
				filterType: 'pdf'
			});
		});

		it('should pass AbortSignal to API', async () => {
			const { documents: documentsApi } = await import('$lib/services/api');
			(documentsApi.getDocuments as ReturnType<typeof vi.fn>).mockResolvedValue({
				documents: mockDocuments
			});

			const controller = new AbortController();
			await loadDocuments(1, { signal: controller.signal });

			expect(documentsApi.getDocuments).toHaveBeenCalledWith(1, {
				signal: controller.signal
			});
		});

		it('should log document count on success', async () => {
			const { documents: documentsApi } = await import('$lib/services/api');
			const { logger } = await import('$lib/utils/logger');

			(documentsApi.getDocuments as ReturnType<typeof vi.fn>).mockResolvedValue({
				documents: mockDocuments
			});

			await loadDocuments(1);

			expect(logger.info).toHaveBeenCalledWith('Loaded 2 documents');
		});

		it('should log error on failure', async () => {
			const { documents: documentsApi } = await import('$lib/services/api');
			const { logger } = await import('$lib/utils/logger');

			const error = new Error('API Error');
			(documentsApi.getDocuments as ReturnType<typeof vi.fn>).mockRejectedValue(error);

			await loadDocuments(1);

			expect(logger.error).toHaveBeenCalledWith('Failed to load documents', error);
		});

		it('should replace existing documents on reload', async () => {
			const { documents: documentsApi } = await import('$lib/services/api');

			// Add existing document
			addDocument({
				id: 99,
				project_id: 1,
				original_filename: 'old.pdf',
				stored_filename: 'old-999.pdf',
				mime_type: 'application/pdf',
				file_size: 512,
				uploaded_at: '2024-01-01T00:00:00Z',
				parsed_at: null,
				status: 'uploaded',
				error_message: null
			});

			expect(get(documents).documents).toHaveLength(1);

			(documentsApi.getDocuments as ReturnType<typeof vi.fn>).mockResolvedValue({
				documents: mockDocuments
			});

			await loadDocuments(1);

			// Should have replaced old documents
			const state = get(documents);
			expect(state.documents).toHaveLength(2);
			expect(state.documents.find((d) => d.id === 99)).toBeUndefined();
		});
	});
});
