<script lang="ts">
	/**
	 * IconPicker - Select project icon from 8 preset icons
	 */
	import { PROJECT_ICONS, type ProjectIconName } from '$lib/constants/project';

	export let selected: ProjectIconName = 'folder';
</script>

<div class="icon-picker" data-testid="icon-picker">
	<label class="picker-label">Icon</label>
	<div class="icon-grid">
		{#each PROJECT_ICONS as icon}
			<button
				type="button"
				class="icon-button"
				class:selected={selected === icon.name}
				on:click={() => (selected = icon.name)}
				aria-label={icon.label}
				data-testid="icon-{icon.name}"
			>
				<span class="icon-emoji">{icon.emoji}</span>
			</button>
		{/each}
	</div>
</div>

<style>
	.icon-picker {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.picker-label {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--text-secondary);
	}

	.icon-grid {
		display: grid;
		grid-template-columns: repeat(8, 1fr);
		gap: 0.5rem;
	}

	.icon-button {
		position: relative;
		width: 44px;
		height: 44px;
		border: 2px solid var(--border-primary);
		border-radius: 0.5rem;
		background: var(--bg-tertiary);
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.icon-button:hover {
		background: var(--bg-hover);
		border-color: var(--accent);
		transform: scale(1.05);
	}

	.icon-button.selected {
		background: var(--accent-muted);
		border-color: var(--accent);
		box-shadow: 0 0 0 2px var(--accent-muted);
	}

	.icon-emoji {
		font-size: 1.5rem;
		line-height: 1;
	}

	@media (max-width: 640px) {
		.icon-grid {
			grid-template-columns: repeat(4, 1fr);
		}
	}
</style>
