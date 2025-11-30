<script lang="ts">
	/**
	 * VerticalNav - Vertical icon tab navigation with accessibility
	 *
	 * Features:
	 * - Inline SVG icons for reliability
	 * - ARIA tab pattern for screen readers
	 * - Keyboard navigation (Arrow keys, Home, End)
	 * - Visible focus indicators
	 * - Theme toggle at bottom
	 */
	import { activeTab, type Tab } from '$lib/stores/navigation';
	import { currentProjectId } from '$lib/stores/projects';
	import { sidebarOpen } from '$lib/stores/sidebar';
	import ThemeToggle from './ThemeToggle.svelte';

	const tabs: Tab[] = ['projects', 'chat', 'documents', 'settings'];

	// Track last click time for double-click detection
	let lastClickTime = 0;
	let lastClickTab: Tab | null = null;
	const DOUBLE_CLICK_THRESHOLD = 300; // ms

	function handleTabClick(tab: Tab) {
		const now = Date.now();
		const timeSinceLastClick = now - lastClickTime;
		const isProjectSelected = $currentProjectId !== null;

		// Check for double-click on the SAME active tab
		if (lastClickTab === tab &&
		    timeSinceLastClick < DOUBLE_CLICK_THRESHOLD &&
		    $activeTab === tab) {
			// Double-click detected on active tab - return to chat (unless already on chat)
			if (tab !== 'chat') {
				setTab('chat');
			}
			// Reset tracking
			lastClickTime = 0;
			lastClickTab = null;
			return;
		}

		// Single click - update tracking
		lastClickTime = now;
		lastClickTab = tab;

		// Only navigate if allowed (chat and projects are always allowed, others need project selected)
		if (tab === 'chat' || tab === 'projects' || isProjectSelected) {
			setTab(tab);
		}
	}

	function setTab(tab: Tab) {
		activeTab.setTab(tab);
		// When switching to chat tab, ensure sidebar is open
		if (tab === 'chat') {
			sidebarOpen.open();
		}
	}


	// Keyboard navigation for tabs
	function handleKeyDown(event: KeyboardEvent, currentTab: Tab) {
		const currentIndex = tabs.indexOf(currentTab);
		let newIndex: number;

		switch (event.key) {
			case 'ArrowDown':
			case 'ArrowRight':
				event.preventDefault();
				newIndex = (currentIndex + 1) % tabs.length;
				break;
			case 'ArrowUp':
			case 'ArrowLeft':
				event.preventDefault();
				newIndex = (currentIndex - 1 + tabs.length) % tabs.length;
				break;
			case 'Home':
				event.preventDefault();
				newIndex = 0;
				break;
			case 'End':
				event.preventDefault();
				newIndex = tabs.length - 1;
				break;
			default:
				return;
		}

		const newTab = tabs[newIndex];
		// Skip disabled tabs when navigating
		if (newTab !== 'chat' && !isProjectSelected) {
			// Find next enabled tab
			for (let i = 0; i < tabs.length; i++) {
				const idx = (newIndex + i) % tabs.length;
				if (tabs[idx] === 'chat' || isProjectSelected) {
					setTab(tabs[idx]);
					break;
				}
			}
		} else {
			setTab(newTab);
		}
	}

	// Disable documents/settings when no project selected
	$: isProjectSelected = $currentProjectId !== null;

</script>

<nav class="vertical-nav" aria-label="Main navigation">
	<div class="tablist" role="tablist" aria-orientation="vertical">
		<!-- Projects Tab -->
		<button
			type="button"
			class="nav-item"
			class:active={$activeTab === 'projects'}
			on:click={() => handleTabClick('projects')}
			on:keydown={(e) => handleKeyDown(e, 'projects')}
			role="tab"
			id="projects-tab"
			aria-selected={$activeTab === 'projects'}
			aria-controls="projects-panel"
			tabindex={$activeTab === 'projects' ? 0 : -1}
			data-testid="nav-projects"
		>
			<!-- Folder icon -->
			<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
			</svg>
			<span class="nav-tooltip">Projects</span>
		</button>

		<!-- Chat Tab -->
		<button
			type="button"
			class="nav-item"
			class:active={$activeTab === 'chat'}
			on:click={() => handleTabClick('chat')}
			on:keydown={(e) => handleKeyDown(e, 'chat')}
			role="tab"
			id="chat-tab"
			aria-selected={$activeTab === 'chat'}
			aria-controls="chat-panel"
			tabindex={$activeTab === 'chat' ? 0 : -1}
		>
			<!-- Chat/Message icon -->
			<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
			</svg>
			<span class="nav-tooltip">Chat</span>
		</button>

		<!-- Documents Tab -->
		<button
			type="button"
			class="nav-item"
			class:active={$activeTab === 'documents'}
			class:disabled={!isProjectSelected}
			on:click={() => handleTabClick('documents')}
			on:keydown={(e) => handleKeyDown(e, 'documents')}
			role="tab"
			id="documents-tab"
			aria-selected={$activeTab === 'documents'}
			aria-controls="documents-panel"
			aria-disabled={!isProjectSelected}
			tabindex={$activeTab === 'documents' ? 0 : -1}
		>
			{#if !isProjectSelected}
				<!-- Lock icon overlay -->
				<svg class="nav-icon-overlay" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
					<path d="M7 11V7a5 5 0 0 1 10 0v4" />
				</svg>
			{/if}
			<!-- File/Document icon -->
			<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
				<polyline points="14 2 14 8 20 8" />
				<line x1="16" y1="13" x2="8" y2="13" />
				<line x1="16" y1="17" x2="8" y2="17" />
				<polyline points="10 9 9 9 8 9" />
			</svg>
			<span class="nav-tooltip">{isProjectSelected ? 'Documents' : 'Select project first'}</span>
		</button>

		<!-- Settings Tab -->
		<button
			type="button"
			class="nav-item"
			class:active={$activeTab === 'settings'}
			class:disabled={!isProjectSelected}
			on:click={() => handleTabClick('settings')}
			on:keydown={(e) => handleKeyDown(e, 'settings')}
			role="tab"
			id="settings-tab"
			aria-selected={$activeTab === 'settings'}
			aria-controls="settings-panel"
			aria-disabled={!isProjectSelected}
			tabindex={$activeTab === 'settings' ? 0 : -1}
		>
			{#if !isProjectSelected}
				<!-- Lock icon overlay -->
				<svg class="nav-icon-overlay" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
					<path d="M7 11V7a5 5 0 0 1 10 0v4" />
				</svg>
			{/if}
			<!-- Settings/Gear icon -->
			<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<circle cx="12" cy="12" r="3" />
				<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
			</svg>
			<span class="nav-tooltip">{isProjectSelected ? 'Settings' : 'Select project first'}</span>
		</button>
	</div>

	<!-- Spacer -->
	<div class="nav-spacer"></div>

	<!-- Theme Toggle at bottom -->
	<div class="nav-footer">
		<ThemeToggle />
	</div>
</nav>

<style>
	.vertical-nav {
		width: 64px;
		height: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 1rem 0;
		gap: 0.5rem;
		background: var(--bg-secondary);
		border-right: 1px solid var(--border-primary);
		flex-shrink: 0;
	}

	.tablist {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}

	.nav-item {
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 44px;
		height: 44px;
		border: none;
		border-radius: 0.75rem;
		background: transparent;
		color: var(--text-secondary);
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.nav-item:hover:not(.disabled) {
		background: var(--bg-hover);
		color: var(--text-primary);
	}

	.nav-item.active {
		background: var(--accent-muted);
		color: var(--accent);
	}

	.nav-item.active::before {
		content: '';
		position: absolute;
		left: -8px;
		top: 50%;
		transform: translateY(-50%);
		width: 4px;
		height: 24px;
		background: var(--accent);
		border-radius: 0 4px 4px 0;
	}

	/* Visible focus indicators for keyboard navigation */
	.nav-item:focus {
		outline: none;
	}

	.nav-item:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: 2px;
		box-shadow: 0 0 0 4px var(--accent-muted);
	}

	.nav-item.disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.nav-icon {
		width: 24px;
		height: 24px;
	}

	.nav-icon-overlay {
		position: absolute;
		top: 6px;
		right: 6px;
		width: 12px;
		height: 12px;
		color: var(--text-muted);
		opacity: 0.8;
	}

	.nav-tooltip {
		position: absolute;
		left: 100%;
		margin-left: 0.75rem;
		padding: 0.375rem 0.75rem;
		background: var(--bg-elevated);
		border: 1px solid var(--border-primary);
		border-radius: 0.5rem;
		color: var(--text-primary);
		font-size: 0.875rem;
		font-weight: 500;
		white-space: nowrap;
		opacity: 0;
		visibility: hidden;
		transition: all 0.2s ease;
		pointer-events: none;
		box-shadow: var(--shadow-md);
		z-index: 100;
	}

	.nav-item:hover .nav-tooltip {
		opacity: 1;
		visibility: visible;
	}

	.nav-spacer {
		flex: 1;
	}

	.nav-footer {
		padding: 0.5rem;
	}

	/* Compact theme toggle for nav */
	.nav-footer :global(.theme-toggle) {
		width: 44px;
		height: 44px;
		padding: 0;
		justify-content: center;
		border-radius: 0.75rem;
	}

	.nav-footer :global(.theme-label) {
		display: none;
	}

	.nav-footer :global(.theme-icon) {
		font-size: 1.25rem;
	}

	/* Mobile: horizontal at bottom */
	@media (max-width: 640px) {
		.vertical-nav {
			position: fixed;
			bottom: 0;
			left: 0;
			right: 0;
			width: 100%;
			height: 64px;
			flex-direction: row;
			justify-content: center;
			border-right: none;
			border-top: 1px solid var(--border-primary);
			z-index: 50;
		}

		.tablist {
			flex-direction: row;
		}

		.nav-item.active::before {
			left: 50%;
			top: -8px;
			transform: translateX(-50%);
			width: 24px;
			height: 4px;
			border-radius: 0 0 4px 4px;
		}

		.nav-spacer {
			display: none;
		}

		.nav-footer {
			display: none;
		}

		.nav-tooltip {
			display: none;
		}
	}
</style>
