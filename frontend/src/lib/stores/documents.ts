/**
 * Documents store
 *
 * State management for document list and loading states.
 * Used by DocumentList and DocumentUploader components.
 */

import { writable, derived } from 'svelte/store';
import type { Document } from '$lib/types';
import { documents as documentsApi } from '$lib/services/api';
import { logger } from '$lib/utils/logger';

/**
 * Documents store (writable)
 *
 * Holds the current list of documents for the active project.
 */
export const documents = writable<Document[]>([]);

/**
 * Loading state for document operations
 */
export const documentsLoading = writable<boolean>(false);

/**
 * Error state for document operations
 */
export const documentsError = writable<string | null>(null);

/**
 * Derived store: Document count
 *
 * Automatically updates when documents list changes
 */
export const documentCount = derived(documents, ($documents) => $documents.length);

/**
 * Derived store: Total storage used (in bytes)
 *
 * Sum of all document file sizes
 */
export const totalStorageUsed = derived(documents, ($documents) =>
	$documents.reduce((total, doc) => total + doc.file_size, 0)
);

/**
 * Load documents for a project
 *
 * @param projectId - Project ID to load documents for
 * @param options - Optional sort/filter parameters
 */
export async function loadDocuments(
	projectId: number,
	options?: {
		sortBy?: 'name' | 'date' | 'size' | 'type';
		sortOrder?: 'asc' | 'desc';
		filterType?: string;
	}
): Promise<void> {
	documentsLoading.set(true);
	documentsError.set(null);

	try {
		logger.info(`Loading documents for project ${projectId}`, options);
		const response = await documentsApi.getDocuments(projectId, options);
		documents.set(response.documents);
		logger.info(`Loaded ${response.documents.length} documents`);
	} catch (error) {
		const errorMessage = error instanceof Error ? error.message : 'Failed to load documents';
		logger.error('Failed to load documents', error);
		documentsError.set(errorMessage);
	} finally {
		documentsLoading.set(false);
	}
}

/**
 * Add a document to the store
 *
 * Used after successful upload to update UI immediately
 *
 * @param document - Document to add
 */
export function addDocument(document: Document): void {
	documents.update((docs) => [...docs, document]);
}

/**
 * Add multiple documents to the store
 *
 * Used after successful batch upload
 *
 * @param newDocuments - Documents to add
 */
export function addDocuments(newDocuments: Document[]): void {
	documents.update((docs) => [...docs, ...newDocuments]);
}

/**
 * Remove a document from the store
 *
 * Used after successful deletion to update UI immediately
 *
 * @param documentId - Document ID to remove
 */
export function removeDocument(documentId: number): void {
	documents.update((docs) => docs.filter((doc) => doc.id !== documentId));
}

/**
 * Clear all documents from the store
 *
 * Used when switching projects or logging out
 */
export function clearDocuments(): void {
	documents.set([]);
	documentsError.set(null);
}

/**
 * Sort documents in-place
 *
 * @param sortBy - Field to sort by
 * @param sortOrder - Sort order (asc or desc)
 */
export function sortDocuments(sortBy: 'name' | 'date' | 'size' | 'type', sortOrder: 'asc' | 'desc' = 'asc'): void {
	documents.update((docs) => {
		const sorted = [...docs];

		sorted.sort((a, b) => {
			let comparison = 0;

			switch (sortBy) {
				case 'name':
					comparison = a.original_filename.localeCompare(b.original_filename);
					break;
				case 'date':
					comparison = new Date(a.uploaded_at).getTime() - new Date(b.uploaded_at).getTime();
					break;
				case 'size':
					comparison = a.file_size - b.file_size;
					break;
				case 'type':
					comparison = a.mime_type.localeCompare(b.mime_type);
					break;
			}

			return sortOrder === 'asc' ? comparison : -comparison;
		});

		return sorted;
	});
}

/**
 * Filter documents by type
 *
 * @param type - MIME type to filter by (e.g., 'pdf', 'docx')
 * @returns Derived store with filtered documents
 */
export function filterDocuments(type: string | null) {
	return derived(documents, ($documents) => {
		if (!type) return $documents;
		return $documents.filter((doc) => doc.mime_type.includes(type));
	});
}
