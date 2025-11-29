<script lang="ts">
	/**
	 * TopBar - Project selector + theme toggle
	 *
	 * Displayed at top of the application
	 */
	import ProjectSelector from './ProjectSelector.svelte';
	import ThemeToggle from './ThemeToggle.svelte';
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
	<!-- Logo/Brand -->
	<div class="brand">
		<svg class="brand-icon" viewBox="0 0 24 24" fill="none">
			<rect x="3" y="3" width="18" height="18" rx="3" stroke="currentColor" stroke-width="2"/>
			<circle cx="9" cy="10" r="1.5" fill="currentColor"/>
			<circle cx="15" cy="10" r="1.5" fill="currentColor"/>
			<path d="M9 15h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
		</svg>
		<span class="brand-name">GPT-OSS</span>
	</div>

	<!-- Project Selector -->
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

	<!-- Theme Toggle -->
	<ThemeToggle />
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
		height: 56px;
		padding: 0 1rem;
		background: var(--bg-secondary);
		border-bottom: 1px solid var(--border-primary);
		flex-shrink: 0;
	}

	.brand {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: var(--text-primary);
	}

	.brand-icon {
		width: 28px;
		height: 28px;
		color: var(--accent);
	}

	.brand-name {
		font-size: 1.125rem;
		font-weight: 700;
		letter-spacing: -0.02em;
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

	/* Hide brand name on small screens */
	@media (max-width: 768px) {
		.brand-name {
			display: none;
		}
	}

	/* Mobile: make top bar more compact */
	@media (max-width: 640px) {
		.top-bar {
			height: 48px;
			padding: 0 0.75rem;
			gap: 0.5rem;
		}
	}
</style>
