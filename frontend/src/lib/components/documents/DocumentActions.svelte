<script lang="ts">
/**
 * DocumentActions component
 *
 * Action buttons for document operations (download, delete)
 */

import { createEventDispatcher } from 'svelte';

export let documentId: number;

const dispatch = createEventDispatcher<{
	download: void;
	delete: void;
}>();

function handleDownload() {
	dispatch('download');
}

function handleDelete() {
	dispatch('delete');
}
</script>

<div class="actions">
	<button
		type="button"
		class="action-button download"
		on:click={handleDownload}
		aria-label="Download document"
		title="Download"
	>
		<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
			<path
				d="M8 10V2M8 10L6 8M8 10L10 8M2 11V13C2 13.5523 2.44772 14 3 14H13C13.5523 14 14 13.5523 14 13V11"
				stroke="currentColor"
				stroke-width="1.5"
				stroke-linecap="round"
				stroke-linejoin="round"
			/>
		</svg>
	</button>

	<button
		type="button"
		class="action-button delete"
		on:click={handleDelete}
		aria-label="Delete document"
		title="Delete"
	>
		<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
			<path
				d="M6 2H10M2 4H14M12 4L11.7 10.3C11.6 11.8 11.5 12.6 11 13.1C10.6 13.5 10 13.8 9.3 13.9C8.5 14 7.5 14 6.5 14H6C5 14 4 14 3.2 13.9C2.5 13.8 1.9 13.5 1.5 13.1C1 12.6 0.9 11.8 0.8 10.3L0.5 4"
				stroke="currentColor"
				stroke-width="1.5"
				stroke-linecap="round"
			/>
		</svg>
	</button>
</div>

<style>
	.actions {
		display: flex;
		gap: 0.5rem;
		align-items: center;
	}

	.action-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		border: none;
		border-radius: 6px;
		background: rgba(255, 255, 255, 0.05);
		color: rgba(255, 255, 255, 0.6);
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.action-button:hover {
		background: rgba(255, 255, 255, 0.1);
		color: rgba(255, 255, 255, 0.9);
		transform: translateY(-1px);
	}

	.action-button.download:hover {
		background: rgba(99, 102, 241, 0.2);
		color: rgba(99, 102, 241, 1);
	}

	.action-button.delete:hover {
		background: rgba(239, 68, 68, 0.2);
		color: rgba(239, 68, 68, 1);
	}

	.action-button:focus {
		outline: 2px solid rgba(99, 102, 241, 0.5);
		outline-offset: 2px;
	}
</style>
