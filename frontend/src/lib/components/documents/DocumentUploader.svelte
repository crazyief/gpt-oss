<script lang="ts">
/**
 * DocumentUploader component
 *
 * Drag-and-drop file upload zone with progress tracking
 *
 * Features:
 * - Drag-and-drop file upload
 * - Click to open file picker
 * - Multiple file selection
 * - File type validation
 * - File size validation (max 200MB per file)
 * - Progress bar for each file
 * - Success/error state per file
 */

import { createEventDispatcher } from 'svelte';
import { documents as documentsApi } from '$lib/services/api';
import { addDocuments } from '$lib/stores/documents';
import { toast } from '$lib/stores/toast';
import type { Document, FailedUpload } from '$lib/types';

// Props
export let projectId: number;
export let maxFileSize = 209715200; // 200MB in bytes
export let allowedTypes = ['.pdf', '.docx', '.xlsx', '.txt', '.md'];
export let maxFiles = 10;

// State
let isDragging = false;
let isUploading = false;
let uploadProgress = new Map<string, number>(); // filename -> progress (0-100)
let fileInput: HTMLInputElement;

const dispatch = createEventDispatcher<{
	upload: Document[];
	error: FailedUpload[];
}>();

// Drag and drop handlers
function handleDragEnter(e: DragEvent) {
	e.preventDefault();
	isDragging = true;
}

function handleDragLeave(e: DragEvent) {
	e.preventDefault();
	isDragging = false;
}

function handleDragOver(e: DragEvent) {
	e.preventDefault();
}

function handleDrop(e: DragEvent) {
	e.preventDefault();
	isDragging = false;

	const files = Array.from(e.dataTransfer?.files || []);
	handleFiles(files);
}

// File picker
function handleFileInputChange(e: Event) {
	const input = e.target as HTMLInputElement;
	const files = Array.from(input.files || []);
	handleFiles(files);

	// Reset input so same file can be selected again
	input.value = '';
}

function openFilePicker() {
	fileInput?.click();
}

// File validation and upload
async function handleFiles(files: File[]) {
	if (files.length === 0) return;

	// Validate file count
	if (files.length > maxFiles) {
		toast.error(`Maximum ${maxFiles} files allowed. Selected ${files.length} files.`);
		return;
	}

	// Validate each file
	const validFiles: File[] = [];
	const errors: FailedUpload[] = [];

	for (const file of files) {
		// Check file size
		if (file.size > maxFileSize) {
			const sizeMB = (file.size / 1024 / 1024).toFixed(2);
			const maxSizeMB = (maxFileSize / 1024 / 1024).toFixed(0);
			errors.push({
				filename: file.name,
				error: `File too large (${sizeMB}MB). Maximum ${maxSizeMB}MB allowed.`
			});
			continue;
		}

		// Check file type
		const extension = `.${file.name.split('.').pop()?.toLowerCase()}`;
		if (!allowedTypes.includes(extension)) {
			errors.push({
				filename: file.name,
				error: `File type not allowed. Allowed: ${allowedTypes.join(', ')}`
			});
			continue;
		}

		validFiles.push(file);
	}

	// Show validation errors
	if (errors.length > 0) {
		dispatch('error', errors);
	}

	// Upload valid files
	if (validFiles.length > 0) {
		await uploadFiles(validFiles);
	}
}

async function uploadFiles(files: File[]) {
	isUploading = true;

	// Initialize progress for each file
	files.forEach((file) => {
		uploadProgress.set(file.name, 0);
	});
	uploadProgress = uploadProgress; // Trigger reactivity

	try {
		// Simulate progress (real progress would require backend support)
		const progressInterval = setInterval(() => {
			files.forEach((file) => {
				const current = uploadProgress.get(file.name) || 0;
				if (current < 90) {
					uploadProgress.set(file.name, current + 10);
				}
			});
			uploadProgress = uploadProgress; // Trigger reactivity
		}, 200);

		// Upload files
		const response = await documentsApi.uploadDocuments(projectId, files);

		clearInterval(progressInterval);

		// Set progress to 100% for successful uploads
		files.forEach((file) => {
			uploadProgress.set(file.name, 100);
		});
		uploadProgress = uploadProgress; // Trigger reactivity

		// Update documents store
		if (response.documents.length > 0) {
			addDocuments(response.documents);
			dispatch('upload', response.documents);
		}

		// Dispatch errors
		if (response.failed.length > 0) {
			dispatch('error', response.failed);
		}

		// Clear progress after delay
		setTimeout(() => {
			uploadProgress.clear();
			uploadProgress = uploadProgress;
		}, 2000);
	} catch (error) {
		const errorMessage = error instanceof Error ? error.message : 'Upload failed';
		toast.error(errorMessage);

		// Clear progress on error
		uploadProgress.clear();
		uploadProgress = uploadProgress;
	} finally {
		isUploading = false;
	}
}

// File type icon helper
function getFileTypeColor(extension: string): string {
	const ext = extension.toLowerCase();
	if (ext === '.pdf') return 'text-red-500';
	if (ext === '.docx') return 'text-blue-500';
	if (ext === '.xlsx') return 'text-green-500';
	if (ext === '.txt') return 'text-gray-500';
	if (ext === '.md') return 'text-purple-500';
	return 'text-gray-400';
}
</script>

<!-- Hidden file input -->
<input
	type="file"
	bind:this={fileInput}
	on:change={handleFileInputChange}
	multiple
	accept={allowedTypes.join(',')}
	class="hidden"
	aria-label="File upload input"
/>

<!-- Drop zone -->
<div
	class="upload-zone"
	class:dragging={isDragging}
	class:uploading={isUploading}
	on:dragenter={handleDragEnter}
	on:dragleave={handleDragLeave}
	on:dragover={handleDragOver}
	on:drop={handleDrop}
	on:click={openFilePicker}
	on:keydown={(e) => e.key === 'Enter' && openFilePicker()}
	role="button"
	tabindex="0"
	aria-label="Upload documents"
>
	<div class="upload-content">
		<!-- Upload icon -->
		<svg
			class="upload-icon"
			width="48"
			height="48"
			viewBox="0 0 48 48"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
		>
			<path
				d="M24 16V32M24 16L18 22M24 16L30 22M40 30V38C40 39.1046 39.1046 40 38 40H10C8.89543 40 8 39.1046 8 38V30"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			/>
		</svg>

		<!-- Upload text -->
		<p class="upload-title">
			{#if isUploading}
				Uploading...
			{:else if isDragging}
				Drop files here
			{:else}
				Drag and drop files or click to browse
			{/if}
		</p>

		<p class="upload-subtitle">
			Supported: {allowedTypes.join(', ')} (max {(maxFileSize / 1024 / 1024).toFixed(0)}MB per file)
		</p>

		<!-- Progress bars -->
		{#if uploadProgress.size > 0}
			<div class="progress-container">
				{#each Array.from(uploadProgress.entries()) as [filename, progress]}
					<div class="progress-item">
						<div class="progress-header">
							<span class="progress-filename">{filename}</span>
							<span class="progress-percent">{progress}%</span>
						</div>
						<div class="progress-bar-bg">
							<div class="progress-bar-fill" style="width: {progress}%"></div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<style>
	.upload-zone {
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 200px;
		padding: 2rem;
		border: 2px dashed rgba(99, 102, 241, 0.3);
		border-radius: 12px;
		background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(139, 92, 246, 0.05));
		cursor: pointer;
		transition: all 0.3s ease;
	}

	.upload-zone:hover {
		border-color: rgba(99, 102, 241, 0.5);
		background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
		transform: scale(1.01);
	}

	.upload-zone.dragging {
		border-color: rgba(99, 102, 241, 0.8);
		background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15));
		transform: scale(1.02);
		box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
	}

	.upload-zone.uploading {
		pointer-events: none;
		opacity: 0.7;
	}

	.upload-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		text-align: center;
	}

	.upload-icon {
		color: rgba(99, 102, 241, 0.7);
		transition: color 0.3s ease;
	}

	.upload-zone:hover .upload-icon,
	.upload-zone.dragging .upload-icon {
		color: rgba(99, 102, 241, 1);
	}

	.upload-title {
		font-size: 1.125rem;
		font-weight: 600;
		color: rgba(255, 255, 255, 0.9);
		margin: 0;
	}

	.upload-subtitle {
		font-size: 0.875rem;
		color: rgba(255, 255, 255, 0.6);
		margin: 0;
	}

	.progress-container {
		width: 100%;
		max-width: 400px;
		margin-top: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.progress-item {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.progress-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.progress-filename {
		font-size: 0.875rem;
		color: rgba(255, 255, 255, 0.8);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		max-width: 300px;
	}

	.progress-percent {
		font-size: 0.75rem;
		font-weight: 600;
		color: rgba(99, 102, 241, 0.9);
	}

	.progress-bar-bg {
		width: 100%;
		height: 6px;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 3px;
		overflow: hidden;
	}

	.progress-bar-fill {
		height: 100%;
		background: linear-gradient(90deg, #6366f1, #8b5cf6);
		border-radius: 3px;
		transition: width 0.3s ease;
	}

	/* Accessibility */
	.upload-zone:focus {
		outline: 2px solid rgba(99, 102, 241, 0.8);
		outline-offset: 2px;
	}
</style>
