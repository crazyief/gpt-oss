<script lang="ts">
	/**
	 * ProjectDetails - Show project details with conversations and documents
	 */
	import { onMount } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import { projects } from '$lib/stores/projects';
	import { activeTab, navigationSource } from '$lib/stores/navigation';
	import { currentConversationId } from '$lib/stores/conversations';
	import { getProjectDetails } from '$lib/services/api/projects';
	import { getColorHex, getIconEmoji } from '$lib/constants/project';
	import type { ProjectColorName, ProjectIconName } from '$lib/constants/project';
	import EditProjectForm from './EditProjectForm.svelte';
	import DeleteProjectDialog from './DeleteProjectDialog.svelte';

	const dispatch = createEventDispatcher();

	let isLoading = false;
	let errorMessage = '';
	let showEditForm = false;
	let showDeleteDialog = false;

	$: selectedProjectId = $projects.selectedProjectId;
	$: projectDetails = $projects.projectDetails;
	$: project = projectDetails?.project;

	// Load project details when selection changes
	$: if (selectedProjectId !== null && !showEditForm) {
		loadDetails(selectedProjectId);
	}

	async function loadDetails(projectId: number) {
		isLoading = true;
		errorMessage = '';

		try {
			const details = await getProjectDetails(projectId);
			projects.setProjectDetails(details);
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Failed to load project details';
		} finally {
			isLoading = false;
		}
	}

	function handleEdit() {
		showEditForm = true;
	}

	function handleDelete() {
		showDeleteDialog = true;
	}

	function handleEditUpdated() {
		showEditForm = false;
		// Reload details to get fresh data
		if (selectedProjectId !== null) {
			loadDetails(selectedProjectId);
		}
	}

	function handleEditCancel() {
		showEditForm = false;
	}

	function handleDeleteConfirmed() {
		showDeleteDialog = false;
		projects.selectProject(null);
	}

	function handleDeleteCancel() {
		showDeleteDialog = false;
	}

	function navigateToConversation(conversationId: number) {
		currentConversationId.set(conversationId);
		navigationSource.set('projects'); // Track that we came from projects
		activeTab.setTab('chat');
	}

	function navigateToDocuments() {
		navigationSource.set('projects'); // Track that we came from projects
		activeTab.setTab('documents');
	}

	onMount(() => {
		if (selectedProjectId !== null) {
			loadDetails(selectedProjectId);
		}
	});
</script>

{#if showEditForm && project}
	<EditProjectForm
		{project}
		on:updated={handleEditUpdated}
		on:cancel={handleEditCancel}
	/>
{:else if isLoading}
	<div class="loading-state">
		<div class="spinner"></div>
		<p>Loading project details...</p>
	</div>
{:else if errorMessage}
	<div class="error-state">
		<svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
			<circle cx="12" cy="12" r="10" />
			<line x1="12" y1="8" x2="12" y2="12" />
			<line x1="12" y1="16" x2="12.01" y2="16" />
		</svg>
		<p>{errorMessage}</p>
	</div>
{:else if projectDetails && project}
	{@const colorHex = getColorHex(project.color || 'blue')}
	{@const iconEmoji = getIconEmoji(project.icon || 'folder')}
	{@const isDefault = project.is_default}

	<div class="project-details" data-testid="project-details">
		<!-- Header -->
		<header class="details-header">
			<div class="header-icon" style="background: {colorHex};">
				<span class="icon-emoji">{iconEmoji}</span>
			</div>
			<div class="header-info">
				<h2 class="project-name">{project.name}</h2>
				{#if project.description}
					<p class="project-description">{project.description}</p>
				{/if}
			</div>
			<div class="header-actions">
				<button
					type="button"
					class="action-btn"
					on:click={handleEdit}
					aria-label="Edit project"
					data-testid="edit-btn"
				>
					<svg width="18" height="18" viewBox="0 0 18 18" fill="none">
						<path d="M12.5 1.5l4 4-10 10H2.5v-4z" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
					</svg>
				</button>
				{#if !isDefault}
					<button
						type="button"
						class="action-btn danger"
						on:click={handleDelete}
						aria-label="Delete project"
						data-testid="delete-btn"
					>
						<svg width="18" height="18" viewBox="0 0 18 18" fill="none">
							<path d="M3 4h12M7 4V3a1 1 0 011-1h2a1 1 0 011 1v1M14 4v10a2 2 0 01-2 2H6a2 2 0 01-2-2V4" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
						</svg>
					</button>
				{/if}
			</div>
		</header>

		<!-- Content -->
		<div class="details-content">
			<!-- Conversations section -->
			<section class="details-section">
				<h3 class="section-title">
					Conversations ({projectDetails.conversations.length})
				</h3>
				{#if projectDetails.conversations.length === 0}
					<p class="empty-text">No conversations yet</p>
				{:else}
					<div class="item-list">
						{#each projectDetails.conversations as conversation}
							<button
								type="button"
								class="list-item"
								on:click={() => navigateToConversation(conversation.id)}
								data-testid="conversation-{conversation.id}"
							>
								<div class="item-info">
									<span class="item-title">{conversation.title}</span>
									<span class="item-meta">
										{conversation.message_count} messages
									</span>
								</div>
								<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
									<path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
								</svg>
							</button>
						{/each}
					</div>
				{/if}
			</section>

			<!-- Documents section -->
			<section class="details-section">
				<h3 class="section-title">
					Documents ({projectDetails.documents.length})
				</h3>
				{#if projectDetails.documents.length === 0}
					<p class="empty-text">No documents yet</p>
				{:else}
					<div class="item-list">
						{#each projectDetails.documents as document}
							<button
								type="button"
								class="list-item"
								on:click={navigateToDocuments}
								data-testid="document-{document.id}"
							>
								<div class="item-info">
									<span class="item-title">{document.original_filename}</span>
									<span class="item-meta">
										{(document.file_size / 1024).toFixed(1)} KB
									</span>
								</div>
								<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
									<path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
								</svg>
							</button>
						{/each}
					</div>
				{/if}
			</section>
		</div>
	</div>
{:else}
	<div class="empty-state">
		<svg class="empty-icon" viewBox="0 0 64 64" fill="none">
			<rect x="8" y="8" width="48" height="48" rx="8" stroke="currentColor" stroke-width="3"/>
		</svg>
		<h3>Select a project</h3>
		<p>Choose a project from the list to view details</p>
	</div>
{/if}

{#if showDeleteDialog && project}
	<DeleteProjectDialog
		{project}
		on:deleted={handleDeleteConfirmed}
		on:cancel={handleDeleteCancel}
	/>
{/if}

<style>
	.project-details {
		display: flex;
		flex-direction: column;
		height: 100%;
		overflow: hidden;
	}

	.details-header {
		display: flex;
		align-items: flex-start;
		gap: 1rem;
		padding: 1.5rem;
		border-bottom: 1px solid var(--border-primary);
	}

	.header-icon {
		width: 64px;
		height: 64px;
		border-radius: 1rem;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		flex-shrink: 0;
	}

	.icon-emoji {
		font-size: 2rem;
		line-height: 1;
	}

	.header-info {
		flex: 1;
		min-width: 0;
	}

	.project-name {
		margin: 0 0 0.5rem 0;
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.project-description {
		margin: 0;
		font-size: 0.875rem;
		color: var(--text-secondary);
		line-height: 1.5;
	}

	.header-actions {
		display: flex;
		gap: 0.5rem;
	}

	.action-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		border: 1px solid var(--border-primary);
		border-radius: 0.5rem;
		background: var(--bg-tertiary);
		color: var(--text-secondary);
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.action-btn:hover {
		background: var(--bg-hover);
		border-color: var(--accent);
		color: var(--accent);
	}

	.action-btn.danger:hover {
		background: var(--error-bg);
		border-color: var(--error);
		color: var(--error);
	}

	.details-content {
		flex: 1;
		overflow-y: auto;
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.details-section {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.section-title {
		margin: 0;
		font-size: 0.875rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-muted);
	}

	.empty-text {
		margin: 0;
		padding: 1rem;
		text-align: center;
		font-size: 0.875rem;
		color: var(--text-muted);
		background: var(--bg-tertiary);
		border-radius: 0.5rem;
	}

	.item-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.list-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.75rem 1rem;
		background: var(--bg-tertiary);
		border: 1px solid var(--border-primary);
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.2s ease;
		text-align: left;
	}

	.list-item:hover {
		background: var(--bg-hover);
		border-color: var(--accent);
	}

	.item-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		flex: 1;
		min-width: 0;
	}

	.item-title {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--text-primary);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.item-meta {
		font-size: 0.75rem;
		color: var(--text-muted);
	}

	.loading-state,
	.error-state,
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		padding: 2rem;
		text-align: center;
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
		to {
			transform: rotate(360deg);
		}
	}

	.error-icon,
	.empty-icon {
		width: 64px;
		height: 64px;
		margin-bottom: 1rem;
		opacity: 0.5;
	}

	.empty-state h3 {
		margin: 0 0 0.5rem 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.empty-state p {
		margin: 0;
		font-size: 0.875rem;
	}
</style>
