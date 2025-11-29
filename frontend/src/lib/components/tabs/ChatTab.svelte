<script lang="ts">
	/**
	 * ChatTab - Chat interface with conversation history sidebar
	 *
	 * Layout:
	 * ┌────────────┬─────────────────────┐
	 * │ History    │    Chat Messages    │
	 * │ - Conv 1   │                     │
	 * │ - Conv 2   │                     │
	 * │ + New Chat │    [Input Area]     │
	 * └────────────┴─────────────────────┘
	 */
	import ChatInterface from '$lib/components/ChatInterface.svelte';
	import ChatHistoryList from '$lib/components/ChatHistoryList.svelte';
	import NewChatButton from '$lib/components/NewChatButton.svelte';
	import SearchInput from '$lib/components/SearchInput.svelte';
	import { currentConversationId } from '$lib/stores/conversations';
	import { currentProjectId } from '$lib/stores/projects';

	// Track if sidebar is collapsed
	let sidebarCollapsed = false;

	function toggleSidebar() {
		sidebarCollapsed = !sidebarCollapsed;
	}
</script>

<div class="chat-tab" class:sidebar-collapsed={sidebarCollapsed}>
	<!-- Conversation History Sidebar -->
	<aside class="history-sidebar">
		<div class="sidebar-header">
			<h3 class="sidebar-title">Conversations</h3>
			<button
				type="button"
				class="collapse-btn"
				on:click={toggleSidebar}
				aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
			>
				<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
					{#if sidebarCollapsed}
						<path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
					{:else}
						<path d="M10 4l-4 4 4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
					{/if}
				</svg>
			</button>
		</div>

		<div class="sidebar-content">
			<SearchInput />
			<NewChatButton />
			<div class="history-list">
				<ChatHistoryList />
			</div>
		</div>
	</aside>

	<!-- Main Chat Area -->
	<main class="chat-main">
		{#if $currentProjectId === null}
			<!-- No project selected -->
			<div class="empty-state">
				<svg class="empty-icon" viewBox="0 0 64 64" fill="none">
					<rect x="8" y="8" width="48" height="48" rx="8" stroke="currentColor" stroke-width="3"/>
					<circle cx="24" cy="26" r="4" fill="currentColor"/>
					<circle cx="40" cy="26" r="4" fill="currentColor"/>
					<path d="M24 40h16" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
				</svg>
				<h2>Welcome to GPT-OSS</h2>
				<p>Select or create a project to start chatting</p>
			</div>
		{:else if $currentConversationId}
			<!-- Chat interface -->
			<ChatInterface />
		{:else}
			<!-- Project selected but no conversation -->
			<div class="empty-state">
				<svg class="empty-icon" viewBox="0 0 64 64" fill="none">
					<path d="M16 24h32M16 32h32M16 40h24" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
				</svg>
				<h2>Start a Conversation</h2>
				<p>Click "New Chat" to begin</p>
			</div>
		{/if}
	</main>
</div>

<style>
	.chat-tab {
		display: flex;
		height: 100%;
		overflow: hidden;
	}

	/* History Sidebar */
	.history-sidebar {
		width: 260px;
		display: flex;
		flex-direction: column;
		background: var(--bg-tertiary);
		border-right: 1px solid var(--border-primary);
		transition: width 0.3s ease;
		flex-shrink: 0;
	}

	.sidebar-collapsed .history-sidebar {
		width: 0;
		overflow: hidden;
		border-right: none;
	}

	.sidebar-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.75rem 1rem;
		border-bottom: 1px solid var(--border-primary);
	}

	.sidebar-title {
		margin: 0;
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.collapse-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 28px;
		height: 28px;
		border: none;
		border-radius: 0.375rem;
		background: transparent;
		color: var(--text-secondary);
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.collapse-btn:hover {
		background: var(--bg-hover);
		color: var(--text-primary);
	}

	.sidebar-content {
		display: flex;
		flex-direction: column;
		flex: 1;
		overflow: hidden;
		padding: 0.5rem;
		gap: 0.5rem;
	}

	.history-list {
		flex: 1;
		overflow-y: auto;
	}

	/* Main Chat Area */
	.chat-main {
		flex: 1;
		display: flex;
		flex-direction: column;
		min-width: 0;
		background: var(--bg-primary);
	}

	/* Empty State */
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		padding: 2rem;
		text-align: center;
		color: var(--text-secondary);
	}

	.empty-icon {
		width: 64px;
		height: 64px;
		margin-bottom: 1.5rem;
		color: var(--accent);
		opacity: 0.6;
	}

	.empty-state h2 {
		margin: 0 0 0.5rem 0;
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.empty-state p {
		margin: 0;
		font-size: 1rem;
	}

	/* Mobile: overlay sidebar */
	@media (max-width: 768px) {
		.history-sidebar {
			position: absolute;
			left: 0;
			top: 0;
			bottom: 0;
			z-index: 40;
			box-shadow: var(--shadow-lg);
		}

		.sidebar-collapsed .history-sidebar {
			transform: translateX(-100%);
			width: 260px;
		}
	}
</style>
