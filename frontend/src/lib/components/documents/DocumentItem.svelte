<script lang="ts">
/**
 * DocumentItem component
 *
 * Single row in document table
 */

import { createEventDispatcher } from 'svelte';
import type { Document } from '$lib/types';
import DocumentActions from './DocumentActions.svelte';

export let document: Document;
export let selected = false;

const dispatch = createEventDispatcher<{
	select: boolean;
	delete: void;
	download: void;
}>();

function handleSelect() {
	dispatch('select', !selected);
}

function handleDownload() {
	dispatch('download');
}

function handleDelete() {
	dispatch('delete');
}

// Format file size
function formatFileSize(bytes: number): string {
	if (bytes < 1024) return `${bytes} B`;
	if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
	return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// Format uploaded date (relative time)
function formatRelativeDate(dateString: string): string {
	const date = new Date(dateString);
	const now = new Date();
	const diffMs = now.getTime() - date.getTime();
	const diffMins = Math.floor(diffMs / 60000);
	const diffHours = Math.floor(diffMs / 3600000);
	const diffDays = Math.floor(diffMs / 86400000);

	if (diffMins < 1) return 'just now';
	if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
	if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
	if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
	return date.toLocaleDateString();
}

// Get file extension
function getFileExtension(filename: string): string {
	return `.${filename.split('.').pop()?.toLowerCase() || ''}`;
}

// File type icon color
function getFileTypeColor(extension: string): string {
	const ext = extension.toLowerCase();
	if (ext === '.pdf') return 'text-red-500';
	if (ext === '.docx') return 'text-blue-500';
	if (ext === '.xlsx') return 'text-green-500';
	if (ext === '.txt') return 'text-gray-400';
	if (ext === '.md') return 'text-purple-500';
	return 'text-gray-400';
}

$: fileExtension = getFileExtension(document.original_filename);
$: fileTypeColor = getFileTypeColor(fileExtension);
</script>

<tr class="document-row" class:selected>
	<!-- Checkbox -->
	<td class="cell-checkbox">
		<input
			type="checkbox"
			checked={selected}
			on:change={handleSelect}
			aria-label="Select document"
		/>
	</td>

	<!-- File icon & name -->
	<td class="cell-name">
		<div class="name-container">
			<span class="file-icon {fileTypeColor}">{fileExtension.toUpperCase().slice(1)}</span>
			<span class="filename" title={document.original_filename}>{document.original_filename}</span>
		</div>
	</td>

	<!-- Type -->
	<td class="cell-type">
		<span class="type-badge {fileTypeColor}">{fileExtension.slice(1).toUpperCase()}</span>
	</td>

	<!-- Size -->
	<td class="cell-size">{formatFileSize(document.file_size)}</td>

	<!-- Uploaded -->
	<td class="cell-uploaded" title={new Date(document.uploaded_at).toLocaleString()}>
		{formatRelativeDate(document.uploaded_at)}
	</td>

	<!-- Actions -->
	<td class="cell-actions">
		<DocumentActions
			documentId={document.id}
			on:download={handleDownload}
			on:delete={handleDelete}
		/>
	</td>
</tr>

<style>
	.document-row {
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
		transition: all 0.2s ease;
	}

	.document-row:hover {
		background: rgba(255, 255, 255, 0.03);
	}

	.document-row.selected {
		background: rgba(99, 102, 241, 0.1);
	}

	td {
		padding: 0.75rem 1rem;
		color: rgba(255, 255, 255, 0.8);
		font-size: 0.875rem;
	}

	.cell-checkbox {
		width: 40px;
	}

	.cell-checkbox input[type='checkbox'] {
		width: 16px;
		height: 16px;
		cursor: pointer;
	}

	.cell-name {
		max-width: 300px;
	}

	.name-container {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.file-icon {
		flex-shrink: 0;
		font-size: 0.75rem;
		font-weight: 700;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		background: rgba(255, 255, 255, 0.05);
	}

	.filename {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.cell-type {
		width: 80px;
	}

	.type-badge {
		display: inline-block;
		font-size: 0.75rem;
		font-weight: 600;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		background: rgba(255, 255, 255, 0.08);
	}

	.cell-size {
		width: 100px;
		text-align: right;
	}

	.cell-uploaded {
		width: 150px;
		color: rgba(255, 255, 255, 0.6);
	}

	.cell-actions {
		width: 100px;
		text-align: right;
	}
</style>
