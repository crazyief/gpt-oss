<script lang="ts">
/**
 * ProjectStats component
 *
 * Display project statistics in a clean card layout
 */

import type { ProjectStats } from '$lib/types';

export let stats: ProjectStats;

function formatFileSize(bytes: number): string {
	if (bytes < 1024) return `${bytes} B`;
	if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
	if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
	return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

function formatRelativeDate(dateString: string | null): string {
	if (!dateString) return 'Never';
	const date = new Date(dateString);
	const now = new Date();
	const diffMs = now.getTime() - date.getTime();
	const diffMins = Math.floor(diffMs / 60000);
	const diffHours = Math.floor(diffMs / 3600000);
	const diffDays = Math.floor(diffMs / 86400000);

	if (diffMins < 1) return 'just now';
	if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
	if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
	if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
	return date.toLocaleDateString();
}
</script>

<div class="stats-container">
	<!-- Documents -->
	<div class="stat-card">
		<div class="stat-icon documents">
			<svg
				width="24"
				height="24"
				viewBox="0 0 24 24"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M7 4H13L17 8V18C17 19.1046 16.1046 20 15 20H7C5.89543 20 5 19.1046 5 18V6C5 4.89543 5.89543 4 7 4Z"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
				<path d="M13 4V8H17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
			</svg>
		</div>
		<div class="stat-content">
			<div class="stat-label">Documents</div>
			<div class="stat-value">{stats.document_count}</div>
		</div>
	</div>

	<!-- Conversations -->
	<div class="stat-card">
		<div class="stat-icon conversations">
			<svg
				width="24"
				height="24"
				viewBox="0 0 24 24"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M8 10H16M8 14H11M7 18L3 21V5C3 3.89543 3.89543 3 5 3H19C20.1046 3 21 3.89543 21 5V17C21 18.1046 20.1046 19 19 19H7Z"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
		</div>
		<div class="stat-content">
			<div class="stat-label">Conversations</div>
			<div class="stat-value">{stats.conversation_count}</div>
		</div>
	</div>

	<!-- Messages -->
	<div class="stat-card">
		<div class="stat-icon messages">
			<svg
				width="24"
				height="24"
				viewBox="0 0 24 24"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M7 8H17M7 12H13M21 12C21 16.9706 16.9706 21 12 21C10.2924 21 8.71635 20.4522 7.4 19.5L3 21L4.5 16.6C3.54784 15.2837 3 13.7076 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
		</div>
		<div class="stat-content">
			<div class="stat-label">Messages</div>
			<div class="stat-value">{stats.message_count}</div>
		</div>
	</div>

	<!-- Storage -->
	<div class="stat-card">
		<div class="stat-icon storage">
			<svg
				width="24"
				height="24"
				viewBox="0 0 24 24"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M5 7H19M5 12H19M5 17H19M3 5C3 3.89543 3.89543 3 5 3H19C20.1046 3 21 3.89543 21 5V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V5Z"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
		</div>
		<div class="stat-content">
			<div class="stat-label">Storage</div>
			<div class="stat-value">{formatFileSize(stats.total_document_size)}</div>
		</div>
	</div>

	<!-- Last Activity -->
	<div class="stat-card wide">
		<div class="stat-icon activity">
			<svg
				width="24"
				height="24"
				viewBox="0 0 24 24"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M12 6V12L16 14M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
		</div>
		<div class="stat-content">
			<div class="stat-label">Last Activity</div>
			<div class="stat-value">{formatRelativeDate(stats.last_activity_at)}</div>
		</div>
	</div>
</div>

<style>
	.stats-container {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
	}

	.stat-card {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1.25rem;
		background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.08));
		border: 1px solid rgba(255, 255, 255, 0.1);
		border-radius: 10px;
		transition: all 0.3s ease;
	}

	.stat-card:hover {
		background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(139, 92, 246, 0.12));
		border-color: rgba(99, 102, 241, 0.3);
		transform: translateY(-2px);
	}

	.stat-card.wide {
		grid-column: span 2;
	}

	.stat-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 48px;
		height: 48px;
		border-radius: 8px;
		flex-shrink: 0;
	}

	.stat-icon.documents {
		background: rgba(239, 68, 68, 0.15);
		color: rgba(239, 68, 68, 0.9);
	}

	.stat-icon.conversations {
		background: rgba(99, 102, 241, 0.15);
		color: rgba(99, 102, 241, 0.9);
	}

	.stat-icon.messages {
		background: rgba(139, 92, 246, 0.15);
		color: rgba(139, 92, 246, 0.9);
	}

	.stat-icon.storage {
		background: rgba(34, 197, 94, 0.15);
		color: rgba(34, 197, 94, 0.9);
	}

	.stat-icon.activity {
		background: rgba(6, 182, 212, 0.15);
		color: rgba(6, 182, 212, 0.9);
	}

	.stat-content {
		flex: 1;
		min-width: 0;
	}

	.stat-label {
		font-size: 0.8125rem;
		font-weight: 500;
		color: rgba(255, 255, 255, 0.6);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: 0.25rem;
	}

	.stat-value {
		font-size: 1.5rem;
		font-weight: 700;
		color: rgba(255, 255, 255, 0.95);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	@media (max-width: 768px) {
		.stats-container {
			grid-template-columns: 1fr;
		}

		.stat-card.wide {
			grid-column: span 1;
		}
	}
</style>
