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
import CreateProjectModal from './modals/CreateProjectModal.svelte';
import ProjectSettingsModal from './modals/ProjectSettingsModal.svelte';
import { sidebarOpen } from '$lib/stores/sidebar';
import { currentProjectId } from '$lib/stores/projects';
import { APP_CONFIG } from '$lib/config';
import { fetchProject } from '$lib/services/api/projects';
import type { Project } from '$lib/types';
import { logger } from '$lib/utils/logger';

// State for Create Project modal
let showCreateProjectModal = false;

// State for Project Settings modal
let showSettingsModal = false;
let currentProject: Project | null = null;
let isLoadingProject = false;

/**
 * Handle project created event
 * Refreshes project list and selects new project
 */
function handleProjectCreated(event: CustomEvent<{ id: number; name: string }>) {
	showCreateProjectModal = false;
	// Set the newly created project as current
	currentProjectId.set(event.detail.id);
	// ProjectSelector will auto-refresh due to store subscription
}

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

/**
 * Open project settings modal
 * Fetches current project data before opening
 */
async function openSettingsModal() {
	if ($currentProjectId === null) return;

	try {
		isLoadingProject = true;
		currentProject = await fetchProject($currentProjectId);
		showSettingsModal = true;
	} catch (error) {
		logger.error('Failed to load project for settings', { projectId: $currentProjectId, error });
	} finally {
		isLoadingProject = false;
	}
}

/**
 * Handle project updated event
 * ProjectSelector will auto-refresh due to store subscription
 */
function handleProjectUpdated() {
	showSettingsModal = false;
	currentProject = null;
}

/**
 * Handle project deleted event
 * Clears current project and closes modal
 */
function handleProjectDeleted() {
	showSettingsModal = false;
	currentProject = null;
	// currentProjectId is set to null in the modal's handleDelete
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
			<!-- Project selector with Settings and New Project buttons -->
			<div class="project-row">
				<ProjectSelector />
				<!-- Settings button (only when project selected) -->
				{#if $currentProjectId !== null}
					<button
						type="button"
						class="settings-button"
						on:click={openSettingsModal}
						disabled={isLoadingProject}
						aria-label="Project settings"
						title="Project settings"
					>
						{#if isLoadingProject}
							<svg class="spinner" width="16" height="16" viewBox="0 0 16 16">
								<circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="30" stroke-linecap="round">
									<animateTransform attributeName="transform" type="rotate" from="0 8 8" to="360 8 8" dur="1s" repeatCount="indefinite"/>
								</circle>
							</svg>
						{:else}
							<!-- Gear icon -->
							<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
								<path d="M8 10a2 2 0 100-4 2 2 0 000 4z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
								<path d="M13.3 6.4l-.8-.5c-.1-.1-.2-.2-.2-.4 0-.1.1-.3.2-.4l.8-.5c.2-.1.3-.4.2-.6l-.8-1.4c-.1-.2-.4-.3-.6-.2l-.9.4c-.2.1-.4 0-.5-.1-.1-.1-.2-.3-.1-.5l.2-1c0-.3-.2-.5-.4-.6l-1.6-.1c-.2 0-.5.2-.5.4l-.2 1c0 .2-.1.3-.3.4-.2.1-.4.1-.5 0l-.9-.4c-.2-.1-.5 0-.6.2l-.8 1.4c-.1.2-.1.5.2.6l.8.5c.2.1.2.2.2.4 0 .1-.1.3-.2.4l-.8.5c-.2.1-.3.4-.2.6l.8 1.4c.1.2.4.3.6.2l.9-.4c.2-.1.4 0 .5.1.1.1.2.3.1.5l-.2 1c0 .3.2.5.4.6l1.6.1c.2 0 .5-.2.5-.4l.2-1c0-.2.1-.3.3-.4.2-.1.4-.1.5 0l.9.4c.2.1.5 0 .6-.2l.8-1.4c.2-.2.1-.5-.1-.6z" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"/>
							</svg>
						{/if}
					</button>
				{/if}
				<button
					type="button"
					class="new-project-button"
					on:click={() => (showCreateProjectModal = true)}
					aria-label="Create new project"
					title="Create new project"
				>
					<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
					</svg>
				</button>
			</div>

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

<!-- Create Project Modal -->
<CreateProjectModal
	isOpen={showCreateProjectModal}
	on:created={handleProjectCreated}
	on:cancel={() => (showCreateProjectModal = false)}
/>

<!-- Project Settings Modal -->
<ProjectSettingsModal
	isOpen={showSettingsModal}
	project={currentProject}
	on:updated={handleProjectUpdated}
	on:deleted={handleProjectDeleted}
	on:close={() => { showSettingsModal = false; currentProject = null; }}
/>

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
	 * Sidebar container - Modern gradient with glassmorphism
	 */
	.sidebar {
		position: fixed;
		top: 0;
		left: 0;
		bottom: 0;
		width: var(--sidebar-width);
		background: linear-gradient(180deg, #fafbfc 0%, #f4f6f9 100%);
		border-right: 1px solid rgba(226, 232, 240, 0.8);
		box-shadow: 4px 0 24px rgba(0, 0, 0, 0.08);
		z-index: 50;
		display: flex;
		flex-direction: column;
		transform: translateX(-100%);
		transition: transform var(--animation-duration) cubic-bezier(0.4, 0, 0.2, 1);
		backdrop-filter: blur(10px);
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
	 * Sidebar header - Elevated gradient design
	 */
	.sidebar-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.25rem 1rem;
		border-bottom: 1px solid rgba(226, 232, 240, 0.8);
		background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
		position: sticky;
		top: 0;
		z-index: 10;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
	}

	/**
	 * Sidebar title - Modern typography
	 */
	.sidebar-title {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 700;
		background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		letter-spacing: -0.02em;
	}

	@media (max-width: 768px) {
		.sidebar-title {
			display: none;
		}
	}

	/**
	 * Toggle button - Smooth hover effect
	 */
	.toggle-button {
		padding: 0.625rem;
		background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
		border: 1px solid #e2e8f0;
		border-radius: 0.5rem;
		color: #64748b;
		cursor: pointer;
		transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	}

	.toggle-button:hover {
		background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
		color: #334155;
		border-color: #cbd5e1;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
		transform: scale(1.05);
	}

	.toggle-button:active {
		transform: scale(0.95);
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
	 * Project row - horizontal layout for selector + new project button
	 */
	.project-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
	}

	/**
	 * New project button - compact icon button
	 */
	.new-project-button {
		flex-shrink: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2.5rem;
		height: 2.5rem;
		border: 1px solid #e5e7eb;
		border-radius: 0.5rem;
		background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
		color: #64748b;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.new-project-button:hover {
		background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
		border-color: #3b82f6;
		color: white;
		transform: scale(1.05);
		box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
	}

	.new-project-button:active {
		transform: scale(0.95);
	}

	/**
	 * Settings button - gear icon for project settings
	 */
	.settings-button {
		flex-shrink: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2.5rem;
		height: 2.5rem;
		border: 1px solid #e5e7eb;
		border-radius: 0.5rem;
		background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
		color: #64748b;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.settings-button:hover:not(:disabled) {
		background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
		border-color: #6366f1;
		color: white;
		transform: scale(1.05);
		box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
	}

	.settings-button:active:not(:disabled) {
		transform: scale(0.95);
	}

	.settings-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.settings-button .spinner {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
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
