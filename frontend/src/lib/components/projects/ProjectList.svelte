<script lang="ts">
	/**
	 * ProjectList - List of projects with selection
	 */
	import { createEventDispatcher } from 'svelte';
	import { sortedProjects, projects } from '$lib/stores/projects';
	import { getColorHex, getIconEmoji } from '$lib/constants/project';
	import type { ProjectColorName, ProjectIconName } from '$lib/constants/project';

	const dispatch = createEventDispatcher();

	function handleSelectProject(projectId: number) {
		projects.selectProject(projectId);
	}

	function handleCreateProject() {
		dispatch('create');
	}
</script>

<div class="project-list" data-testid="project-list">
	<!-- Create button -->
	<button
		type="button"
		class="create-btn"
		on:click={handleCreateProject}
		data-testid="create-project-btn"
	>
		<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
			<path d="M10 5v10M5 10h10" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
		</svg>
		<span>New Project</span>
	</button>

	<!-- Projects list -->
	<div class="projects-scroll">
		{#each $sortedProjects as project (project.id)}
			{@const isSelected = $projects.selectedProjectId === project.id}
			{@const isDefault = project.is_default}
			{@const colorHex = getColorHex(project.color || 'blue')}
			{@const iconEmoji = getIconEmoji(project.icon || 'folder')}

			<!-- svelte-ignore a11y-click-events-have-key-events -->
			<!-- svelte-ignore a11y-no-static-element-interactions -->
			<div
				class="project-item"
				class:selected={isSelected}
				class:default={isDefault}
				on:click={() => handleSelectProject(project.id)}
				data-testid="project-item-{project.id}"
			>
				<div class="project-icon-wrapper">
					<div class="color-dot" style="background: {colorHex};"></div>
					<span class="project-icon">{iconEmoji}</span>
				</div>
				<div class="project-info">
					<div class="project-name">{project.name}</div>
					<div class="project-counts">
						<span class="count-item">
							💬 {project.conversation_count || 0}
						</span>
						<span class="count-item">
							📄 {project.document_count || 0}
						</span>
					</div>
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	.project-list {
		display: flex;
		flex-direction: column;
		height: 100%;
		background: var(--bg-tertiary);
	}

	.create-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		margin: 1rem;
		padding: 0.75rem 1rem;
		background: var(--accent);
		color: var(--text-inverse);
		border: none;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.create-btn:hover {
		background: var(--accent-hover);
		box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
		transform: translateY(-1px);
	}

	.projects-scroll {
		flex: 1;
		overflow-y: auto;
		padding: 0 0.5rem 0.5rem;
	}

	.project-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem;
		margin-bottom: 0.5rem;
		border-radius: 0.5rem;
		background: var(--bg-secondary);
		border: 1px solid transparent;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.project-item:hover {
		background: var(--bg-hover);
		border-color: var(--border-primary);
	}

	.project-item.selected {
		background: var(--accent-muted);
		border-color: var(--accent);
		box-shadow: 0 0 0 1px var(--accent);
	}

	.project-item.default {
		border-color: var(--border-primary);
		opacity: 0.8;
	}

	.project-icon-wrapper {
		position: relative;
		flex-shrink: 0;
	}

	.color-dot {
		position: absolute;
		top: -2px;
		right: -2px;
		width: 12px;
		height: 12px;
		border-radius: 50%;
		border: 2px solid var(--bg-secondary);
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
	}

	.project-icon {
		font-size: 1.5rem;
		line-height: 1;
		display: block;
	}

	.project-info {
		flex: 1;
		min-width: 0;
	}

	.project-name {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--text-primary);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.project-counts {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-top: 0.25rem;
	}

	.count-item {
		font-size: 0.75rem;
		color: var(--text-muted);
	}
</style>
