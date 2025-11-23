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
	<div class="conversation-info">
		{#if isEditingTitle}
			<!-- Title input (edit mode) -->
			<input
				type="text"
				bind:value={editTitleValue}
				on:keydown={handleTitleKeydown}
				on:blur={saveEditTitle}
				class="conversation-title-input"
				placeholder="Enter conversation title"
				autofocus
			/>
		{:else}
			<!-- Title display (click to edit) -->
			<h1
				class="conversation-title"
				on:click={startEditTitle}
				on:keydown={(e) => e.key === 'Enter' && startEditTitle()}
				role="button"
				tabindex="0"
				title="Click to edit title"
			>
				{conversationTitle}
				<svg class="edit-icon" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M11.5 2.5l2 2L6 12H4v-2l7.5-7.5z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
				</svg>
			</h1>
		{/if}

		{#if conversationId}
			<p class="conversation-id">ID: {conversationId}</p>
		{/if}

		<!-- Project selector -->
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
	</div>

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

<style>
	.chat-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 1.5rem;
		border-bottom: 1px solid #e5e7eb;
		background-color: #ffffff;
		position: sticky;
		top: 0;
		z-index: 10;
	}

	.conversation-info {
		flex: 1;
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
		margin: 0.25rem 0 0 0;
		font-size: 0.75rem;
		color: #6b7280;
	}

	.project-selector-wrapper {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 0.5rem;
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
		margin-top: 0.5rem;
		padding: 0.375rem 0.625rem;
		background-color: #eff6ff;
		color: #3b82f6;
		border: 1px solid #dbeafe;
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 500;
		width: fit-content;
	}

	.token-usage svg {
		flex-shrink: 0;
	}

	.token-count {
		font-weight: 600;
	}

	.token-percentage {
		color: #60a5fa;
		font-weight: 400;
	}

	.token-usage.warning {
		background-color: #fff7ed;
		color: #f97316;
		border-color: #fed7aa;
	}

	.token-usage.warning .token-percentage {
		color: #fb923c;
	}

	.token-usage.critical {
		background-color: #fef2f2;
		color: #dc2626;
		border-color: #fecaca;
	}

	.token-usage.critical .token-percentage {
		color: #ef4444;
	}

	.cancel-button {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background-color: #fee2e2;
		color: #dc2626;
		border: 1px solid #fecaca;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.cancel-button:hover {
		background-color: #fecaca;
		border-color: #fca5a5;
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
