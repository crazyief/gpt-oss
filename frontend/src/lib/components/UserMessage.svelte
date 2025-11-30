<script lang="ts">
/**
 * UserMessage component
 *
 * Purpose: Display user message in chat interface
 *
 * Features:
 * - Simple text bubble (no markdown rendering for user messages)
 * - Blue gradient background (ChatGPT-inspired)
 * - Right-aligned layout
 * - Timestamp display
 * - User avatar/icon
 *
 * Design decisions:
 * - No markdown: User messages are plain text (no need to parse)
 * - Right alignment: Common chat UX (user = right, AI = left)
 * - Blue gradient: Matches primary action color (New Chat button, etc.)
 *
 * WHY separate component from AssistantMessage:
 * - Different styling: User vs AI message appearance differs
 * - Different features: AI has reactions, regenerate; user doesn't
 * - Clarity: Easier to read/maintain than conditional rendering
 */

import type { Message } from '$lib/types';
import { formatTime } from '$lib/utils/date';
import { logger } from '$lib/utils/logger';

// Props
export let message: Message;

// Copy button state
let copySuccess = false;

/**
 * Copy message content to clipboard
 */
async function handleCopy() {
	try {
		await navigator.clipboard.writeText(message.content);
		copySuccess = true;
		setTimeout(() => {
			copySuccess = false;
		}, 2000);
	} catch (err) {
		logger.error('Failed to copy user message:', { error: err });
	}
}

// formatTime moved to $lib/utils/date.ts
// WHY centralized utility: Ensures consistent UTC timestamp handling across all components
</script>

<div class="user-message-container">
	<!-- User message bubble -->
	<div class="user-message-bubble">
		<!-- Message content (plain text, pre-wrap to preserve line breaks) -->
		<div class="message-content">
			{message.content}
		</div>

		<!-- Timestamp and Copy button footer -->
		<div class="message-footer">
			<!-- Timestamp (left) -->
			<div class="timestamp" title={message.created_at}>
				{formatTime(message.created_at)}
			</div>

			<!-- Copy button (right) -->
			<button type="button" on:click={handleCopy} class="copy-button" aria-label="Copy message">
				{#if copySuccess}
					<!-- Checkmark icon -->
					<svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M12 3.5L5.5 10 2 6.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
					<span>Copied!</span>
				{:else}
					<!-- Copy icon -->
					<svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
						<rect x="4" y="4" width="8" height="8" rx="1" stroke="currentColor" stroke-width="1.2"/>
						<path d="M2.5 10V2.5a1 1 0 0 1 1-1H10" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
					</svg>
					<span>Copy</span>
				{/if}
			</button>
		</div>
	</div>

	<!-- User avatar/icon (right side) -->
	<div class="user-avatar">
		<svg
			width="24"
			height="24"
			viewBox="0 0 24 24"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
		>
			<circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="2" />
			<path
				d="M4 20c0-4 3-7 8-7s8 3 8 7"
				stroke="currentColor"
				stroke-width="2"
				stroke-linecap="round"
			/>
		</svg>
	</div>
</div>

<style>
	/**
	 * User message container (theme-aware)
	 */
	.user-message-container {
		display: flex;
		flex-direction: row-reverse;
		align-items: flex-start;
		gap: 0.75rem;
		margin: 1rem 0;
		padding: 0 1rem;
		animation: slideIn 0.3s ease-out;
	}

	/**
	 * User message bubble (theme-aware)
	 */
	.user-message-bubble {
		position: relative;
		max-width: 70%;
		padding: 1rem 1.25rem;
		background: var(--user-bg);
		color: var(--user-text, white);
		border-radius: 1.25rem 1.25rem 0.25rem 1.25rem;
		box-shadow: var(--user-shadow, 0 4px 16px rgba(99, 102, 241, 0.4));
		transition: all 0.2s ease;
		backdrop-filter: blur(10px);
	}

	.user-message-bubble:hover {
		transform: translateY(-1px);
	}

	.user-message-bubble::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 2px;
		background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%);
		border-radius: 1.25rem 1.25rem 0 0;
	}

	.message-content {
		font-size: 0.9375rem;
		line-height: 1.5;
		white-space: pre-wrap;
		word-wrap: break-word;
		margin-bottom: 0.75rem;
	}

	.message-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
	}

	.timestamp {
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.7);
		flex-shrink: 0;
	}

	.copy-button {
		display: flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.25rem 0.5rem;
		background: rgba(255, 255, 255, 0.15);
		color: rgba(255, 255, 255, 0.9);
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 0.375rem;
		font-size: 0.75rem;
		cursor: pointer;
		transition: all 0.2s ease;
		flex-shrink: 0;
		white-space: nowrap;
	}

	.copy-button:hover {
		background: rgba(255, 255, 255, 0.25);
		border-color: rgba(255, 255, 255, 0.4);
		transform: scale(1.05);
	}

	.copy-button svg {
		flex-shrink: 0;
	}

	.user-avatar {
		flex-shrink: 0;
		width: 2.25rem;
		height: 2.25rem;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--user-bg);
		color: var(--user-text, white);
		border-radius: 50%;
		border: 2px solid var(--accent);
		box-shadow: 0 2px 8px var(--accent-muted);
		transition: all 0.3s ease;
	}

	.user-avatar:hover {
		transform: scale(1.05);
	}

	@media (max-width: 768px) {
		.user-message-bubble {
			max-width: 85%;
		}
	}
</style>
