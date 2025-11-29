<script lang="ts">
	/**
	 * Main application page
	 *
	 * Layout (with ARIA landmarks):
	 * ┌─────────────────────────────────────────────────────┐
	 * │ [Logo]  [Project Selector]           [Theme Toggle] │ ← TopBar (banner)
	 * ├────────┬────────────────────────────────────────────┤
	 * │ Chat   │                                            │
	 * │ Docs   │          Tab Content Area                  │ ← Chat / Documents / Settings
	 * │ Gear   │                                            │   (main + tabpanel)
	 * └────────┴────────────────────────────────────────────┘
	 *     ↑
	 *  VerticalNav (navigation + tablist)
	 *
	 * Accessibility:
	 * - Skip link for keyboard users
	 * - ARIA landmarks (banner, navigation, main)
	 * - Tab/tabpanel pattern for navigation
	 */

	import TopBar from '$lib/components/TopBar.svelte';
	import VerticalNav from '$lib/components/VerticalNav.svelte';
	import ChatTab from '$lib/components/tabs/ChatTab.svelte';
	import DocumentsTab from '$lib/components/tabs/DocumentsTab.svelte';
	import SettingsTab from '$lib/components/tabs/SettingsTab.svelte';
	import { activeTab } from '$lib/stores/navigation';
</script>

<!-- Skip link for keyboard navigation (hidden until focused) -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<div class="app-layout">
	<!-- Top Bar (implicit banner role via <header>) -->
	<header>
		<TopBar />
	</header>

	<!-- Main Area (Nav + Content) -->
	<div class="main-area">
		<!-- Vertical Navigation (contains tablist) -->
		<VerticalNav />

		<!-- Tab Content (main landmark) -->
		<main id="main-content" class="content-area" aria-label="Tab content">
			{#if $activeTab === 'chat'}
				<div id="chat-panel" role="tabpanel" aria-labelledby="chat-tab" tabindex="0">
					<ChatTab />
				</div>
			{:else if $activeTab === 'documents'}
				<div id="documents-panel" role="tabpanel" aria-labelledby="documents-tab" tabindex="0">
					<DocumentsTab />
				</div>
			{:else if $activeTab === 'settings'}
				<div id="settings-panel" role="tabpanel" aria-labelledby="settings-tab" tabindex="0">
					<SettingsTab />
				</div>
			{/if}
		</main>
	</div>
</div>

<style>
	/* Skip link (hidden until focused) */
	.skip-link {
		position: absolute;
		top: -100px;
		left: 50%;
		transform: translateX(-50%);
		z-index: 9999;
		padding: 0.75rem 1.5rem;
		background: var(--accent);
		color: white;
		font-weight: 600;
		text-decoration: none;
		border-radius: 0 0 0.5rem 0.5rem;
		transition: top 0.2s ease;
	}

	.skip-link:focus {
		top: 0;
		outline: 2px solid var(--accent);
		outline-offset: 2px;
	}

	.app-layout {
		display: flex;
		flex-direction: column;
		width: 100%;
		height: 100vh;
		overflow: hidden;
		background: var(--bg-primary);
	}

	/* Header wrapper for banner role */
	header[role="banner"] {
		flex-shrink: 0;
	}

	.main-area {
		display: flex;
		flex: 1;
		overflow: hidden;
	}

	.content-area {
		flex: 1;
		overflow: hidden;
		min-width: 0;
	}

	/* Tab panels - full height and focusable for keyboard navigation */
	.content-area [role="tabpanel"] {
		display: flex;
		flex-direction: column;
		height: 100%;
		outline: none;
	}

	.content-area [role="tabpanel"]:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: -2px;
	}

	/* Mobile: account for bottom nav */
	@media (max-width: 640px) {
		.main-area {
			padding-bottom: 64px; /* Height of mobile nav */
		}
	}
</style>
