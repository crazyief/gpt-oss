/**
 * Unit tests for documents store
 *
 * Tests: State mutations, CRUD operations, derived stores, sorting, filtering
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import {
	documents,
	documentsLoading,
	documentsError,
	documentCount,
	totalStorageUsed,
	addDocument,
	addDocuments,
	removeDocument,
	clearDocuments,
	sortDocuments,
	filterDocuments
} from './documents';
import type { Document } from '$lib/types';

describe('documents store', () => {
	beforeEach(() => {
		clearDocuments();
	});

	describe('initial state', () => {
		it('should start with empty documents', () => {
			const docs = get(documents);
			expect(docs).toEqual([]);
		});

		it('should have loading = false initially', () => {
			const loading = get(documentsLoading);
			expect(loading).toBe(false);
		});

		it('should have no error initially', () => {
			const error = get(documentsError);
			expect(error).toBeNull();
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
			const docs = get(documents);
			expect(docs).toHaveLength(1);
			expect(docs[0]).toEqual(document);
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

			const docs = get(documents);
			expect(docs).toHaveLength(2);
			expect(docs[1]).toEqual(doc2);
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
			const docs = get(documents);
			expect(docs).toHaveLength(2);
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

			const docs = get(documents);
			expect(docs).toHaveLength(0);
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

			const docs = get(documents);
			expect(docs).toHaveLength(1);
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

			const docs = get(documents);
			expect(docs).toEqual([]);
		});

		it('should clear error when clearing documents', () => {
			documentsError.set('Test error');
			clearDocuments();

			const error = get(documentsError);
			expect(error).toBeNull();
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
			const docs = get(documents);
			expect(docs[0].original_filename).toBe('aaa.pdf');
			expect(docs[1].original_filename).toBe('mmm.pdf');
			expect(docs[2].original_filename).toBe('zzz.pdf');
		});

		it('should sort by name descending', () => {
			sortDocuments('name', 'desc');
			const docs = get(documents);
			expect(docs[0].original_filename).toBe('zzz.pdf');
			expect(docs[2].original_filename).toBe('aaa.pdf');
		});

		it('should sort by date ascending', () => {
			sortDocuments('date', 'asc');
			const docs = get(documents);
			expect(docs[0].id).toBe(1); // 2025-01-01
			expect(docs[1].id).toBe(3); // 2025-01-02
			expect(docs[2].id).toBe(2); // 2025-01-03
		});

		it('should sort by size ascending', () => {
			sortDocuments('size', 'asc');
			const docs = get(documents);
			expect(docs[0].file_size).toBe(1000);
			expect(docs[1].file_size).toBe(2000);
			expect(docs[2].file_size).toBe(3000);
		});

		it('should sort by type ascending', () => {
			sortDocuments('type', 'asc');
			const docs = get(documents);
			expect(docs[0].mime_type).toBe('application/pdf');
			expect(docs[2].mime_type).toBe('text/plain');
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
});
