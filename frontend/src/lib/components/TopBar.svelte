<script lang="ts">
	/**
	 * TopBar - Project selector (compact)
	 *
	 * Displayed at top of the application
	 * Theme toggle moved to VerticalNav for more chat space
	 */
	import ProjectSelector from './ProjectSelector.svelte';
	import CreateProjectModal from './modals/CreateProjectModal.svelte';
	import { currentProjectId } from '$lib/stores/projects';

	// State for Create Project modal
	let showCreateProjectModal = false;

	function handleProjectCreated(event: CustomEvent<{ id: number; name: string }>) {
		showCreateProjectModal = false;
		currentProjectId.set(event.detail.id);
	}
</script>

<header class="top-bar">
	<!-- Project Selector (moved left, no brand text) -->
	<div class="project-section">
		<ProjectSelector />
		<button
			type="button"
			class="new-project-btn"
			on:click={() => (showCreateProjectModal = true)}
			aria-label="Create new project"
			title="Create new project"
		>
			<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
				<path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
			</svg>
		</button>
	</div>

	<!-- Spacer -->
	<div class="spacer"></div>
</header>

<!-- Create Project Modal -->
<CreateProjectModal
	isOpen={showCreateProjectModal}
	on:created={handleProjectCreated}
	on:cancel={() => (showCreateProjectModal = false)}
/>

<style>
	.top-bar {
		display: flex;
		align-items: center;
		gap: 1rem;
		height: 48px;
		padding: 0 1rem;
		background: var(--bg-secondary);
		border-bottom: 1px solid var(--border-primary);
		flex-shrink: 0;
	}

	.project-section {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.new-project-btn {
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

	.new-project-btn:hover {
		background: var(--accent);
		border-color: var(--accent);
		color: var(--text-inverse);
		transform: scale(1.05);
	}

	.new-project-btn:active {
		transform: scale(0.95);
	}

	.spacer {
		flex: 1;
	}

	/* Mobile: make top bar more compact */
	@media (max-width: 640px) {
		.top-bar {
			height: 44px;
			padding: 0 0.75rem;
			gap: 0.5rem;
		}
	}
</style>
