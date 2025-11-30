<script lang="ts">
	/**
	 * Main application page
	 *
	 * Layout (with ARIA landmarks):
	 * ┌────────┬────────────────────────────────────────────┐
	 * │ Chat   │                                            │
	 * │ Docs   │          Tab Content Area                  │ ← Chat / Documents / Settings
	 * │ Gear   │                                            │   (main + tabpanel)
	 * │ Theme  │                                            │
	 * └────────┴────────────────────────────────────────────┘
	 *     ↑
	 *  VerticalNav (navigation + tablist + theme toggle)
	 *
	 * Note: Project selector is now in Sidebar (ChatTab)
	 *
	 * Accessibility:
	 * - Skip link for keyboard users
	 * - ARIA landmarks (navigation, main)
	 * - Tab/tabpanel pattern for navigation
	 */

	import VerticalNav from '$lib/components/VerticalNav.svelte';
	import ChatTab from '$lib/components/tabs/ChatTab.svelte';
	import DocumentsTab from '$lib/components/tabs/DocumentsTab.svelte';
	import SettingsTab from '$lib/components/tabs/SettingsTab.svelte';
	import { activeTab } from '$lib/stores/navigation';

	/**
	 * SvelteKit internal props handling
	 *
	 * Standard SvelteKit props:
	 * - data: From load functions (+page.ts)
	 * - form: From form actions (+page.server.ts)
	 */
	// eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
	export let data: any = undefined;
	// eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
	export let form: any = undefined;

	// Capture any additional props SvelteKit might pass (prevents "unknown prop" warnings)
	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	export let params: any = undefined; // BUG-006 FIX: SvelteKit 2.x passes params
</script>

<!-- Skip link for keyboard navigation (hidden until focused) -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<div class="app-layout">
	<!-- Main Area (Nav + Content) - Full height, no TopBar -->
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
		width: 100%;
		height: 100vh;
		overflow: hidden;
		background: var(--bg-primary);
	}

	.main-area {
		display: flex;
		flex: 1;
		width: 100%;
		height: 100%;
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
