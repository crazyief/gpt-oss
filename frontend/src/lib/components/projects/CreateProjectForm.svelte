<script lang="ts">
	/**
	 * CreateProjectForm - Form to create a new project
	 */
	import { createEventDispatcher } from 'svelte';
	import ColorPicker from './ColorPicker.svelte';
	import IconPicker from './IconPicker.svelte';
	import { projects } from '$lib/stores/projects';
	import { createProject } from '$lib/services/api/projects';
	import type { ProjectColorName, ProjectIconName } from '$lib/constants/project';

	const dispatch = createEventDispatcher();

	// Form state
	let name = '';
	let description = '';
	let color: ProjectColorName = 'blue';
	let icon: ProjectIconName = 'folder';
	let isSubmitting = false;
	let errorMessage = '';

	// Validation
	$: isValid = name.trim().length > 0;

	async function handleSubmit() {
		if (!isValid || isSubmitting) return;

		isSubmitting = true;
		errorMessage = '';

		try {
			const newProject = await createProject({
				name: name.trim(),
				description: description.trim() || undefined,
				color,
				icon
			});

			// Add to store
			projects.addProject(newProject);
			projects.selectProject(newProject.id);

			// Notify parent to close form
			dispatch('created', { project: newProject });
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to create project';
		} finally {
			isSubmitting = false;
		}
	}

	function handleCancel() {
		dispatch('cancel');
	}
</script>

<div class="create-project-form" data-testid="create-project-form">
	<header class="form-header">
		<h2>Create New Project</h2>
		<button
			type="button"
			class="close-btn"
			on:click={handleCancel}
			aria-label="Close form"
		>
			<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
				<path d="M5 5l10 10M15 5l-10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
			</svg>
		</button>
	</header>

	<form on:submit|preventDefault={handleSubmit}>
		<!-- Name field -->
		<div class="form-field">
			<label for="project-name" class="field-label">
				Name <span class="required">*</span>
			</label>
			<input
				id="project-name"
				type="text"
				bind:value={name}
				placeholder="Enter project name"
				class="field-input"
				data-testid="project-name-input"
				maxlength="100"
				required
			/>
		</div>

		<!-- Description field -->
		<div class="form-field">
			<label for="project-description" class="field-label">
				Description
			</label>
			<textarea
				id="project-description"
				bind:value={description}
				placeholder="Optional description"
				class="field-textarea"
				data-testid="project-description-input"
				rows="3"
				maxlength="500"
			/>
		</div>

		<!-- Color picker -->
		<ColorPicker bind:selected={color} />

		<!-- Icon picker -->
		<IconPicker bind:selected={icon} />

		<!-- Error message -->
		{#if errorMessage}
			<div class="error-message" role="alert">
				<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
					<circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="2" />
					<path d="M8 4v5M8 11v1" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
				</svg>
				{errorMessage}
			</div>
		{/if}

		<!-- Form actions -->
		<div class="form-actions">
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
				type="submit"
				class="btn btn-primary"
				disabled={!isValid || isSubmitting}
				data-testid="create-btn"
			>
				{#if isSubmitting}
					<div class="spinner"></div>
					Creating...
				{:else}
					Create Project
				{/if}
			</button>
		</div>
	</form>
</div>

<style>
	.create-project-form {
		display: flex;
		flex-direction: column;
		height: 100%;
		background: var(--bg-primary);
		border-radius: 0.75rem;
		overflow: hidden;
	}

	.form-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.5rem;
		border-bottom: 1px solid var(--border-primary);
	}

	.form-header h2 {
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

	form {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		padding: 1.5rem;
		overflow-y: auto;
	}

	.form-field {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.field-label {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--text-secondary);
	}

	.required {
		color: var(--error);
	}

	.field-input,
	.field-textarea {
		padding: 0.75rem;
		font-size: 0.875rem;
		border: 1px solid var(--border-primary);
		border-radius: 0.5rem;
		background: var(--bg-tertiary);
		color: var(--text-primary);
		transition: all 0.2s ease;
	}

	.field-input:focus,
	.field-textarea:focus {
		outline: none;
		border-color: var(--accent);
		box-shadow: 0 0 0 3px var(--accent-muted);
	}

	.field-textarea {
		resize: vertical;
		min-height: 80px;
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

	.form-actions {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		padding-top: 1rem;
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

	.btn-primary {
		background: var(--accent);
		color: var(--text-inverse);
	}

	.btn-primary:hover:not(:disabled) {
		background: var(--accent-hover);
		box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
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
