<script lang="ts">
/**
 * CreateProjectModal component
 *
 * Modal dialog for creating a new project.
 *
 * Features:
 * - Name input (required)
 * - Description textarea (optional)
 * - Loading state during API call
 * - Error display
 * - Keyboard support (Escape to cancel, Enter to submit)
 */

import { createEventDispatcher, onMount } from 'svelte';
import { createProject } from '$lib/services/api/projects';

export let isOpen = false;

let name = '';
let description = '';
let isLoading = false;
let error: string | null = null;
let nameInput: HTMLInputElement;

const dispatch = createEventDispatcher<{
	created: { id: number; name: string };
	cancel: void;
}>();

async function handleSubmit() {
	if (!name.trim()) {
		error = 'Project name is required';
		return;
	}

	try {
		isLoading = true;
		error = null;

		const project = await createProject(name.trim(), description.trim() || undefined);

		dispatch('created', { id: project.id, name: project.name });
		close();
	} catch (err) {
		error = err instanceof Error ? err.message : 'Failed to create project';
	} finally {
		isLoading = false;
	}
}

function handleCancel() {
	dispatch('cancel');
	close();
}

function close() {
	name = '';
	description = '';
	error = null;
}

function handleKeydown(e: KeyboardEvent) {
	if (e.key === 'Escape') {
		handleCancel();
	}
}

function handleFormKeydown(e: KeyboardEvent) {
	if (e.key === 'Enter' && !e.shiftKey && e.target instanceof HTMLInputElement) {
		e.preventDefault();
		handleSubmit();
	}
}

onMount(() => {
	if (isOpen && nameInput) {
		nameInput.focus();
	}
});

$: if (isOpen && nameInput) {
	nameInput.focus();
}
</script>

{#if isOpen}
	<!-- Modal overlay -->
	<div
		class="modal-overlay"
		on:click={handleCancel}
		on:keydown={handleKeydown}
		role="button"
		tabindex="-1"
		aria-label="Close modal"
	>
		<!-- Modal content -->
		<div
			class="modal-content"
			on:click|stopPropagation
			on:keydown|stopPropagation={handleFormKeydown}
			role="dialog"
			aria-modal="true"
			aria-labelledby="modal-title"
		>
			<!-- Modal header -->
			<div class="modal-header">
				<h2 id="modal-title" class="modal-title">Create New Project</h2>
				<button
					type="button"
					class="close-button"
					on:click={handleCancel}
					aria-label="Close dialog"
				>
					<svg
						width="20"
						height="20"
						viewBox="0 0 20 20"
						fill="none"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							d="M15 5L5 15M5 5l10 10"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
						/>
					</svg>
				</button>
			</div>

			<!-- Modal body -->
			<div class="modal-body">
				{#if error}
					<div class="error-message" role="alert">
						{error}
					</div>
				{/if}

				<div class="form-group">
					<label for="project-name" class="form-label">
						Project Name <span class="required">*</span>
					</label>
					<input
						bind:this={nameInput}
						id="project-name"
						type="text"
						bind:value={name}
						class="form-input"
						placeholder="e.g., IEC 62443 Analysis"
						disabled={isLoading}
						maxlength="100"
					/>
				</div>

				<div class="form-group">
					<label for="project-description" class="form-label"> Description </label>
					<textarea
						id="project-description"
						bind:value={description}
						class="form-textarea"
						placeholder="Optional: Describe the purpose of this project"
						disabled={isLoading}
						rows="3"
						maxlength="500"
					></textarea>
				</div>
			</div>

			<!-- Modal footer -->
			<div class="modal-footer">
				<button
					type="button"
					class="button button-cancel"
					on:click={handleCancel}
					disabled={isLoading}
				>
					Cancel
				</button>
				<button
					type="button"
					class="button button-create"
					disabled={isLoading || !name.trim()}
					on:click={handleSubmit}
				>
					{#if isLoading}
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
						Creating...
					{:else}
						Create Project
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		backdrop-filter: blur(4px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		animation: fadeIn 0.2s ease-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	.modal-content {
		background: white;
		border-radius: 12px;
		max-width: 500px;
		width: 90%;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
		animation: slideUp 0.3s ease-out;
	}

	@keyframes slideUp {
		from {
			transform: translateY(20px);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.25rem 1.5rem;
		border-bottom: 1px solid #e5e7eb;
	}

	.modal-title {
		font-size: 1.25rem;
		font-weight: 600;
		color: #111827;
		margin: 0;
	}

	.close-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		border: none;
		border-radius: 6px;
		background: transparent;
		color: #6b7280;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.close-button:hover {
		background: #f3f4f6;
		color: #111827;
	}

	.modal-body {
		padding: 1.5rem;
	}

	.error-message {
		padding: 0.75rem 1rem;
		background: #fef2f2;
		border: 1px solid #fecaca;
		border-radius: 6px;
		color: #dc2626;
		font-size: 0.875rem;
		margin-bottom: 1rem;
	}

	.form-group {
		margin-bottom: 1rem;
	}

	.form-group:last-child {
		margin-bottom: 0;
	}

	.form-label {
		display: block;
		font-size: 0.875rem;
		font-weight: 500;
		color: #374151;
		margin-bottom: 0.5rem;
	}

	.required {
		color: #dc2626;
	}

	.form-input,
	.form-textarea {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 0.9375rem;
		color: #111827;
		background: #f9fafb;
		transition: all 0.2s ease;
		box-sizing: border-box;
	}

	.form-input:focus,
	.form-textarea:focus {
		outline: none;
		border-color: #3b82f6;
		background: white;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	.form-input:disabled,
	.form-textarea:disabled {
		background: #f3f4f6;
		color: #9ca3af;
		cursor: not-allowed;
	}

	.form-textarea {
		resize: vertical;
		min-height: 80px;
	}

	.modal-footer {
		display: flex;
		gap: 0.75rem;
		padding: 1.25rem 1.5rem;
		border-top: 1px solid #e5e7eb;
		justify-content: flex-end;
	}

	.button {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 0.625rem 1.25rem;
		border-radius: 6px;
		font-size: 0.9375rem;
		font-weight: 500;
		cursor: pointer;
		border: none;
		transition: all 0.2s ease;
	}

	.button-cancel {
		background: #f3f4f6;
		color: #374151;
	}

	.button-cancel:hover:not(:disabled) {
		background: #e5e7eb;
	}

	.button-create {
		background: #3b82f6;
		color: white;
	}

	.button-create:hover:not(:disabled) {
		background: #2563eb;
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
	}

	.button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}

	.button:focus {
		outline: 2px solid rgba(59, 130, 246, 0.5);
		outline-offset: 2px;
	}

	.spinner {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}
</style>
