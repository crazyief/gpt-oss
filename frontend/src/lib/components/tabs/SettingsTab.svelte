<script lang="ts">
	/**
	 * SettingsTab - Project settings and management
	 *
	 * Features:
	 * - Project name editing
	 * - Project deletion
	 * - Project statistics
	 */
	import { currentProjectId } from '$lib/stores/projects';
	import { conversations } from '$lib/stores/conversations';
	import { fetchProject, updateProject, deleteProject } from '$lib/services/api/projects';
	import { toast } from '$lib/stores/toast';
	import { activeTab } from '$lib/stores/navigation';
	import type { Project } from '$lib/types';
	import { onMount } from 'svelte';

	let project: Project | null = null;
	let isLoading = true;
	let isSaving = false;
	let isDeleting = false;
	let editedName = '';
	let showDeleteConfirm = false;

	// Load project data
	async function loadProject() {
		if ($currentProjectId === null) return;

		isLoading = true;
		try {
			project = await fetchProject($currentProjectId);
			editedName = project.name;
		} catch (error) {
			toast.error('Failed to load project settings');
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		loadProject();
	});

	// Reload when project changes
	$: if ($currentProjectId !== null) {
		loadProject();
	}

	async function handleSave() {
		if (!project || !editedName.trim()) return;

		isSaving = true;
		try {
			await updateProject(project.id, { name: editedName.trim() });
			project.name = editedName.trim();
			toast.success('Project updated successfully');
		} catch (error) {
			toast.error('Failed to update project');
		} finally {
			isSaving = false;
		}
	}

	async function handleDelete() {
		if (!project) return;

		isDeleting = true;
		try {
			await deleteProject(project.id);
			toast.success('Project deleted successfully');

			// Clear state and navigate away
			currentProjectId.set(null);
			conversations.setConversations([]);
			activeTab.setTab('chat');
		} catch (error) {
			toast.error('Failed to delete project');
		} finally {
			isDeleting = false;
			showDeleteConfirm = false;
		}
	}

	$: hasChanges = project && editedName.trim() !== project.name;
</script>

<div class="settings-tab">
	<header class="settings-header">
		<h2 class="settings-title">
			<svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
				<path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
			</svg>
			Project Settings
		</h2>
	</header>

	<div class="settings-content">
		{#if isLoading}
			<div class="loading-state">
				<div class="spinner"></div>
				<p>Loading settings...</p>
			</div>
		{:else if project}
			<!-- Project Name -->
			<section class="settings-section">
				<h3 class="section-title">Project Name</h3>
				<div class="input-group">
					<input
						type="text"
						class="text-input"
						bind:value={editedName}
						placeholder="Enter project name"
					/>
					<button
						class="save-btn"
						on:click={handleSave}
						disabled={!hasChanges || isSaving}
					>
						{isSaving ? 'Saving...' : 'Save'}
					</button>
				</div>
			</section>

			<!-- Project Info -->
			<section class="settings-section">
				<h3 class="section-title">Project Information</h3>
				<dl class="info-list">
					<div class="info-item">
						<dt>Created</dt>
						<dd>{new Date(project.created_at).toLocaleDateString()}</dd>
					</div>
					<div class="info-item">
						<dt>Last Updated</dt>
						<dd>{new Date(project.updated_at).toLocaleDateString()}</dd>
					</div>
				</dl>
			</section>

			<!-- Danger Zone -->
			<section class="settings-section danger-zone">
				<h3 class="section-title danger">Danger Zone</h3>
				<p class="danger-text">
					Deleting this project will permanently remove all conversations and documents.
					This action cannot be undone.
				</p>
				{#if showDeleteConfirm}
					<div class="delete-confirm">
						<p>Are you sure you want to delete "{project.name}"?</p>
						<div class="confirm-buttons">
							<button
								class="cancel-btn"
								on:click={() => (showDeleteConfirm = false)}
								disabled={isDeleting}
							>
								Cancel
							</button>
							<button
								class="confirm-delete-btn"
								on:click={handleDelete}
								disabled={isDeleting}
							>
								{isDeleting ? 'Deleting...' : 'Yes, Delete Project'}
							</button>
						</div>
					</div>
				{:else}
					<button
						class="delete-btn"
						on:click={() => (showDeleteConfirm = true)}
					>
						Delete Project
					</button>
				{/if}
			</section>
		{:else}
			<div class="empty-state">
				<p>No project selected</p>
			</div>
		{/if}
	</div>
</div>

<style>
	.settings-tab {
		display: flex;
		flex-direction: column;
		height: 100%;
		background: var(--bg-primary);
		overflow: hidden;
	}

	.settings-header {
		display: flex;
		align-items: center;
		padding: 1rem 1.5rem;
		border-bottom: 1px solid var(--border-primary);
		flex-shrink: 0;
	}

	.settings-title {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.title-icon {
		width: 24px;
		height: 24px;
		color: var(--accent);
	}

	.settings-content {
		flex: 1;
		overflow-y: auto;
		padding: 1.5rem;
	}

	.settings-section {
		margin-bottom: 2rem;
		padding: 1.5rem;
		background: var(--bg-secondary);
		border: 1px solid var(--border-primary);
		border-radius: 0.75rem;
	}

	.section-title {
		margin: 0 0 1rem 0;
		font-size: 1rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.input-group {
		display: flex;
		gap: 0.75rem;
	}

	.text-input {
		flex: 1;
		padding: 0.75rem 1rem;
		background: var(--bg-input);
		border: 1px solid var(--border-primary);
		border-radius: 0.5rem;
		color: var(--text-primary);
		font-size: 0.875rem;
		transition: border-color 0.2s ease;
	}

	.text-input:focus {
		outline: none;
		border-color: var(--accent);
	}

	.save-btn {
		padding: 0.75rem 1.5rem;
		background: var(--accent);
		color: var(--text-inverse);
		border: none;
		border-radius: 0.5rem;
		font-weight: 500;
		cursor: pointer;
		transition: background 0.2s ease;
	}

	.save-btn:hover:not(:disabled) {
		background: var(--accent-hover);
	}

	.save-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.info-list {
		margin: 0;
		display: grid;
		gap: 0.75rem;
	}

	.info-item {
		display: flex;
		justify-content: space-between;
		padding: 0.5rem 0;
		border-bottom: 1px solid var(--border-secondary);
	}

	.info-item dt {
		color: var(--text-secondary);
		font-size: 0.875rem;
	}

	.info-item dd {
		margin: 0;
		color: var(--text-primary);
		font-size: 0.875rem;
	}

	/* Danger Zone */
	.danger-zone {
		border-color: var(--error);
	}

	.section-title.danger {
		color: var(--error);
	}

	.danger-text {
		margin: 0 0 1rem 0;
		font-size: 0.875rem;
		color: var(--text-secondary);
	}

	.delete-btn {
		padding: 0.75rem 1.5rem;
		background: transparent;
		color: var(--error);
		border: 1px solid var(--error);
		border-radius: 0.5rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.delete-btn:hover {
		background: var(--error);
		color: white;
	}

	.delete-confirm {
		padding: 1rem;
		background: rgba(239, 68, 68, 0.1);
		border-radius: 0.5rem;
	}

	.delete-confirm p {
		margin: 0 0 1rem 0;
		color: var(--text-primary);
	}

	.confirm-buttons {
		display: flex;
		gap: 0.75rem;
	}

	.cancel-btn {
		padding: 0.5rem 1rem;
		background: var(--bg-tertiary);
		color: var(--text-primary);
		border: 1px solid var(--border-primary);
		border-radius: 0.5rem;
		cursor: pointer;
	}

	.confirm-delete-btn {
		padding: 0.5rem 1rem;
		background: var(--error);
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-weight: 500;
		cursor: pointer;
	}

	.confirm-delete-btn:disabled,
	.cancel-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* Loading & Empty States */
	.loading-state,
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 200px;
		color: var(--text-secondary);
	}

	.spinner {
		width: 32px;
		height: 32px;
		border: 3px solid var(--border-primary);
		border-top-color: var(--accent);
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
		margin-bottom: 1rem;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
