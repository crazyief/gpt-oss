/**
 * Unit tests for documents.ts - Documents API client
 *
 * Test coverage:
 * - uploadDocuments function (5 tests)
 * - getDocuments function (5 tests)
 * - getDocument function (3 tests)
 * - downloadDocument function (3 tests)
 * - deleteDocument function (3 tests)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
	uploadDocuments,
	getDocuments,
	getDocument,
	downloadDocument,
	deleteDocument
} from './documents';
import { API_ENDPOINTS } from '$lib/config';
import type { Document, DocumentUploadResponse, DocumentListResponse } from '$lib/types';
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

describe('documents.ts - uploadDocuments', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('sends POST request with FormData to /api/projects/{id}/documents/upload', async () => {
		const mockResponse: DocumentUploadResponse = {
			documents: [
				{
					id: 1,
					project_id: 123,
					original_filename: 'test.pdf',
					file_path: '/uploads/test.pdf',
					file_size: 1024,
					mime_type: 'application/pdf',
					created_at: '2025-11-24T00:00:00Z'
				}
			],
			failed: []
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockResponse);

		const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
		await uploadDocuments(123, [file]);

		expect(apiRequest).toHaveBeenCalledWith(
			API_ENDPOINTS.documents.upload(123),
			expect.objectContaining({
				method: 'POST',
				body: expect.any(FormData)
			})
		);
	});

	it('shows success toast when files upload successfully', async () => {
		const mockResponse: DocumentUploadResponse = {
			documents: [
				{
					id: 1,
					project_id: 123,
					original_filename: 'test.pdf',
					file_path: '/uploads/test.pdf',
					file_size: 1024,
					mime_type: 'application/pdf',
					created_at: '2025-11-24T00:00:00Z'
				}
			],
			failed: []
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockResponse);

		const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
		await uploadDocuments(123, [file]);

		expect(toastStore.toast.success).toHaveBeenCalledWith('1 file(s) uploaded successfully');
	});

	it('shows error toast when files fail to upload', async () => {
		const mockResponse: DocumentUploadResponse = {
			documents: [],
			failed: [{ filename: 'bad.pdf', error: 'Invalid format' }]
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockResponse);

		const file = new File(['test content'], 'bad.pdf', { type: 'application/pdf' });
		await uploadDocuments(123, [file]);

		expect(toastStore.toast.error).toHaveBeenCalledWith('1 file(s) failed to upload');
	});

	it('returns uploaded documents data', async () => {
		const mockDocument: Document = {
			id: 1,
			project_id: 123,
			original_filename: 'test.pdf',
			file_path: '/uploads/test.pdf',
			file_size: 1024,
			mime_type: 'application/pdf',
			created_at: '2025-11-24T00:00:00Z'
		};

		const mockResponse: DocumentUploadResponse = {
			documents: [mockDocument],
			failed: []
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockResponse);

		const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
		const result = await uploadDocuments(123, [file]);

		expect(result.documents).toHaveLength(1);
		expect(result.documents[0].original_filename).toBe('test.pdf');
	});

	it('handles multiple files upload', async () => {
		const mockResponse: DocumentUploadResponse = {
			documents: [
				{
					id: 1,
					project_id: 123,
					original_filename: 'file1.pdf',
					file_path: '/uploads/file1.pdf',
					file_size: 1024,
					mime_type: 'application/pdf',
					created_at: '2025-11-24T00:00:00Z'
				},
				{
					id: 2,
					project_id: 123,
					original_filename: 'file2.txt',
					file_path: '/uploads/file2.txt',
					file_size: 512,
					mime_type: 'text/plain',
					created_at: '2025-11-24T00:00:00Z'
				}
			],
			failed: []
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockResponse);

		const files = [
			new File(['content1'], 'file1.pdf', { type: 'application/pdf' }),
			new File(['content2'], 'file2.txt', { type: 'text/plain' })
		];

		const result = await uploadDocuments(123, files);

		expect(result.documents).toHaveLength(2);
		expect(toastStore.toast.success).toHaveBeenCalledWith('2 file(s) uploaded successfully');
	});
});

describe('documents.ts - getDocuments', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('sends GET request to /api/projects/{id}/documents', async () => {
		const mockResponse: DocumentListResponse = {
			documents: [],
			total_count: 0
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockResponse);

		await getDocuments(123);

		expect(apiRequest).toHaveBeenCalledWith(
			API_ENDPOINTS.documents.list(123),
			expect.objectContaining({})
		);
	});

	it('returns array of documents', async () => {
		const mockDocuments: Document[] = [
			{
				id: 1,
				project_id: 123,
				original_filename: 'doc1.pdf',
				file_path: '/uploads/doc1.pdf',
				file_size: 1024,
				mime_type: 'application/pdf',
				created_at: '2025-11-24T00:00:00Z'
			},
			{
				id: 2,
				project_id: 123,
				original_filename: 'doc2.txt',
				file_path: '/uploads/doc2.txt',
				file_size: 512,
				mime_type: 'text/plain',
				created_at: '2025-11-24T01:00:00Z'
			}
		];

		const mockResponse: DocumentListResponse = {
			documents: mockDocuments,
			total_count: 2
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockResponse);

		const result = await getDocuments(123);

		expect(result.documents).toHaveLength(2);
		expect(result.total_count).toBe(2);
	});

	it('includes sort parameters in URL', async () => {
		const mockResponse: DocumentListResponse = {
			documents: [],
			total_count: 0
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockResponse);

		await getDocuments(123, { sortBy: 'date', sortOrder: 'desc' });

		expect(apiRequest).toHaveBeenCalledWith(
			expect.stringContaining('sort_by=date'),
			expect.any(Object)
		);
		expect(apiRequest).toHaveBeenCalledWith(
			expect.stringContaining('sort_order=desc'),
			expect.any(Object)
		);
	});

	it('includes filter parameters in URL', async () => {
		const mockResponse: DocumentListResponse = {
			documents: [],
			total_count: 0
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockResponse);

		await getDocuments(123, { filterType: 'pdf' });

		expect(apiRequest).toHaveBeenCalledWith(
			expect.stringContaining('filter_type=pdf'),
			expect.any(Object)
		);
	});

	it('throws error on API failure', async () => {
		vi.mocked(apiRequest).mockRejectedValueOnce(new Error('Network error'));

		await expect(getDocuments(123)).rejects.toThrow('Network error');
	});
});

describe('documents.ts - getDocument', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('sends GET request to /api/documents/{id}', async () => {
		const mockDocument: Document = {
			id: 456,
			project_id: 123,
			original_filename: 'test.pdf',
			file_path: '/uploads/test.pdf',
			file_size: 1024,
			mime_type: 'application/pdf',
			created_at: '2025-11-24T00:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockDocument);

		await getDocument(456);

		expect(apiRequest).toHaveBeenCalledWith(API_ENDPOINTS.documents.get(456));
	});

	it('returns single document data', async () => {
		const mockDocument: Document = {
			id: 456,
			project_id: 123,
			original_filename: 'test.pdf',
			file_path: '/uploads/test.pdf',
			file_size: 2048,
			mime_type: 'application/pdf',
			created_at: '2025-11-24T10:00:00Z'
		};

		vi.mocked(apiRequest).mockResolvedValueOnce(mockDocument);

		const result = await getDocument(456);

		expect(result).toEqual(mockDocument);
		expect(result.id).toBe(456);
		expect(result.original_filename).toBe('test.pdf');
	});

	it('throws error on 404 Not Found', async () => {
		vi.mocked(apiRequest).mockRejectedValueOnce(new Error('Document not found'));

		await expect(getDocument(999)).rejects.toThrow('Document not found');
	});
});

describe('documents.ts - downloadDocument', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		// Mock DOM methods
		const mockLink = {
			href: '',
			download: '',
			style: { display: '' },
			click: vi.fn()
		};
		vi.spyOn(document, 'createElement').mockReturnValue(mockLink as unknown as HTMLAnchorElement);
		vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as unknown as Node);
		vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as unknown as Node);
	});

	afterEach(() => {
		vi.clearAllMocks();
		vi.restoreAllMocks();
	});

	it('creates and clicks a download link', async () => {
		await downloadDocument(456);

		expect(document.createElement).toHaveBeenCalledWith('a');
		expect(document.body.appendChild).toHaveBeenCalled();
		expect(document.body.removeChild).toHaveBeenCalled();
	});

	it('sets correct download URL', async () => {
		const mockLink = {
			href: '',
			download: '',
			style: { display: '' },
			click: vi.fn()
		};
		vi.spyOn(document, 'createElement').mockReturnValue(mockLink as unknown as HTMLAnchorElement);

		await downloadDocument(456);

		expect(mockLink.href).toBe(API_ENDPOINTS.documents.download(456));
	});

	it('shows success toast after download starts', async () => {
		await downloadDocument(456);

		expect(toastStore.toast.success).toHaveBeenCalledWith('Download started');
	});
});

describe('documents.ts - deleteDocument', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('sends DELETE request to /api/documents/{id}', async () => {
		vi.mocked(apiRequest).mockResolvedValueOnce(undefined);

		await deleteDocument(456);

		expect(apiRequest).toHaveBeenCalledWith(API_ENDPOINTS.documents.delete(456), {
			method: 'DELETE'
		});
	});

	it('shows success toast after deletion', async () => {
		vi.mocked(apiRequest).mockResolvedValueOnce(undefined);

		await deleteDocument(456);

		expect(toastStore.toast.success).toHaveBeenCalledWith('Document deleted successfully');
	});

	it('throws error on API failure', async () => {
		vi.mocked(apiRequest).mockRejectedValueOnce(new Error('Document not found'));

		await expect(deleteDocument(999)).rejects.toThrow('Document not found');
	});
});
