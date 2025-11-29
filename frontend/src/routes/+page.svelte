<script lang="ts">
/**
 * Main chat page
 *
 * Purpose: Full-screen chat interface with sidebar and document management
 *
 * Layout:
 * ┌──────────┬─────────────────────┐
 * │          │ [Documents Panel]   │ ← Collapsible (when project selected)
 * │ Sidebar  ├─────────────────────┤
 * │          │   Chat Interface    │
 * │          │                     │
 * └──────────┴─────────────────────┘
 *
 * Features:
 * - Sidebar with conversation history (Task-005)
 * - Chat interface with streaming (Task-006)
 * - Document management panel (Stage 2)
 * - Responsive layout (sidebar overlays on mobile)
 */

import Sidebar from '$lib/components/Sidebar.svelte';
import ChatInterface from '$lib/components/ChatInterface.svelte';
import DocumentPanel from '$lib/components/documents/DocumentPanel.svelte';
import { sidebarOpen } from '$lib/stores/sidebar';
import { currentConversationId } from '$lib/stores/conversations';
import { currentProjectId } from '$lib/stores/projects';
</script>

<div class="app-container">
	<!-- Sidebar (toggleable on mobile, persistent on desktop) -->
	<Sidebar />

	<!-- Main content area (chat interface) -->
	<main
		class="main-content"
		class:sidebar-open={$sidebarOpen}
		class:no-conversation={!$currentConversationId}
	>
		<!-- Document Panel (when project selected) -->
		{#if $currentProjectId !== null}
			<div class="document-panel-container">
				<DocumentPanel />
			</div>
		{/if}

		{#if $currentConversationId}
			<!-- Chat interface (when conversation selected) -->
			<ChatInterface />
		{:else}
			<!-- Welcome screen (no conversation selected) -->
			<div class="welcome-screen">
				<div class="welcome-content">
					<svg
						width="80"
						height="80"
						viewBox="0 0 80 80"
						fill="none"
						xmlns="http://www.w3.org/2000/svg"
						class="welcome-icon"
					>
						<rect
							x="10"
							y="10"
							width="60"
							height="60"
							rx="8"
							stroke="currentColor"
							stroke-width="3"
						/>
						<circle cx="28" cy="32" r="4" fill="currentColor" />
						<circle cx="52" cy="32" r="4" fill="currentColor" />
						<path
							d="M28 48h24"
							stroke="currentColor"
							stroke-width="3"
							stroke-linecap="round"
						/>
					</svg>

					<h1 class="welcome-title">Welcome to GPT-OSS</h1>
					<p class="welcome-subtitle">
						Your local AI knowledge assistant for cybersecurity and compliance research
					</p>

					<div class="welcome-actions">
						<div class="action-card">
							<svg
								width="32"
								height="32"
								viewBox="0 0 32 32"
								fill="none"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="M16 8v16M8 16h16"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
								/>
							</svg>
							<h3>Start a New Chat</h3>
							<p>Click "New Chat" in the sidebar to begin a conversation</p>
						</div>

						<div class="action-card">
							<svg
								width="32"
								height="32"
								viewBox="0 0 32 32"
								fill="none"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="M6 10h20M6 16h20M6 22h20"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
								/>
							</svg>
							<h3>Browse History</h3>
							<p>Select a previous conversation from the sidebar to continue</p>
						</div>

						<div class="action-card">
							<svg
								width="32"
								height="32"
								viewBox="0 0 32 32"
								fill="none"
								xmlns="http://www.w3.org/2000/svg"
							>
								<circle
									cx="14"
									cy="14"
									r="8"
									stroke="currentColor"
									stroke-width="2"
								/>
								<path
									d="M20 20l6 6"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
								/>
							</svg>
							<h3>Search Conversations</h3>
							<p>Use the search box to find specific topics or discussions</p>
						</div>
					</div>

					<div class="welcome-footer">
						<p class="footer-text">
							<strong>Stage 2 Complete:</strong> Document management and RAG foundation
						</p>
						<p class="footer-subtext">
							Features: Document upload/download/delete • Project management • Chat with SSE streaming • Markdown support • Syntax highlighting
						</p>
					</div>
				</div>
			</div>
		{/if}
	</main>
</div>

<style>
	/**
	 * App container
	 *
	 * WHY flexbox layout:
	 * - Sidebar + main content side-by-side
	 * - Sidebar has fixed width, main content fills remaining space
	 */
	.app-container {
		display: flex;
		width: 100%;
		height: 100vh;
		overflow: hidden;
	}

	/**
	 * Main content area
	 *
	 * WHY margin-left on desktop:
	 * - Sidebar offset: Push content to avoid overlap with fixed sidebar
	 * - Responsive: On mobile, sidebar overlays (no margin needed)
	 */
	.main-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		background-color: #ffffff;
		transition: margin-left 0.3s ease;
	}

	/* Desktop: offset for fixed sidebar */
	@media (min-width: 769px) {
		.main-content {
			margin-left: 260px; /* Sidebar width */
		}
	}

	/**
	 * Document panel container
	 *
	 * WHY fixed positioning at top:
	 * - Documents stay accessible while scrolling chat
	 * - Collapsible to maximize chat space when needed
	 */
	.document-panel-container {
		padding: 1rem;
		background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
		border-bottom: 1px solid #e5e7eb;
		flex-shrink: 0; /* Don't shrink when chat content grows */
	}

	/**
	 * Welcome screen (no conversation selected)
	 */
	.welcome-screen {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		padding: 2rem;
		background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
	}

	.welcome-content {
		max-width: 800px;
		text-align: center;
	}

	.welcome-icon {
		margin: 0 auto 2rem auto;
		color: #3b82f6; /* Blue 500 */
	}

	.welcome-title {
		margin: 0 0 0.5rem 0;
		font-size: 2.5rem;
		font-weight: 700;
		color: #111827; /* Gray 900 */
	}

	.welcome-subtitle {
		margin: 0 0 3rem 0;
		font-size: 1.125rem;
		color: #6b7280; /* Gray 500 */
	}

	/**
	 * Action cards (guidance for new users)
	 */
	.welcome-actions {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: 1.5rem;
		margin-bottom: 3rem;
	}

	.action-card {
		padding: 1.5rem;
		background: white;
		border-radius: 0.75rem;
		border: 1px solid #e5e7eb; /* Gray 200 */
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
		transition: all 0.2s ease;
	}

	.action-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}

	.action-card svg {
		margin-bottom: 1rem;
		color: #3b82f6; /* Blue 500 */
	}

	.action-card h3 {
		margin: 0 0 0.5rem 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: #111827; /* Gray 900 */
	}

	.action-card p {
		margin: 0;
		font-size: 0.875rem;
		color: #6b7280; /* Gray 500 */
		line-height: 1.5;
	}

	/**
	 * Welcome footer (status info)
	 */
	.welcome-footer {
		padding: 1.5rem;
		background: white;
		border-radius: 0.75rem;
		border: 1px solid #e5e7eb;
	}

	.footer-text {
		margin: 0 0 0.5rem 0;
		font-size: 1rem;
		color: #374151; /* Gray 700 */
	}

	.footer-subtext {
		margin: 0;
		font-size: 0.875rem;
		color: #6b7280; /* Gray 500 */
	}

	/**
	 * Responsive: Stack action cards on mobile
	 */
	@media (max-width: 768px) {
		.welcome-title {
			font-size: 2rem;
		}

		.welcome-subtitle {
			font-size: 1rem;
		}

		.welcome-actions {
			grid-template-columns: 1fr;
		}
	}
</style>
