<script lang="ts">
/**
 * ProjectSettings component
 *
 * Edit project name and description, with delete functionality
 */

import { createEventDispatcher } from 'svelte';
import type { Project } from '$lib/types';
import DeleteConfirmModal from '../modals/DeleteConfirmModal.svelte';

export let project: Project;

const dispatch = createEventDispatcher<{
	save: { name: string; description: string };
	delete: void;
	cancel: void;
}>();

// Local state
let name = project.name;
let description = project.description || '';
let isSaving = false;
let showDeleteModal = false;

// Validation
$: hasChanges = name !== project.name || description !== (project.description || '');
$: canSave = name.trim().length > 0 && hasChanges;

async function handleSave() {
	if (!canSave) return;

	isSaving = true;
	dispatch('save', { name, description });
	// Parent component will handle the save and update isSaving state
}

function handleCancel() {
	// Reset to original values
	name = project.name;
	description = project.description || '';
	dispatch('cancel');
}

function handleDeleteClick() {
	showDeleteModal = true;
}

function handleDeleteConfirm() {
	dispatch('delete');
	showDeleteModal = false;
}

function handleDeleteCancel() {
	showDeleteModal = false;
}
</script>

<div class="settings-container">
	<!-- Header -->
	<div class="settings-header">
		<h2>Project Settings</h2>
	</div>

	<!-- Form -->
	<form on:submit|preventDefault={handleSave} class="settings-form">
		<!-- Name field -->
		<div class="form-group">
			<label for="project-name" class="form-label">
				Project Name <span class="required">*</span>
			</label>
			<input
				id="project-name"
				type="text"
				bind:value={name}
				class="form-input"
				placeholder="Enter project name"
				maxlength="255"
				required
			/>
		</div>

		<!-- Description field -->
		<div class="form-group">
			<label for="project-description" class="form-label"> Description </label>
			<textarea
				id="project-description"
				bind:value={description}
				class="form-textarea"
				placeholder="Enter project description (optional)"
				rows="4"
				maxlength="1000"
			></textarea>
			<div class="char-count">{description.length}/1000</div>
		</div>

		<!-- Action buttons -->
		<div class="form-actions">
			<button type="button" class="button button-cancel" on:click={handleCancel}>
				Cancel
			</button>
			<button
				type="submit"
				class="button button-save"
				disabled={!canSave || isSaving}
			>
				{isSaving ? 'Saving...' : 'Save Changes'}
			</button>
		</div>
	</form>

	<!-- Danger zone -->
	<div class="danger-zone">
		<div class="danger-header">
			<h3>Danger Zone</h3>
		</div>
		<div class="danger-content">
			<div class="danger-info">
				<p class="danger-title">Delete Project</p>
				<p class="danger-subtitle">
					This will permanently delete the project, all documents, conversations, and messages.
					This action cannot be undone.
				</p>
			</div>
			<button type="button" class="button button-delete" on:click={handleDeleteClick}>
				Delete Project
			</button>
		</div>
	</div>
</div>

<!-- Delete confirmation modal -->
<DeleteConfirmModal
	isOpen={showDeleteModal}
	title="Delete Project"
	message="Are you sure you want to delete '{project.name}'? This will permanently delete all documents, conversations, and messages. This action cannot be undone."
	confirmText="Delete Project"
	requireTyping={project.name}
	on:confirm={handleDeleteConfirm}
	on:cancel={handleDeleteCancel}
/>

<style>
	.settings-container {
		display: flex;
		flex-direction: column;
		gap: 2rem;
		max-width: 800px;
	}

	.settings-header h2 {
		font-size: 1.5rem;
		font-weight: 700;
		color: rgba(255, 255, 255, 0.95);
		margin: 0;
	}

	.settings-form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.form-label {
		font-size: 0.875rem;
		font-weight: 600;
		color: rgba(255, 255, 255, 0.8);
	}

	.required {
		color: rgba(239, 68, 68, 0.9);
	}

	.form-input,
	.form-textarea {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 6px;
		background: rgba(255, 255, 255, 0.05);
		color: rgba(255, 255, 255, 0.9);
		font-size: 0.9375rem;
		font-family: inherit;
		transition: all 0.2s ease;
	}

	.form-input:focus,
	.form-textarea:focus {
		outline: none;
		border-color: rgba(99, 102, 241, 0.5);
		background: rgba(255, 255, 255, 0.08);
	}

	.form-textarea {
		resize: vertical;
		min-height: 100px;
	}

	.char-count {
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.5);
		text-align: right;
	}

	.form-actions {
		display: flex;
		gap: 0.75rem;
		justify-content: flex-end;
	}

	.button {
		padding: 0.625rem 1.25rem;
		border-radius: 6px;
		font-size: 0.9375rem;
		font-weight: 500;
		cursor: pointer;
		border: none;
		transition: all 0.2s ease;
	}

	.button-cancel {
		background: rgba(255, 255, 255, 0.1);
		color: rgba(255, 255, 255, 0.9);
	}

	.button-cancel:hover {
		background: rgba(255, 255, 255, 0.15);
	}

	.button-save {
		background: linear-gradient(135deg, #6366f1, #8b5cf6);
		color: white;
	}

	.button-save:hover:not(:disabled) {
		background: linear-gradient(135deg, #4f46e5, #7c3aed);
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
	}

	.button-save:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.danger-zone {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		padding: 1.5rem;
		border: 1px solid rgba(239, 68, 68, 0.3);
		border-radius: 8px;
		background: rgba(239, 68, 68, 0.05);
	}

	.danger-header h3 {
		font-size: 1rem;
		font-weight: 600;
		color: rgba(239, 68, 68, 0.9);
		margin: 0;
	}

	.danger-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
	}

	.danger-info {
		flex: 1;
	}

	.danger-title {
		font-size: 0.9375rem;
		font-weight: 600;
		color: rgba(255, 255, 255, 0.9);
		margin: 0 0 0.25rem 0;
	}

	.danger-subtitle {
		font-size: 0.8125rem;
		color: rgba(255, 255, 255, 0.6);
		margin: 0;
		line-height: 1.5;
	}

	.button-delete {
		background: linear-gradient(135deg, #ef4444, #dc2626);
		color: white;
		flex-shrink: 0;
	}

	.button-delete:hover {
		background: linear-gradient(135deg, #dc2626, #b91c1c);
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
	}

	.button:focus {
		outline: 2px solid rgba(99, 102, 241, 0.5);
		outline-offset: 2px;
	}

	@media (max-width: 640px) {
		.danger-content {
			flex-direction: column;
			align-items: stretch;
		}

		.button-delete {
			width: 100%;
		}
	}
</style>
