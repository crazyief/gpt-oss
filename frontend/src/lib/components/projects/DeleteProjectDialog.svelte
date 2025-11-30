<script lang="ts">
	/**
	 * DeleteProjectDialog - Confirm project deletion with options
	 */
	import { createEventDispatcher } from 'svelte';
	import { projects } from '$lib/stores/projects';
	import { deleteProject } from '$lib/services/api/projects';
	import type { Project } from '$lib/types';
	import type { DeleteProjectAction } from '$lib/types';

	const dispatch = createEventDispatcher();

	export let project: Project;

	let deleteAction: DeleteProjectAction = 'move';
	let isSubmitting = false;
	let errorMessage = '';

	// Calculate counts from project data
	$: conversationCount = project.conversation_count || 0;
	$: documentCount = project.document_count || 0;

	async function handleConfirm() {
		if (isSubmitting) return;

		isSubmitting = true;
		errorMessage = '';

		try {
			await deleteProject(project.id, deleteAction);

			// Remove from store
			projects.removeProject(project.id);

			// Notify parent
			dispatch('deleted', { projectId: project.id, action: deleteAction });
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to delete project';
		} finally {
			isSubmitting = false;
		}
	}

	function handleCancel() {
		dispatch('cancel');
	}
</script>

<div class="dialog-overlay" on:click={handleCancel} data-testid="delete-dialog-overlay">
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="dialog-content" on:click|stopPropagation data-testid="delete-project-dialog">
		<header class="dialog-header">
			<h2>Delete Project</h2>
			<button
				type="button"
				class="close-btn"
				on:click={handleCancel}
				aria-label="Close dialog"
			>
				<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
					<path d="M5 5l10 10M15 5l-10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
				</svg>
			</button>
		</header>

		<div class="dialog-body">
			<p class="warning-text">
				You are about to delete <strong>{project.name}</strong>.
			</p>

			<div class="impact-summary">
				<div class="impact-item">
					<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
						<path d="M17 7l-7 7-7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
					</svg>
					<span>{conversationCount} conversation{conversationCount !== 1 ? 's' : ''}</span>
				</div>
				<div class="impact-item">
					<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
						<path d="M14 2H6a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V4a2 2 0 00-2-2z" stroke="currentColor" stroke-width="2" />
					</svg>
					<span>{documentCount} document{documentCount !== 1 ? 's' : ''}</span>
				</div>
			</div>

			<div class="action-options">
				<label class="option-label">
					<input
						type="radio"
						bind:group={deleteAction}
						value="move"
						data-testid="action-move"
					/>
					<div class="option-content">
						<span class="option-title">Move to Default Project</span>
						<span class="option-description">
							Conversations and documents will be moved to the Default project
						</span>
					</div>
				</label>

				<label class="option-label">
					<input
						type="radio"
						bind:group={deleteAction}
						value="delete"
						data-testid="action-delete"
					/>
					<div class="option-content">
						<span class="option-title">Delete Everything</span>
						<span class="option-description">
							Permanently delete all conversations and documents
						</span>
					</div>
				</label>
			</div>

			{#if errorMessage}
				<div class="error-message" role="alert">
					<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
						<circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="2" />
						<path d="M8 4v5M8 11v1" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
					</svg>
					{errorMessage}
				</div>
			{/if}
		</div>

		<footer class="dialog-footer">
			<button
				type="button"
				class="btn btn-secondary"
				on:click={handleCancel}
				disabled={isSubmitting}
				data-testid="cancel-btn"
			>
				Cancel
			</button>
			<button
				type="button"
				class="btn btn-danger"
				on:click={handleConfirm}
				disabled={isSubmitting}
				data-testid="confirm-btn"
			>
				{#if isSubmitting}
					<div class="spinner"></div>
					Deleting...
				{:else}
					Delete Project
				{/if}
			</button>
		</footer>
	</div>
</div>

<style>
	.dialog-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		animation: fadeIn 0.2s ease;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	.dialog-content {
		width: 90%;
		max-width: 500px;
		background: var(--bg-primary);
		border-radius: 0.75rem;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: slideUp 0.3s ease;
		overflow: hidden;
	}

	@keyframes slideUp {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.dialog-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.5rem;
		border-bottom: 1px solid var(--border-primary);
	}

	.dialog-header h2 {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.close-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		border: none;
		border-radius: 0.375rem;
		background: transparent;
		color: var(--text-secondary);
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.close-btn:hover {
		background: var(--bg-hover);
		color: var(--text-primary);
	}

	.dialog-body {
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.warning-text {
		margin: 0;
		font-size: 0.9375rem;
		color: var(--text-primary);
		line-height: 1.5;
	}

	.impact-summary {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		padding: 1rem;
		background: var(--bg-tertiary);
		border-radius: 0.5rem;
		border: 1px solid var(--border-primary);
	}

	.impact-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-size: 0.875rem;
		color: var(--text-secondary);
	}

	.action-options {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.option-label {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		padding: 1rem;
		border: 2px solid var(--border-primary);
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.option-label:hover {
		border-color: var(--accent);
		background: var(--bg-hover);
	}

	.option-label:has(input:checked) {
		border-color: var(--accent);
		background: var(--accent-muted);
	}

	.option-label input[type='radio'] {
		margin-top: 0.125rem;
		cursor: pointer;
	}

	.option-content {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.option-title {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--text-primary);
	}

	.option-description {
		font-size: 0.75rem;
		color: var(--text-secondary);
	}

	.error-message {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem;
		background: var(--error-bg);
		border: 1px solid var(--error);
		border-radius: 0.5rem;
		color: var(--error);
		font-size: 0.875rem;
	}

	.dialog-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		padding: 1.5rem;
		border-top: 1px solid var(--border-primary);
	}

	.btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 0.75rem 1.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-secondary {
		background: var(--bg-tertiary);
		color: var(--text-primary);
		border: 1px solid var(--border-primary);
	}

	.btn-secondary:hover:not(:disabled) {
		background: var(--bg-hover);
	}

	.btn-danger {
		background: var(--error);
		color: white;
	}

	.btn-danger:hover:not(:disabled) {
		background: var(--error-hover);
		box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
	}

	.spinner {
		width: 16px;
		height: 16px;
		border: 2px solid currentColor;
		border-top-color: transparent;
		border-radius: 50%;
		animation: spin 0.6s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
