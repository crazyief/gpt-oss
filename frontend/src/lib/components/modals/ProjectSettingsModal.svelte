<script lang="ts">
/**
 * ProjectSettingsModal component
 *
 * Modal wrapper for ProjectSettings component.
 * Handles project editing, saving, and deletion.
 */

import { createEventDispatcher } from 'svelte';
import ProjectSettings from '../project/ProjectSettings.svelte';
import { updateProject, deleteProject } from '$lib/services/api/projects';
import { toast } from '$lib/stores/toast';
import { logger } from '$lib/utils/logger';
import type { Project } from '$lib/types';

export let isOpen = false;
export let project: Project | null = null;

let isProcessing = false;

const dispatch = createEventDispatcher<{
	updated: Project;
	deleted: number;
	close: void;
}>();

function handleKeydown(e: KeyboardEvent) {
	if (e.key === 'Escape' && !isProcessing) {
		handleClose();
	}
}

function handleClose() {
	if (isProcessing) return;
	dispatch('close');
}

async function handleSave(event: CustomEvent<{ name: string; description: string }>) {
	if (!project) return;

	try {
		isProcessing = true;
		const { name, description } = event.detail;
		const updated = await updateProject(project.id, { name, description });
		dispatch('updated', updated);
		handleClose();
		logger.info('Project updated', { projectId: project.id });
	} catch (error) {
		const errorMsg = error instanceof Error ? error.message : 'Failed to update project';
		toast.error(errorMsg);
		logger.error('Failed to update project', { projectId: project?.id, error });
	} finally {
		isProcessing = false;
	}
}

async function handleDelete() {
	if (!project) return;

	try {
		isProcessing = true;
		await deleteProject(project.id);

		// Dispatch event - parent (Sidebar) handles store cleanup
		dispatch('deleted', project.id);
		handleClose();
		toast.success('Project deleted successfully');
		logger.info('Project deleted', { projectId: project.id });
	} catch (error) {
		const errorMsg = error instanceof Error ? error.message : 'Failed to delete project';
		toast.error(errorMsg);
		logger.error('Failed to delete project', { projectId: project?.id, error });
	} finally {
		isProcessing = false;
	}
}

function handleCancel() {
	handleClose();
}
</script>

{#if isOpen && project}
	<!-- Modal overlay -->
	<div
		class="modal-overlay"
		on:click={handleClose}
		on:keydown={handleKeydown}
		role="button"
		tabindex="-1"
		aria-label="Close modal"
	>
		<!-- Modal content -->
		<div
			class="modal-content"
			on:click|stopPropagation
			on:keydown|stopPropagation
			role="dialog"
			aria-modal="true"
			aria-labelledby="settings-modal-title"
		>
			<!-- Modal header -->
			<div class="modal-header">
				<h2 id="settings-modal-title" class="modal-title">Project Settings</h2>
				<button
					type="button"
					class="close-button"
					on:click={handleClose}
					disabled={isProcessing}
					aria-label="Close dialog"
				>
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
				</button>
			</div>

			<!-- Modal body -->
			<div class="modal-body">
				<ProjectSettings
					{project}
					on:save={handleSave}
					on:delete={handleDelete}
					on:cancel={handleCancel}
				/>
			</div>

			<!-- Processing overlay -->
			{#if isProcessing}
				<div class="processing-overlay">
					<svg class="spinner" width="32" height="32" viewBox="0 0 32 32">
						<circle
							cx="16"
							cy="16"
							r="12"
							stroke="currentColor"
							stroke-width="3"
							fill="none"
							stroke-dasharray="60"
							stroke-linecap="round"
						>
							<animateTransform
								attributeName="transform"
								type="rotate"
								from="0 16 16"
								to="360 16 16"
								dur="1s"
								repeatCount="indefinite"
							/>
						</circle>
					</svg>
				</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.7);
		backdrop-filter: blur(4px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		animation: fadeIn 0.2s ease-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	.modal-content {
		position: relative;
		background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 12px;
		max-width: 600px;
		width: 90%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
		animation: slideUp 0.3s ease-out;
	}

	@keyframes slideUp {
		from {
			transform: translateY(20px);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.25rem 1.5rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.modal-title {
		font-size: 1.25rem;
		font-weight: 600;
		color: rgba(255, 255, 255, 0.95);
		margin: 0;
	}

	.close-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		border: none;
		border-radius: 6px;
		background: rgba(255, 255, 255, 0.1);
		color: rgba(255, 255, 255, 0.7);
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.close-button:hover:not(:disabled) {
		background: rgba(255, 255, 255, 0.2);
		color: rgba(255, 255, 255, 0.9);
	}

	.close-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.modal-body {
		padding: 1.5rem;
	}

	.processing-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(15, 23, 42, 0.8);
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 12px;
	}

	.spinner {
		color: #60a5fa;
	}

	/* Custom scrollbar */
	.modal-content::-webkit-scrollbar {
		width: 8px;
	}

	.modal-content::-webkit-scrollbar-track {
		background: rgba(255, 255, 255, 0.05);
	}

	.modal-content::-webkit-scrollbar-thumb {
		background: rgba(255, 255, 255, 0.2);
		border-radius: 4px;
	}

	.modal-content::-webkit-scrollbar-thumb:hover {
		background: rgba(255, 255, 255, 0.3);
	}
</style>
