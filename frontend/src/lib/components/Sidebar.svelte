<script lang="ts">
/**
 * Sidebar: Main navigation with project selector, search, new chat, and chat history.
 * Features: Toggle open/close, responsive overlay on mobile, sticky header with scrollable list.
 */

import NewChatButton from './NewChatButton.svelte';
import SearchInput from './SearchInput.svelte';
import ProjectSelector from './ProjectSelector.svelte';
import ChatHistoryList from './ChatHistoryList.svelte';
import CreateProjectModal from './modals/CreateProjectModal.svelte';
import ProjectSettingsModal from './modals/ProjectSettingsModal.svelte';
import { sidebarOpen } from '$lib/stores/sidebar';
import { currentProjectId } from '$lib/stores/projects';
import { conversations } from '$lib/stores/conversations';
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

function handleProjectCreated(event: CustomEvent<{ id: number; name: string }>) {
	showCreateProjectModal = false;
	currentProjectId.set(event.detail.id);
}

function toggleSidebar() {
	sidebarOpen.toggle();
}

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

function handleProjectUpdated() {
	showSettingsModal = false;
	currentProject = null;
}

function handleProjectDeleted(event: CustomEvent<number>) {
	const deletedId = event.detail;
	showSettingsModal = false;
	currentProject = null;
	if ($currentProjectId === deletedId) {
		currentProjectId.set(null);
		conversations.setConversations([]);
	}
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
	/* Overlay (mobile) */
	.sidebar-overlay { position: fixed; inset: 0; background-color: rgba(0, 0, 0, 0.5); z-index: 40; display: none; }
	@media (max-width: 768px) { .sidebar-overlay { display: block; } }

	/* Sidebar container */
	.sidebar {
		position: fixed; top: 0; left: 0; bottom: 0; width: var(--sidebar-width);
		background: linear-gradient(180deg, #fafbfc 0%, #f4f6f9 100%);
		border-right: 1px solid rgba(226, 232, 240, 0.8);
		box-shadow: 4px 0 24px rgba(0, 0, 0, 0.08); z-index: 50;
		display: flex; flex-direction: column;
		transform: translateX(-100%);
		transition: transform var(--animation-duration) cubic-bezier(0.4, 0, 0.2, 1);
		backdrop-filter: blur(10px);
	}
	.sidebar.open { transform: translateX(0); }
	@media (min-width: 769px) { .sidebar { transform: translateX(0); } }

	/* Header */
	.sidebar-header {
		display: flex; align-items: center; justify-content: space-between;
		padding: 1.25rem 1rem; border-bottom: 1px solid rgba(226, 232, 240, 0.8);
		background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
		position: sticky; top: 0; z-index: 10;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
	}
	.sidebar-title {
		margin: 0; font-size: 1.25rem; font-weight: 700;
		background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
		-webkit-background-clip: text; -webkit-text-fill-color: transparent;
		background-clip: text; letter-spacing: -0.02em;
	}
	@media (max-width: 768px) { .sidebar-title { display: none; } }

	/* Toggle button */
	.toggle-button {
		padding: 0.625rem; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
		border: 1px solid #e2e8f0; border-radius: 0.5rem; color: #64748b;
		cursor: pointer; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	}
	.toggle-button:hover { background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); color: #334155; border-color: #cbd5e1; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); transform: scale(1.05); }
	.toggle-button:active { transform: scale(0.95); }
	@media (min-width: 769px) { .toggle-button { display: none; } }

	/* Content & sticky header */
	.sidebar-content { display: flex; flex-direction: column; flex: 1; overflow: hidden; }
	.sidebar-sticky-header { background-color: #ffffff; border-bottom: 1px solid #e5e7eb; position: sticky; top: 0; z-index: 5; }
	.project-row { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.75rem; }

	/* Icon buttons (shared base) */
	.new-project-button, .settings-button {
		flex-shrink: 0; display: flex; align-items: center; justify-content: center;
		width: 2.5rem; height: 2.5rem; border: 1px solid #e5e7eb; border-radius: 0.5rem;
		background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
		color: #64748b; cursor: pointer; transition: all 0.2s ease;
	}
	.new-project-button:hover { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); border-color: #3b82f6; color: white; transform: scale(1.05); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }
	.new-project-button:active { transform: scale(0.95); }
	.settings-button:hover:not(:disabled) { background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); border-color: #6366f1; color: white; transform: scale(1.05); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }
	.settings-button:active:not(:disabled) { transform: scale(0.95); }
	.settings-button:disabled { opacity: 0.6; cursor: not-allowed; }
	.settings-button .spinner { animation: spin 1s linear infinite; }
	@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

	/* Scrollable area & scrollbar */
	.sidebar-scrollable { flex: 1; overflow-y: auto; overflow-x: hidden; }
	.sidebar-scrollable::-webkit-scrollbar { width: 6px; }
	.sidebar-scrollable::-webkit-scrollbar-track { background: #f9fafb; }
	.sidebar-scrollable::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
	.sidebar-scrollable::-webkit-scrollbar-thumb:hover { background: #9ca3af; }
</style>
