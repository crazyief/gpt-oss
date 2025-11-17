<script lang="ts">
/**
 * Sidebar component
 *
 * Purpose: Main sidebar container with chat history, search, and project selection
 *
 * Features:
 * - Toggleable sidebar (open/close with animation)
 * - Responsive design (overlay on mobile, fixed on desktop)
 * - Project selector at top
 * - Search input for filtering conversations
 * - New chat button
 * - Scrollable chat history list
 * - Persists open/close state to localStorage
 *
 * Layout structure:
 * ┌─────────────────┐
 * │ Project Selector│  (sticky header)
 * ├─────────────────┤
 * │ Search Input    │  (sticky header)
 * ├─────────────────┤
 * │ New Chat Button │  (sticky header)
 * ├─────────────────┤
 * │                 │
 * │  Chat History   │  (scrollable)
 * │  (Virtual List) │
 * │                 │
 * └─────────────────┘
 *
 * WHY sticky header elements:
 * - Accessibility: New Chat and Search always visible (no scrolling required)
 * - UX: Common actions always available regardless of scroll position
 * - Visual hierarchy: Separates controls from content
 */

import NewChatButton from './NewChatButton.svelte';
import SearchInput from './SearchInput.svelte';
import ProjectSelector from './ProjectSelector.svelte';
import ChatHistoryList from './ChatHistoryList.svelte';
import { sidebarOpen } from '$lib/stores/sidebar';
import { APP_CONFIG } from '$lib/config';

/**
 * Toggle sidebar visibility
 *
 * WHY toggle function instead of direct store.set():
 * - Encapsulation: Component controls sidebar state
 * - Future enhancement: Can add animation hooks, analytics, etc.
 */
function toggleSidebar() {
	sidebarOpen.toggle();
}
</script>

<!-- Sidebar overlay (mobile: click to close sidebar) -->
{#if $sidebarOpen}
	<div
		class="sidebar-overlay"
		on:click={toggleSidebar}
		on:keydown={(e) => e.key === 'Escape' && toggleSidebar()}
		role="button"
		tabindex="-1"
		aria-label="Close sidebar"
	></div>
{/if}

<!-- Sidebar container -->
<aside
	class="sidebar"
	class:open={$sidebarOpen}
	aria-label="Sidebar navigation"
	style="--sidebar-width: {APP_CONFIG.sidebar.width}; --animation-duration: {APP_CONFIG.sidebar.toggleAnimationMs}ms;"
>
	<!-- Sidebar header with toggle button -->
	<div class="sidebar-header">
		<h2 class="sidebar-title">Conversations</h2>
		<button
			type="button"
			on:click={toggleSidebar}
			class="toggle-button"
			aria-label={$sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
			aria-expanded={$sidebarOpen}
		>
			{#if $sidebarOpen}
				<!-- Close icon (X) -->
				<svg
					width="20"
					height="20"
					viewBox="0 0 20 20"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M15 5L5 15M5 5l10 10"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
					/>
				</svg>
			{:else}
				<!-- Menu icon (hamburger) -->
				<svg
					width="20"
					height="20"
					viewBox="0 0 20 20"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M3 6h14M3 10h14M3 14h14"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
					/>
				</svg>
			{/if}
		</button>
	</div>

	<!-- Sidebar content (sticky header + scrollable list) -->
	<div class="sidebar-content">
		<!-- Sticky header section -->
		<div class="sidebar-sticky-header">
			<!-- Project selector -->
			<ProjectSelector />

			<!-- Search input -->
			<SearchInput />

			<!-- New chat button -->
			<NewChatButton />
		</div>

		<!-- Scrollable chat history -->
		<div class="sidebar-scrollable">
			<ChatHistoryList />
		</div>
	</div>
</aside>

<style>
	/**
	 * Sidebar overlay (mobile only)
	 *
	 * WHY overlay on mobile:
	 * - Focus: Dims background, directs attention to sidebar
	 * - UX pattern: Matches Material Design, iOS patterns
	 * - Accessibility: Prevents interaction with background while sidebar open
	 *
	 * WHY z-index 40:
	 * - Below sidebar (z-index 50) but above main content (z-index 0)
	 * - Common Tailwind z-index scale: 0, 10, 20, 30, 40, 50
	 */
	.sidebar-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: rgba(0, 0, 0, 0.5);
		z-index: 40;
		display: none; /* Hidden on desktop */
	}

	/**
	 * Show overlay on mobile when sidebar is open
	 *
	 * WHY @media (max-width: 768px):
	 * - Tablet breakpoint: Matches common mobile/tablet boundary
	 * - Sidebar overlay: Only needed on small screens (mobile/tablet portrait)
	 */
	@media (max-width: 768px) {
		.sidebar-overlay {
			display: block;
		}
	}

	/**
	 * Sidebar container
	 *
	 * Layout: Fixed position, full height
	 * WHY fixed position:
	 * - Always visible: Sidebar doesn't scroll with page
	 * - Overlay mode: Can overlay main content on mobile
	 *
	 * WHY transform instead of left/margin-left for hide/show:
	 * - Performance: transform uses GPU, left uses CPU (smoother animation)
	 * - No layout shift: transform doesn't trigger reflow (better performance)
	 */
	.sidebar {
		position: fixed;
		top: 0;
		left: 0;
		bottom: 0;
		width: var(--sidebar-width);
		background-color: #ffffff;
		border-right: 1px solid #e5e7eb; /* Gray 200 */
		z-index: 50;
		display: flex;
		flex-direction: column;
		transform: translateX(-100%); /* Hidden by default */
		transition: transform var(--animation-duration) ease;
	}

	/**
	 * Sidebar open state
	 *
	 * WHY translateX(0) instead of left: 0:
	 * - GPU acceleration: Better animation performance
	 * - Same pattern as hide state (consistent)
	 */
	.sidebar.open {
		transform: translateX(0);
	}

	/**
	 * Desktop: sidebar always open
	 *
	 * WHY override transform on desktop:
	 * - Persistent UI: Sidebar is core navigation, should always be visible
	 * - Screen real estate: Desktop has space for persistent sidebar
	 */
	@media (min-width: 769px) {
		.sidebar {
			transform: translateX(0); /* Always visible */
		}
	}

	/**
	 * Sidebar header
	 *
	 * Layout: Title on left, toggle button on right
	 * WHY sticky positioning:
	 * - Always visible: Header doesn't scroll away
	 * - Context: User always sees "Conversations" label
	 */
	.sidebar-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem;
		border-bottom: 1px solid #e5e7eb; /* Gray 200 */
		background-color: #ffffff;
		position: sticky;
		top: 0;
		z-index: 10;
	}

	/**
	 * Sidebar title
	 *
	 * WHY hide on mobile, show on desktop:
	 * - Space: Mobile needs room for toggle button
	 * - Context: Desktop users benefit from explicit label
	 */
	.sidebar-title {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: #111827; /* Gray 900 */
	}

	@media (max-width: 768px) {
		.sidebar-title {
			display: none;
		}
	}

	/**
	 * Toggle button
	 *
	 * WHY show on mobile, hide on desktop:
	 * - Mobile: Need toggle to open/close (limited space)
	 * - Desktop: Sidebar always open, toggle unnecessary
	 */
	.toggle-button {
		padding: 0.5rem;
		background: none;
		border: none;
		border-radius: 0.375rem;
		color: #6b7280; /* Gray 500 */
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.toggle-button:hover {
		background-color: #f3f4f6; /* Gray 100 */
		color: #111827; /* Gray 900 */
	}

	@media (min-width: 769px) {
		.toggle-button {
			display: none; /* Hide on desktop */
		}
	}

	/**
	 * Sidebar content container
	 *
	 * WHY flex-direction column:
	 * - Vertical layout: Header stacked above scrollable area
	 * - Flex-grow: Scrollable area takes remaining space
	 */
	.sidebar-content {
		display: flex;
		flex-direction: column;
		flex: 1;
		overflow: hidden; /* Prevent content overflow */
	}

	/**
	 * Sticky header section (Project + Search + New Chat)
	 *
	 * WHY sticky instead of absolute:
	 * - Scroll behavior: Stays at top when chat history scrolls
	 * - Layout: Doesn't overlap chat history
	 */
	.sidebar-sticky-header {
		background-color: #ffffff;
		border-bottom: 1px solid #e5e7eb; /* Gray 200 */
		position: sticky;
		top: 0;
		z-index: 5;
	}

	/**
	 * Scrollable chat history section
	 *
	 * WHY flex: 1:
	 * - Fill space: Takes all remaining vertical space
	 * - Scroll: Allows chat history to scroll independently
	 *
	 * WHY overflow-y: auto:
	 * - Scrollbar: Appears when content exceeds height
	 * - Virtual list: VirtualList component handles internal scrolling
	 */
	.sidebar-scrollable {
		flex: 1;
		overflow-y: auto;
		overflow-x: hidden;
	}

	/**
	 * Scrollbar styling (WebKit browsers)
	 *
	 * WHY custom scrollbar:
	 * - Visual consistency: Matches app design
	 * - Less intrusive: Thinner than default scrollbar
	 */
	.sidebar-scrollable::-webkit-scrollbar {
		width: 6px;
	}

	.sidebar-scrollable::-webkit-scrollbar-track {
		background: #f9fafb; /* Gray 50 */
	}

	.sidebar-scrollable::-webkit-scrollbar-thumb {
		background: #d1d5db; /* Gray 300 */
		border-radius: 3px;
	}

	.sidebar-scrollable::-webkit-scrollbar-thumb:hover {
		background: #9ca3af; /* Gray 400 */
	}
</style>
