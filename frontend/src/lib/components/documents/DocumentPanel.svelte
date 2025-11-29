<script lang="ts">
/**
 * DocumentPanel component
 *
 * Purpose: Collapsible panel containing document uploader and list
 *
 * Features:
 * - Collapsible panel (expand/collapse with animation)
 * - DocumentUploader at top for file uploads
 * - DocumentList below showing project documents
 * - Auto-loads documents when project changes
 * - Handles upload, delete, download events
 *
 * Layout:
 * ┌────────────────────────────────────────┐
 * │ Documents (3)                    [▼]   │ ← Header (collapsible)
 * ├────────────────────────────────────────┤
 * │ ┌────────────────────────────────────┐ │
 * │ │        Drag & Drop to Upload       │ │ ← Uploader
 * │ └────────────────────────────────────┘ │
 * │                                        │
 * │ ┌─────────────────────────────────────┐│
 * │ │ Document 1.pdf    [↓] [🗑]          ││ ← Document List
 * │ │ Document 2.docx   [↓] [🗑]          ││
 * │ └─────────────────────────────────────┘│
 * └────────────────────────────────────────┘
 *
 * WHY collapsible panel:
 * - Space efficiency: Documents panel can be hidden to maximize chat area
 * - User control: Users can focus on chat or documents as needed
 * - Clean UI: Reduces visual clutter when documents aren't the focus
 */

import { onMount, onDestroy } from 'svelte';
import { slide } from 'svelte/transition';
import DocumentUploader from './DocumentUploader.svelte';
import DocumentList from './DocumentList.svelte';
import {
	documents,
	documentsLoading,
	documentsError,
	documentCount,
	loadDocuments,
	addDocuments,
	removeDocument,
	sortDocuments,
	clearDocuments
} from '$lib/stores/documents';
import { deleteDocument, downloadDocument } from '$lib/services/api/documents';
import { currentProjectId } from '$lib/stores/projects';
import { toast } from '$lib/stores/toast';
import { logger } from '$lib/utils/logger';
import type { Document } from '$lib/types';

// Panel state
let isExpanded = true;
let isDeleting = false;

// Subscribe to project changes to load documents
let unsubscribe: () => void;

onMount(() => {
	// Load documents when project changes
	unsubscribe = currentProjectId.subscribe(async (projectId) => {
		if (projectId !== null) {
			await loadDocuments(projectId);
		} else {
			clearDocuments();
		}
	});
});

onDestroy(() => {
	if (unsubscribe) {
		unsubscribe();
	}
});

/**
 * Toggle panel expanded/collapsed state
 */
function togglePanel() {
	isExpanded = !isExpanded;
}

/**
 * Handle successful upload event from DocumentUploader
 * Updates the documents store with newly uploaded documents
 */
function handleUpload(event: CustomEvent<Document[]>) {
	const uploadedDocs = event.detail;
	addDocuments(uploadedDocs);
	logger.info(`Added ${uploadedDocs.length} documents to store`);
}

/**
 * Handle upload error event from DocumentUploader
 * Shows error toast (already handled by DocumentUploader, but we log it)
 */
function handleUploadError(event: CustomEvent<{ filename: string; error: string }[]>) {
	const failedUploads = event.detail;
	logger.error(`${failedUploads.length} uploads failed`, failedUploads);
}

/**
 * Handle sort event from DocumentList
 * Sorts documents in the store
 */
function handleSort(event: CustomEvent<{ field: 'name' | 'date' | 'size' | 'type'; order: 'asc' | 'desc' }>) {
	const { field, order } = event.detail;
	sortDocuments(field, order);
}

/**
 * Handle filter event from DocumentList
 * Reloads documents with filter applied
 */
async function handleFilter(event: CustomEvent<{ type: string | null }>) {
	const { type } = event.detail;
	const projectId = $currentProjectId;
	if (projectId !== null) {
		await loadDocuments(projectId, { filterType: type || undefined });
	}
}

/**
 * Handle delete event from DocumentList
 * Confirms deletion and removes document
 */
async function handleDelete(event: CustomEvent<{ documentId: number }>) {
	const { documentId } = event.detail;

	// Find document name for confirmation
	const doc = $documents.find((d) => d.id === documentId);
	if (!doc) return;

	// Confirm deletion
	const confirmed = confirm(`Are you sure you want to delete "${doc.original_filename}"?\n\nThis action cannot be undone.`);
	if (!confirmed) return;

	try {
		isDeleting = true;
		await deleteDocument(documentId);
		removeDocument(documentId);
		logger.info(`Deleted document ${documentId}`);
	} catch (error) {
		const errorMsg = error instanceof Error ? error.message : 'Failed to delete document';
		toast.error(errorMsg);
		logger.error('Failed to delete document', { documentId, error });
	} finally {
		isDeleting = false;
	}
}

/**
 * Handle download event from DocumentList
 * Triggers file download
 */
async function handleDownload(event: CustomEvent<{ documentId: number }>) {
	const { documentId } = event.detail;

	try {
		await downloadDocument(documentId);
		logger.info(`Downloaded document ${documentId}`);
	} catch (error) {
		const errorMsg = error instanceof Error ? error.message : 'Failed to download document';
		toast.error(errorMsg);
		logger.error('Failed to download document', { documentId, error });
	}
}
</script>

<div class="document-panel" class:expanded={isExpanded}>
	<!-- Panel header (always visible) -->
	<button
		type="button"
		class="panel-header"
		on:click={togglePanel}
		aria-expanded={isExpanded}
		aria-controls="document-panel-content"
	>
		<div class="header-left">
			<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" class="header-icon">
				<path
					d="M4 4h8l4 4v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6a2 2 0 012-2z"
					stroke="currentColor"
					stroke-width="1.5"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
				<path d="M12 4v4h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
			</svg>
			<span class="header-title">Documents</span>
			{#if $documentCount > 0}
				<span class="document-count">({$documentCount})</span>
			{/if}
		</div>

		<div class="header-right">
			{#if $documentsLoading}
				<svg class="spinner" width="16" height="16" viewBox="0 0 16 16">
					<circle
						cx="8"
						cy="8"
						r="6"
						stroke="currentColor"
						stroke-width="2"
						fill="none"
						stroke-dasharray="30"
						stroke-linecap="round"
					>
						<animateTransform
							attributeName="transform"
							type="rotate"
							from="0 8 8"
							to="360 8 8"
							dur="1s"
							repeatCount="indefinite"
						/>
					</circle>
				</svg>
			{/if}

			<!-- Chevron icon (rotates when expanded) -->
			<svg
				width="16"
				height="16"
				viewBox="0 0 16 16"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
				class="chevron"
				class:rotated={isExpanded}
			>
				<path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
			</svg>
		</div>
	</button>

	<!-- Panel content (collapsible) -->
	{#if isExpanded}
		<div id="document-panel-content" class="panel-content" transition:slide={{ duration: 200 }}>
			{#if $documentsError}
				<div class="error-banner" role="alert">
					<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
						<circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5" />
						<path d="M8 4v4M8 10v2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
					</svg>
					<span>{$documentsError}</span>
					<button
						type="button"
						class="retry-button"
						on:click={() => $currentProjectId && loadDocuments($currentProjectId)}
					>
						Retry
					</button>
				</div>
			{/if}

			<!-- Document Uploader -->
			<div class="uploader-section">
				<DocumentUploader projectId={$currentProjectId} on:upload={handleUpload} on:error={handleUploadError} />
			</div>

			<!-- Document List -->
			<div class="list-section">
				<DocumentList
					projectId={$currentProjectId}
					documents={$documents}
					isLoading={$documentsLoading || isDeleting}
					on:sort={handleSort}
					on:filter={handleFilter}
					on:delete={handleDelete}
					on:download={handleDownload}
				/>
			</div>
		</div>
	{/if}
</div>

<style>
	.document-panel {
		background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
		border-radius: 12px;
		border: 1px solid rgba(255, 255, 255, 0.1);
		overflow: hidden;
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
	}

	/* Panel header - clickable to toggle */
	.panel-header {
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 1.25rem;
		background: transparent;
		border: none;
		cursor: pointer;
		transition: background-color 0.2s ease;
	}

	.panel-header:hover {
		background: rgba(255, 255, 255, 0.05);
	}

	.header-left {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.header-icon {
		color: #60a5fa;
	}

	.header-title {
		font-size: 0.9375rem;
		font-weight: 600;
		color: #f1f5f9;
	}

	.document-count {
		font-size: 0.8125rem;
		color: #94a3b8;
		font-weight: 400;
	}

	.header-right {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.spinner {
		color: #60a5fa;
	}

	.chevron {
		color: #94a3b8;
		transition: transform 0.2s ease;
	}

	.chevron.rotated {
		transform: rotate(180deg);
	}

	/* Panel content */
	.panel-content {
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	/* Error banner */
	.error-banner {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1rem;
		background: rgba(239, 68, 68, 0.1);
		border-bottom: 1px solid rgba(239, 68, 68, 0.2);
		color: #fca5a5;
		font-size: 0.875rem;
	}

	.retry-button {
		margin-left: auto;
		padding: 0.25rem 0.75rem;
		background: rgba(239, 68, 68, 0.2);
		border: 1px solid rgba(239, 68, 68, 0.3);
		border-radius: 4px;
		color: #fca5a5;
		font-size: 0.8125rem;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.retry-button:hover {
		background: rgba(239, 68, 68, 0.3);
	}

	/* Uploader section */
	.uploader-section {
		padding: 1rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	}

	/* List section */
	.list-section {
		max-height: 300px;
		overflow-y: auto;
	}

	/* Custom scrollbar */
	.list-section::-webkit-scrollbar {
		width: 6px;
	}

	.list-section::-webkit-scrollbar-track {
		background: rgba(255, 255, 255, 0.05);
	}

	.list-section::-webkit-scrollbar-thumb {
		background: rgba(255, 255, 255, 0.2);
		border-radius: 3px;
	}

	.list-section::-webkit-scrollbar-thumb:hover {
		background: rgba(255, 255, 255, 0.3);
	}
</style>
