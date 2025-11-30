<script lang="ts">
/**
 * DocumentList component
 *
 * Table view of documents with sorting and filtering
 *
 * Uses documents store directly for state management
 */

import { createEventDispatcher } from 'svelte';
import type { Document } from '$lib/types';
import DocumentItem from './DocumentItem.svelte';
import { documents as documentsStore } from '$lib/stores/documents';
import { currentProjectId } from '$lib/stores/projects';
import { documents as documentsApi } from '$lib/services/api';
import { toast } from '$lib/stores/toast';

const dispatch = createEventDispatcher<{
	sort: { column: string; order: 'asc' | 'desc' };
	filter: { type: string | null };
}>();

// Props for controlled sort state (passed from parent to persist across re-renders)
export let sortColumn: 'name' | 'type' | 'size' | 'date' = 'date';
export let sortOrder: 'asc' | 'desc' = 'desc';
export let filterType: string | null = null;

// Get state from store
$: documents = $documentsStore.documents;
$: isLoading = $documentsStore.isLoading;
$: projectId = $currentProjectId;

// Selection state
let selectedIds = new Set<number>();

// Column definitions
const columns: Array<{ key: 'name' | 'type' | 'size' | 'date'; label: string; sortable: boolean }> = [
	{ key: 'name', label: 'Name', sortable: true },
	{ key: 'type', label: 'Type', sortable: true },
	{ key: 'size', label: 'Size', sortable: true },
	{ key: 'date', label: 'Uploaded', sortable: true }
] as const;

// File types for filter dropdown
const fileTypes = [
	{ value: null, label: 'All Types' },
	{ value: 'pdf', label: 'PDF' },
	{ value: 'docx', label: 'Word' },
	{ value: 'xlsx', label: 'Excel' },
	{ value: 'txt', label: 'Text' },
	{ value: 'md', label: 'Markdown' }
];

function handleSort(column: 'name' | 'type' | 'size' | 'date') {
	if (sortColumn === column) {
		// Toggle order
		sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
	} else {
		// New column, default to desc
		sortColumn = column;
		sortOrder = 'desc';
	}

	dispatch('sort', { column, order: sortOrder });
}

function handleFilterChange(event: Event) {
	const select = event.target as HTMLSelectElement;
	filterType = select.value || null;
	dispatch('filter', { type: filterType });
}

function handleSelectDocument(documentId: number, selected: boolean) {
	if (selected) {
		selectedIds.add(documentId);
	} else {
		selectedIds.delete(documentId);
	}
	selectedIds = selectedIds; // Trigger reactivity
}

function handleSelectAll(event: Event) {
	const checkbox = event.target as HTMLInputElement;
	if (checkbox.checked) {
		selectedIds = new Set(documents.map((doc) => doc.id));
	} else {
		selectedIds.clear();
	}
	selectedIds = selectedIds; // Trigger reactivity
}

async function handleDownload(documentId: number) {
	try {
		// Note: downloadDocument handles its own toasts
		await documentsApi.downloadDocument(documentId);
	} catch (error) {
		// Error toast already shown by downloadDocument - do not duplicate
		// Just log the error silently
		console.error('Download error:', error);
	}
}

async function handleDelete(documentId: number) {
	if (!projectId) return;

	try {
		// Note: deleteDocument handles its own success toast
		await documentsApi.deleteDocument(documentId);
		// Reload documents to update list
		const { loadDocuments } = await import('$lib/stores/documents');
		await loadDocuments(projectId);
	} catch (error) {
		// Error toast already shown by apiRequest in base.ts - do not duplicate
		// Just log the error silently
		console.error('Delete error:', error);
	}
}

$: allSelected = documents.length > 0 && selectedIds.size === documents.length;
</script>

<div class="document-list-container">
	<!-- Toolbar -->
	<div class="toolbar">
		<div class="toolbar-left">
			<span class="document-count">{documents.length} document{documents.length !== 1 ? 's' : ''}</span>
			{#if selectedIds.size > 0}
				<span class="selection-count">{selectedIds.size} selected</span>
			{/if}
		</div>

		<div class="toolbar-right">
			<select class="filter-select" value={filterType || ''} on:change={handleFilterChange}>
				{#each fileTypes as fileType}
					<option value={fileType.value || ''}>{fileType.label}</option>
				{/each}
			</select>
		</div>
	</div>

	<!-- Table -->
	{#if isLoading}
		<div class="loading-state">
			<div class="spinner"></div>
			<p>Loading documents...</p>
		</div>
	{:else if documents.length === 0}
		<div class="empty-state">
			<svg
				width="64"
				height="64"
				viewBox="0 0 64 64"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M16 8H32L48 24V52C48 54.2091 46.2091 56 44 56H16C13.7909 56 12 54.2091 12 52V12C12 9.79086 13.7909 8 16 8Z"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
				<path d="M32 8V24H48" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
			</svg>
			<h3>No documents yet</h3>
			<p>Upload documents to get started</p>
		</div>
	{:else}
		<div class="table-container">
			<table class="documents-table">
				<thead>
					<tr>
						<th class="th-checkbox">
							<input
								type="checkbox"
								checked={allSelected}
								on:change={handleSelectAll}
								aria-label="Select all documents"
							/>
						</th>
						{#each columns as column}
							<th
								class="th-sortable"
								class:sorted={sortColumn === column.key}
								on:click={() => column.sortable && handleSort(column.key)}
								on:keydown={(e) => e.key === 'Enter' && column.sortable && handleSort(column.key)}
								role="button"
								tabindex="0"
								aria-label="Sort by {column.label}"
							>
								<span>{column.label}</span>
								{#if sortColumn === column.key}
									<svg
										class="sort-icon"
										class:asc={sortOrder === 'asc'}
										width="12"
										height="12"
										viewBox="0 0 12 12"
										fill="none"
										xmlns="http://www.w3.org/2000/svg"
									>
										<path
											d="M6 2V10M6 2L3 5M6 2L9 5"
											stroke="currentColor"
											stroke-width="1.5"
											stroke-linecap="round"
											stroke-linejoin="round"
										/>
									</svg>
								{/if}
							</th>
						{/each}
						<th class="th-actions">Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each documents as document (document.id)}
						<DocumentItem
							{document}
							selected={selectedIds.has(document.id)}
							on:select={(e) => handleSelectDocument(document.id, e.detail)}
							on:download={() => handleDownload(document.id)}
							on:delete={() => handleDelete(document.id)}
						/>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

<style>
	.document-list-container {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.toolbar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.75rem 1rem;
		background: rgba(255, 255, 255, 0.03);
		border-radius: 8px;
	}

	.toolbar-left,
	.toolbar-right {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.document-count {
		font-size: 0.875rem;
		font-weight: 600;
		color: rgba(255, 255, 255, 0.8);
	}

	.selection-count {
		font-size: 0.75rem;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		background: rgba(99, 102, 241, 0.2);
		color: rgba(99, 102, 241, 1);
	}

	.filter-select {
		padding: 0.5rem 0.75rem;
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 6px;
		background: rgba(255, 255, 255, 0.05);
		color: rgba(255, 255, 255, 0.9);
		font-size: 0.875rem;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.filter-select:focus {
		outline: none;
		border-color: rgba(99, 102, 241, 0.5);
		background: rgba(255, 255, 255, 0.08);
	}

	.loading-state,
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 4rem 2rem;
		text-align: center;
		color: rgba(255, 255, 255, 0.6);
	}

	.loading-state .spinner {
		width: 40px;
		height: 40px;
		border: 3px solid rgba(255, 255, 255, 0.1);
		border-top-color: rgba(99, 102, 241, 0.8);
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
		margin-bottom: 1rem;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.empty-state svg {
		color: rgba(255, 255, 255, 0.3);
		margin-bottom: 1rem;
	}

	.empty-state h3 {
		font-size: 1.125rem;
		font-weight: 600;
		color: rgba(255, 255, 255, 0.8);
		margin: 0 0 0.5rem 0;
	}

	.empty-state p {
		margin: 0;
		font-size: 0.875rem;
	}

	.table-container {
		overflow-x: auto;
		border-radius: 8px;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.documents-table {
		width: 100%;
		border-collapse: collapse;
		background: rgba(255, 255, 255, 0.02);
	}

	thead tr {
		border-bottom: 2px solid rgba(255, 255, 255, 0.1);
	}

	th {
		padding: 0.875rem 1rem;
		text-align: left;
		font-size: 0.8125rem;
		font-weight: 600;
		color: rgba(255, 255, 255, 0.7);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.th-checkbox {
		width: 40px;
	}

	.th-checkbox input[type='checkbox'] {
		width: 16px;
		height: 16px;
		cursor: pointer;
	}

	.th-sortable {
		cursor: pointer;
		user-select: none;
		transition: all 0.2s ease;
	}

	.th-sortable:hover {
		color: rgba(255, 255, 255, 0.9);
	}

	.th-sortable.sorted {
		color: rgba(99, 102, 241, 0.9);
	}

	.th-sortable span {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}

	.sort-icon {
		color: rgba(99, 102, 241, 0.9);
		transition: transform 0.2s ease;
	}

	.sort-icon.asc {
		transform: rotate(180deg);
	}

	.th-actions {
		width: 100px;
		text-align: right;
	}
</style>
