<script lang="ts">
	/**
	 * ProjectsTab - Project management interface
	 *
	 * Layout: Dual-panel with ProjectList (left) and ProjectDetails (right)
	 */
	import ProjectList from '$lib/components/projects/ProjectList.svelte';
	import ProjectDetails from '$lib/components/projects/ProjectDetails.svelte';
	import CreateProjectForm from '$lib/components/projects/CreateProjectForm.svelte';
	import { projects } from '$lib/stores/projects';

	let showCreateForm = false;

	function handleCreateProject() {
		showCreateForm = true;
	}

	function handleProjectCreated() {
		showCreateForm = false;
	}

	function handleCancelCreate() {
		showCreateForm = false;
	}
</script>

<div class="projects-tab" data-testid="projects-tab">
	<div class="projects-layout">
		<!-- Left Panel: Project List -->
		<aside class="project-list-panel">
			<ProjectList on:create={handleCreateProject} />
		</aside>

		<!-- Right Panel: Project Details or Create Form -->
		<main class="project-details-panel">
			{#if showCreateForm}
				<CreateProjectForm
					on:created={handleProjectCreated}
					on:cancel={handleCancelCreate}
				/>
			{:else if $projects.selectedProjectId}
				<ProjectDetails />
			{:else}
				<!-- Empty state -->
				<div class="empty-state">
					<svg class="empty-icon" viewBox="0 0 64 64" fill="none">
						<rect x="8" y="8" width="48" height="48" rx="8" stroke="currentColor" stroke-width="3"/>
						<path d="M22 28h20M22 36h20M22 20h8" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
					</svg>
					<h2>Select a Project</h2>
					<p>Choose a project from the list to view details, or create a new one</p>
				</div>
			{/if}
		</main>
	</div>
</div>

<style>
	.projects-tab {
		display: flex;
		flex-direction: column;
		height: 100%;
		overflow: hidden;
		background: var(--bg-primary);
	}

	.projects-layout {
		display: flex;
		flex: 1;
		overflow: hidden;
	}

	.project-list-panel {
		width: 300px;
		border-right: 1px solid var(--border-primary);
		overflow-y: auto;
		flex-shrink: 0;
	}

	.project-details-panel {
		flex: 1;
		overflow-y: auto;
		background: var(--bg-primary);
	}

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

	.empty-icon {
		width: 80px;
		height: 80px;
		margin-bottom: 1.5rem;
		color: var(--accent);
		opacity: 0.6;
	}

	.empty-state h2 {
		margin: 0 0 0.5rem 0;
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.empty-state p {
		margin: 0;
		font-size: 1rem;
	}

	/* Mobile: single column */
	@media (max-width: 768px) {
		.projects-layout {
			flex-direction: column;
		}

		.project-list-panel {
			width: 100%;
			border-right: none;
			border-bottom: 1px solid var(--border-primary);
			max-height: 40%;
		}

		.project-details-panel {
			display: none; /* Or show as overlay when project selected */
		}

		.projects-layout:has(.project-details-panel:not(.empty-state)) .project-list-panel {
			display: none;
		}

		.projects-layout:has(.project-details-panel:not(.empty-state)) .project-details-panel {
			display: block;
		}
	}
</style>
