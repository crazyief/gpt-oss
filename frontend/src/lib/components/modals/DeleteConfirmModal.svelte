<script lang="ts">
/**
 * DeleteConfirmModal component
 *
 * Confirmation dialog for destructive actions
 *
 * Features:
 * - Modal overlay with backdrop
 * - Optional "type to confirm" safety check
 * - Keyboard support (Escape to cancel)
 * - Focus trap
 */

import { createEventDispatcher, onMount } from 'svelte';

export let isOpen = false;
export let title = 'Confirm Delete';
export let message: string;
export let confirmText = 'Delete';
export let requireTyping: string | null = null; // Text user must type to confirm

let typedText = '';
let confirmButton: HTMLButtonElement;

const dispatch = createEventDispatcher<{
	confirm: void;
	cancel: void;
}>();

$: canConfirm = requireTyping ? typedText === requireTyping : true;

function handleConfirm() {
	if (!canConfirm) return;
	dispatch('confirm');
	close();
}

function handleCancel() {
	dispatch('cancel');
	close();
}

function close() {
	typedText = '';
}

function handleKeydown(e: KeyboardEvent) {
	if (e.key === 'Escape') {
		handleCancel();
	}
}

onMount(() => {
	if (isOpen && confirmButton) {
		confirmButton.focus();
	}
});
</script>

{#if isOpen}
	<!-- Modal overlay -->
	<div
		class="modal-overlay"
		on:click={handleCancel}
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
			aria-labelledby="modal-title"
		>
			<!-- Modal header -->
			<div class="modal-header">
				<h2 id="modal-title" class="modal-title">{title}</h2>
				<button
					type="button"
					class="close-button"
					on:click={handleCancel}
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
				<p class="modal-message">{message}</p>

				{#if requireTyping}
					<div class="confirm-input-container">
						<label for="confirm-input" class="confirm-label">
							Type <strong>{requireTyping}</strong> to confirm:
						</label>
						<input
							id="confirm-input"
							type="text"
							bind:value={typedText}
							class="confirm-input"
							placeholder={requireTyping}
							autocomplete="off"
						/>
					</div>
				{/if}
			</div>

			<!-- Modal footer -->
			<div class="modal-footer">
				<button type="button" class="button button-cancel" on:click={handleCancel}> Cancel </button>
				<button
					bind:this={confirmButton}
					type="button"
					class="button button-confirm"
					disabled={!canConfirm}
					on:click={handleConfirm}
				>
					{confirmText}
				</button>
			</div>
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
		background: rgba(0, 0, 0, 0.75);
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
		background: linear-gradient(135deg, rgba(30, 30, 50, 0.95), rgba(40, 40, 60, 0.95));
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 12px;
		max-width: 500px;
		width: 90%;
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
		padding: 1.5rem;
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
		background: transparent;
		color: rgba(255, 255, 255, 0.6);
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.close-button:hover {
		background: rgba(255, 255, 255, 0.1);
		color: rgba(255, 255, 255, 0.9);
	}

	.modal-body {
		padding: 1.5rem;
	}

	.modal-message {
		font-size: 0.9375rem;
		color: rgba(255, 255, 255, 0.8);
		line-height: 1.6;
		margin: 0 0 1rem 0;
	}

	.confirm-input-container {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.confirm-label {
		font-size: 0.875rem;
		color: rgba(255, 255, 255, 0.7);
	}

	.confirm-label strong {
		color: rgba(239, 68, 68, 0.9);
		font-weight: 600;
	}

	.confirm-input {
		width: 100%;
		padding: 0.75rem;
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 6px;
		background: rgba(255, 255, 255, 0.05);
		color: rgba(255, 255, 255, 0.9);
		font-size: 0.9375rem;
		transition: all 0.2s ease;
	}

	.confirm-input:focus {
		outline: none;
		border-color: rgba(99, 102, 241, 0.5);
		background: rgba(255, 255, 255, 0.08);
	}

	.modal-footer {
		display: flex;
		gap: 0.75rem;
		padding: 1.5rem;
		border-top: 1px solid rgba(255, 255, 255, 0.1);
		justify-content: flex-end;
	}

	.button {
		padding: 0.625rem 1.25rem;
		border-radius: 6px;
		font-size: 0.9375rem;
		font-weight: 500;
		cursor: pointer;
		border: none;
		transition: all 0.2s ease;
	}

	.button-cancel {
		background: rgba(255, 255, 255, 0.1);
		color: rgba(255, 255, 255, 0.9);
	}

	.button-cancel:hover {
		background: rgba(255, 255, 255, 0.15);
	}

	.button-confirm {
		background: linear-gradient(135deg, #ef4444, #dc2626);
		color: white;
	}

	.button-confirm:hover:not(:disabled) {
		background: linear-gradient(135deg, #dc2626, #b91c1c);
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
	}

	.button-confirm:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.button:focus {
		outline: 2px solid rgba(99, 102, 241, 0.5);
		outline-offset: 2px;
	}
</style>
