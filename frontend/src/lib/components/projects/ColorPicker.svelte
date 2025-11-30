<script lang="ts">
	/**
	 * ColorPicker - Select project color from 8 preset colors
	 */
	import { PROJECT_COLORS, type ProjectColorName } from '$lib/constants/project';

	export let selected: ProjectColorName = 'blue';
</script>

<div class="color-picker" data-testid="color-picker">
	<label class="picker-label">Color</label>
	<div class="color-grid">
		{#each PROJECT_COLORS as color}
			<button
				type="button"
				class="color-dot"
				class:selected={selected === color.name}
				style="background: {color.hex};"
				on:click={() => (selected = color.name)}
				aria-label={color.label}
				data-testid="color-{color.name}"
			>
				{#if selected === color.name}
					<svg class="check-icon" viewBox="0 0 16 16" fill="none">
						<path d="M3 8l3 3 7-7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
					</svg>
				{/if}
			</button>
		{/each}
	</div>
</div>

<style>
	.color-picker {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.picker-label {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--text-secondary);
	}

	.color-grid {
		display: grid;
		grid-template-columns: repeat(8, 1fr);
		gap: 0.5rem;
	}

	.color-dot {
		position: relative;
		width: 36px;
		height: 36px;
		border: 2px solid transparent;
		border-radius: 50%;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.color-dot:hover {
		transform: scale(1.1);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
	}

	.color-dot.selected {
		border-color: var(--text-primary);
		box-shadow: 0 0 0 2px var(--bg-primary), 0 0 0 4px currentColor;
	}

	.check-icon {
		width: 16px;
		height: 16px;
		filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
	}

	@media (max-width: 640px) {
		.color-grid {
			grid-template-columns: repeat(4, 1fr);
		}
	}
</style>
