<script lang="ts">
	/**
	 * ThemeToggle - Cycle through themes with visual feedback
	 *
	 * Themes: dark -> matrix -> light -> dark
	 */
	import { theme, themeNames, themeIcons, type Theme } from '$lib/stores/theme';

	function handleClick() {
		theme.cycle();
	}

	// Get next theme for tooltip
	function getNextTheme(current: Theme): Theme {
		const themes: Theme[] = ['dark', 'matrix', 'light'];
		const idx = themes.indexOf(current);
		return themes[(idx + 1) % themes.length];
	}
</script>

<button
	type="button"
	class="theme-toggle"
	on:click={handleClick}
	title="Switch to {themeNames[getNextTheme($theme)]} theme"
	aria-label="Current theme: {themeNames[$theme]}. Click to switch."
>
	<span class="theme-icon">{themeIcons[$theme]}</span>
	<span class="theme-label">{themeNames[$theme]}</span>
</button>

<style>
	.theme-toggle {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		background: var(--bg-tertiary);
		border: 1px solid var(--border-primary);
		border-radius: 0.5rem;
		color: var(--text-primary);
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.theme-toggle:hover {
		background: var(--bg-hover);
		border-color: var(--accent);
		transform: scale(1.02);
	}

	.theme-toggle:active {
		transform: scale(0.98);
	}

	.theme-icon {
		font-size: 1rem;
	}

	.theme-label {
		color: var(--text-secondary);
	}

	/* Hide label on small screens */
	@media (max-width: 640px) {
		.theme-label {
			display: none;
		}

		.theme-toggle {
			padding: 0.5rem;
		}
	}
</style>
