<script lang="ts">
/**
 * ChatHeader Component
 *
 * Purpose: Display conversation title, project selector, and token usage
 *
 * Features:
 * - Inline title editing (click to edit)
 * - Project dropdown selector
 * - Token usage indicator with color-coded warnings
 * - Cancel stream button (when streaming)
 *
 * WHY separate component:
 * - Single responsibility: Header concerns only
 * - Reusability: Could use same header in different layouts
 * - Maintainability: Easier to modify header without affecting message area
 * - Code quality: Keeps ChatInterface under 400 lines
 */

import { createEventDispatcher } from 'svelte';
import type { Project } from '$lib/types';

const dispatch = createEventDispatcher();

/**
 * Component props
 *
 * WHY props instead of store subscriptions:
 * - Performance: Parent controls when to update
 * - Flexibility: Can use with different stores
 * - Testability: Easy to test with mock data
 */
export let conversationTitle: string;
export let conversationId: number | null;
export let projects: Project[] = [];
export let conversationProjectId: number | null = null;
export let isChangingProject = false;
export let totalTokens = 0;
export let maxTokens = 22800;
export let isStreaming = false;

// Title editing state
let isEditingTitle = false;
let editTitleValue = '';

/**
 * Calculate percentage of max context used
 */
$: contextPercentage = (totalTokens / maxTokens) * 100;

/**
 * Start editing conversation title
 */
function startEditTitle() {
	editTitleValue = conversationTitle;
	isEditingTitle = true;
}

/**
 * Handle title keydown events
 */
function handleTitleKeydown(event: KeyboardEvent) {
	if (event.key === 'Enter') {
		event.preventDefault();
		saveEditTitle();
	} else if (event.key === 'Escape') {
		event.preventDefault();
		cancelEditTitle();
	}
}

/**
 * Save edited title
 *
 * WHY dispatch event instead of calling parent function:
 * - Svelte pattern: Components emit events, parents handle them
 * - Decoupling: Component doesn't know parent implementation
 * - Flexibility: Different parents can handle differently
 */
function saveEditTitle() {
	if (!editTitleValue.trim()) {
		isEditingTitle = false;
		return;
	}

	// Dispatch event to parent
	dispatch('saveTitle', { title: editTitleValue.trim() });

	isEditingTitle = false;
}

/**
 * Cancel title editing
 */
function cancelEditTitle() {
	isEditingTitle = false;
	editTitleValue = '';
}

/**
 * Handle project change
 */
function handleProjectChange(event: Event) {
	const target = event.target as HTMLSelectElement;
	const newProjectId = parseInt(target.value, 10);

	// Dispatch event to parent
	dispatch('changeProject', { projectId: newProjectId });
}

/**
 * Handle cancel stream
 */
function handleCancelStream() {
	dispatch('cancelStream');
}
</script>

<div class="chat-header">
	<!-- Left side: Project selector -->
	<div class="header-left">
		{#if projects.length > 0 && conversationProjectId !== null}
			<div class="project-selector-wrapper">
				<label for="conversation-project" class="project-label">
					<svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M2 3h10M2 7h10M2 11h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
					</svg>
					Project:
				</label>
				<select
					id="conversation-project"
					value={conversationProjectId}
					on:change={handleProjectChange}
					disabled={isChangingProject}
					class="project-select"
					aria-label="Change conversation project"
				>
					{#each projects as project (project.id)}
						<option value={project.id}>
							{project.name}
						</option>
					{/each}
				</select>
			</div>
		{/if}
	</div>

	<!-- Right side: ID + Token usage + Cancel button -->
	<div class="header-right">
		{#if conversationId}
			<p class="conversation-id">ID: {conversationId}</p>
		{/if}

		<!-- Token usage indicator -->
		{#if totalTokens > 0}
			<div class="token-usage" class:warning={contextPercentage > 80} class:critical={contextPercentage > 95}>
				<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M8 2v12M4 6l4-4 4 4M4 10l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
				<span class="token-count">{totalTokens.toLocaleString()} / {maxTokens.toLocaleString()}</span>
				<span class="token-percentage">({contextPercentage.toFixed(1)}%)</span>
			</div>
		{/if}

		<!-- Cancel stream button (show during streaming) -->
		{#if isStreaming}
			<button
				type="button"
				on:click={handleCancelStream}
				class="cancel-button"
				aria-label="Cancel stream"
			>
				<svg
					width="20"
					height="20"
					viewBox="0 0 20 20"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<rect x="4" y="4" width="12" height="12" rx="1" fill="currentColor" />
				</svg>
				<span>Stop</span>
			</button>
		{/if}
	</div>
</div>

<style>
	.chat-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 1.5rem;
		border-bottom: 1px solid rgba(226, 232, 240, 0.8);
		background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.98) 100%);
		backdrop-filter: blur(12px);
		position: sticky;
		top: 0;
		z-index: 10;
		min-height: 64px;
		box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
	}

	.header-left {
		flex: 1;
		display: flex;
		align-items: center;
	}

	.header-right {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.conversation-title {
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: #111827;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.25rem 0.5rem;
		border-radius: 0.375rem;
		transition: background-color 0.2s ease;
	}

	.conversation-title:hover {
		background-color: #f3f4f6;
	}

	.edit-icon {
		opacity: 0;
		transition: opacity 0.2s ease;
		color: #9ca3af;
	}

	.conversation-title:hover .edit-icon {
		opacity: 1;
	}

	.conversation-title-input {
		margin: 0;
		padding: 0.25rem 0.5rem;
		font-size: 1.25rem;
		font-weight: 600;
		color: #111827;
		border: 2px solid #3b82f6;
		border-radius: 0.375rem;
		background-color: #ffffff;
		outline: none;
		width: 100%;
		max-width: 500px;
	}

	.conversation-id {
		margin: 0;
		font-size: 0.75rem;
		color: #6b7280;
		font-weight: 500;
		white-space: nowrap;
	}

	.project-selector-wrapper {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.project-label {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		font-size: 0.75rem;
		font-weight: 500;
		color: #6b7280;
	}

	.project-label svg {
		flex-shrink: 0;
	}

	.project-select {
		padding: 0.25rem 0.5rem;
		font-size: 0.75rem;
		border: 1px solid #e5e7eb;
		border-radius: 0.375rem;
		background-color: #ffffff;
		color: #111827;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.project-select:hover:not(:disabled) {
		border-color: #d1d5db;
		background-color: #f9fafb;
	}

	.project-select:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	.project-select:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.token-usage {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.5rem 0.875rem;
		background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
		color: #2563eb;
		border: 1px solid #bfdbfe;
		border-radius: 0.5rem;
		font-size: 0.75rem;
		font-weight: 500;
		white-space: nowrap;
		box-shadow: 0 2px 6px rgba(59, 130, 246, 0.15);
		transition: all 0.25s ease;
	}

	.token-usage:hover {
		box-shadow: 0 4px 10px rgba(59, 130, 246, 0.25);
		transform: translateY(-1px);
	}

	.token-usage svg {
		flex-shrink: 0;
	}

	.token-count {
		font-weight: 700;
	}

	.token-percentage {
		color: #3b82f6;
		font-weight: 500;
	}

	.token-usage.warning {
		background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%);
		color: #ea580c;
		border-color: #fdba74;
		box-shadow: 0 2px 6px rgba(249, 115, 22, 0.2);
	}

	.token-usage.warning:hover {
		box-shadow: 0 4px 10px rgba(249, 115, 22, 0.3);
	}

	.token-usage.warning .token-percentage {
		color: #f97316;
	}

	.token-usage.critical {
		background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
		color: #b91c1c;
		border-color: #fca5a5;
		box-shadow: 0 2px 6px rgba(220, 38, 38, 0.2);
		animation: pulse 2s infinite;
	}

	@keyframes pulse {
		0%, 100% {
			box-shadow: 0 2px 6px rgba(220, 38, 38, 0.2);
		}
		50% {
			box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
		}
	}

	.token-usage.critical:hover {
		box-shadow: 0 4px 10px rgba(220, 38, 38, 0.35);
	}

	.token-usage.critical .token-percentage {
		color: #dc2626;
		font-weight: 700;
	}

	.cancel-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 1.125rem;
		background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
		color: #b91c1c;
		border: 1px solid #fca5a5;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
		box-shadow: 0 2px 6px rgba(220, 38, 38, 0.2);
	}

	.cancel-button:hover {
		background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
		border-color: #f87171;
		box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
		transform: translateY(-1px);
	}

	.cancel-button:active {
		transform: translateY(0) scale(0.98);
	}

	@media (max-width: 768px) {
		.chat-header {
			padding: 0.75rem 1rem;
		}

		.conversation-title {
			font-size: 1.125rem;
		}
	}
</style>
