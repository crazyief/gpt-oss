<script lang="ts">
	/**
	 * DocumentsTab - Full document management panel
	 *
	 * Features:
	 * - Document upload (drag & drop)
	 * - Document list with sorting/filtering
	 * - Document actions (download, delete)
	 */
	import DocumentUploader from '$lib/components/documents/DocumentUploader.svelte';
	import DocumentList from '$lib/components/documents/DocumentList.svelte';
	import { documents, loadDocuments, clearDocuments } from '$lib/stores/documents';
	import { currentProjectId } from '$lib/stores/projects';
	import { onMount, onDestroy } from 'svelte';

	let abortController: AbortController | null = null;
	let unsubscribe: (() => void) | null = null;

	onMount(() => {
		unsubscribe = currentProjectId.subscribe((projectId) => {
			if (abortController) {
				abortController.abort();
			}
			if (projectId !== null) {
				abortController = new AbortController();
				// Don't await here - let it run async without blocking
				loadDocuments(projectId, { signal: abortController.signal }).catch((error) => {
					// Silently ignore AbortError (happens when switching projects)
					// Other errors are logged by loadDocuments
				});
			} else {
				clearDocuments();
			}
		});
	});

	onDestroy(() => {
		if (abortController) {
			abortController.abort();
		}
		if (unsubscribe) {
			unsubscribe();
		}
	});

	function handleDocumentUploaded() {
		if ($currentProjectId !== null) {
			loadDocuments($currentProjectId);
		}
	}
</script>

<div class="documents-tab">
	<header class="documents-header">
		<h2 class="documents-title">
			<svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
			</svg>
			Documents
		</h2>
		<span class="document-count">{$documents.documents.length} files</span>
	</header>

	<div class="documents-content">
		<!-- Upload Section -->
		<section class="upload-section">
			{#if $currentProjectId !== null}
				<DocumentUploader projectId={$currentProjectId} on:uploaded={handleDocumentUploaded} />
			{/if}
		</section>

		<!-- Document List -->
		<section class="list-section">
			{#if $documents.isLoading}
				<div class="loading-state">
					<div class="spinner"></div>
					<p>Loading documents...</p>
				</div>
			{:else if $documents.error}
				<div class="error-state">
					<svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<circle cx="12" cy="12" r="10" />
						<line x1="12" y1="8" x2="12" y2="12" />
						<line x1="12" y1="16" x2="12.01" y2="16" />
					</svg>
					<p>{$documents.error}</p>
					<button class="retry-btn" on:click={() => $currentProjectId && loadDocuments($currentProjectId)}>
						Retry
					</button>
				</div>
			{:else if $documents.documents.length === 0}
				<div class="empty-state">
					<svg class="empty-icon" viewBox="0 0 64 64" fill="none">
						<rect x="12" y="8" width="40" height="48" rx="4" stroke="currentColor" stroke-width="3"/>
						<path d="M24 24h16M24 32h16M24 40h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
					</svg>
					<h3>No documents yet</h3>
					<p>Upload documents to get started with knowledge-based chat</p>
				</div>
			{:else}
				<DocumentList />
			{/if}
		</section>
	</div>
</div>

<style>
	.documents-tab {
		display: flex;
		flex-direction: column;
		height: 100%;
		background: var(--bg-primary);
		overflow: hidden;
	}

	.documents-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 1.5rem;
		border-bottom: 1px solid var(--border-primary);
		flex-shrink: 0;
	}

	.documents-title {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin: 0;
		font-size: 1.25rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.title-icon {
		width: 24px;
		height: 24px;
		color: var(--accent);
	}

	.document-count {
		font-size: 0.875rem;
		color: var(--text-muted);
		padding: 0.25rem 0.75rem;
		background: var(--bg-tertiary);
		border-radius: 9999px;
	}

	.documents-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		padding: 1.5rem;
		gap: 1.5rem;
	}

	.upload-section {
		flex-shrink: 0;
	}

	.list-section {
		flex: 1;
		overflow-y: auto;
	}

	/* Loading State */
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 200px;
		color: var(--text-secondary);
	}

	.spinner {
		width: 32px;
		height: 32px;
		border: 3px solid var(--border-primary);
		border-top-color: var(--accent);
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
		margin-bottom: 1rem;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}

	/* Error State */
	.error-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 200px;
		color: var(--error);
		text-align: center;
	}

	.error-icon {
		width: 48px;
		height: 48px;
		margin-bottom: 1rem;
	}

	.retry-btn {
		margin-top: 1rem;
		padding: 0.5rem 1rem;
		background: var(--accent);
		color: var(--text-inverse);
		border: none;
		border-radius: 0.5rem;
		font-weight: 500;
		cursor: pointer;
		transition: background 0.2s ease;
	}

	.retry-btn:hover {
		background: var(--accent-hover);
	}

	/* Empty State */
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 200px;
		text-align: center;
		color: var(--text-secondary);
	}

	.empty-icon {
		width: 64px;
		height: 64px;
		margin-bottom: 1rem;
		opacity: 0.5;
	}

	.empty-state h3 {
		margin: 0 0 0.5rem 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--text-primary);
	}

	.empty-state p {
		margin: 0;
		font-size: 0.875rem;
	}
</style>
