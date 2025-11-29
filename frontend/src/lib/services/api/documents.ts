/**
 * Documents API client
 *
 * Handles all document-related API operations (upload, download, delete).
 * All functions use shared apiRequest wrapper with automatic error handling.
 */

import { apiRequest } from './base';
import { API_ENDPOINTS } from '$lib/config';
import { toast } from '$lib/stores/toast';
import type { Document, DocumentUploadResponse, DocumentListResponse } from '$lib/types';

/**
 * Upload documents to a project.
 *
 * @param projectId - Project ID to upload documents to
 * @param files - Array of File objects to upload
 * @returns Promise<DocumentUploadResponse> - Uploaded documents and any failures
 * @throws Error if API call fails
 *
 * @example
 * const result = await uploadDocuments(123, [file1, file2]);
 * console.log(`Uploaded ${result.documents.length} files`);
 * if (result.failed.length > 0) {
 *   console.log(`${result.failed.length} files failed to upload`);
 * }
 */
export async function uploadDocuments(
	projectId: number,
	files: File[]
): Promise<DocumentUploadResponse> {
	// Create FormData for multipart upload
	const formData = new FormData();
	for (const file of files) {
		formData.append('files', file);
	}

	const response = await apiRequest<DocumentUploadResponse>(
		API_ENDPOINTS.documents.upload(projectId),
		{
			method: 'POST',
			body: formData
			// Note: Don't set Content-Type header - browser will set it with boundary
		}
	);

	// Show success toast if any files uploaded successfully
	if (response.documents.length > 0) {
		toast.success(`${response.documents.length} file(s) uploaded successfully`);
	}

	// Show error toast if any files failed
	if (response.failed.length > 0) {
		toast.error(`${response.failed.length} file(s) failed to upload`);
	}

	return response;
}

/**
 * Get list of documents for a project.
 *
 * @param projectId - Project ID
 * @param options - Optional sort/filter parameters
 * @returns Promise<DocumentListResponse> - List of documents
 * @throws Error if API call fails
 *
 * @example
 * const response = await getDocuments(123, { sortBy: 'date', sortOrder: 'desc' });
 * console.log(`Found ${response.documents.length} documents`);
 */
export async function getDocuments(
	projectId: number,
	options?: {
		sortBy?: 'name' | 'date' | 'size' | 'type';
		sortOrder?: 'asc' | 'desc';
		filterType?: string;
	}
): Promise<DocumentListResponse> {
	// Build query parameters
	const params = new URLSearchParams();
	if (options?.sortBy) params.append('sort_by', options.sortBy);
	if (options?.sortOrder) params.append('sort_order', options.sortOrder);
	if (options?.filterType) params.append('filter_type', options.filterType);

	const url = `${API_ENDPOINTS.documents.list(projectId)}${params.toString() ? `?${params}` : ''}`;

	return apiRequest<DocumentListResponse>(url);
}

/**
 * Get single document metadata.
 *
 * @param documentId - Document ID
 * @returns Promise<Document> - Document metadata
 * @throws Error if document not found or API call fails
 *
 * @example
 * const doc = await getDocument(456);
 * console.log(doc.original_filename, doc.file_size);
 */
export async function getDocument(documentId: number): Promise<Document> {
	return apiRequest<Document>(API_ENDPOINTS.documents.get(documentId));
}

/**
 * Download document file.
 *
 * Triggers browser download by opening the download URL in a new window.
 *
 * @param documentId - Document ID to download
 * @returns Promise<void>
 * @throws Error if document not found or API call fails
 *
 * @example
 * await downloadDocument(456);
 * // Browser will prompt user to save file
 */
export async function downloadDocument(documentId: number): Promise<void> {
	// For file downloads, we use a different approach:
	// Open the download URL in a new window to trigger browser download
	const url = API_ENDPOINTS.documents.download(documentId);

	// Create a temporary link and trigger click
	const link = document.createElement('a');
	link.href = url;
	link.download = ''; // Let browser use filename from Content-Disposition header
	link.style.display = 'none';
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);

	toast.success('Download started');
}

/**
 * Delete document.
 *
 * Deletes both the file and database record.
 *
 * @param documentId - Document ID to delete
 * @returns Promise<void>
 * @throws Error if document not found or API call fails
 *
 * @example
 * await deleteDocument(456);
 */
export async function deleteDocument(documentId: number): Promise<void> {
	await apiRequest<void>(API_ENDPOINTS.documents.delete(documentId), {
		method: 'DELETE'
	});

	toast.success('Document deleted successfully');
}
