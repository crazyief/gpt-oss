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

// Props
export let message: Message;

/**
 * Format timestamp to human-readable time
 *
 * Examples: "14:32", "09:05"
 *
 * WHY time-only instead of full datetime:
 * - Context: Date is visible in conversation metadata
 * - Space-efficient: Short timestamp fits in bubble
 * - Scanning: Easy to glance at message timing
 *
 * @param isoDate - ISO 8601 datetime string
 * @returns Formatted time string (HH:MM)
 */
function formatTime(isoDate: string): string {
	const date = new Date(isoDate);
	const hours = date.getHours().toString().padStart(2, '0');
	const minutes = date.getMinutes().toString().padStart(2, '0');
	return `${hours}:${minutes}`;
}
</script>

<div class="user-message-container">
	<!-- User message bubble -->
	<div class="user-message-bubble">
		<!-- Message content (plain text, pre-wrap to preserve line breaks) -->
		<div class="message-content">
			{message.content}
		</div>

		<!-- Timestamp -->
		<div class="timestamp" title={message.created_at}>
			{formatTime(message.created_at)}
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
	 * User message container
	 *
	 * Layout: Flexbox with bubble (left) + avatar (right)
	 * WHY flex-direction: row-reverse:
	 * - Right alignment: Avatar on right, bubble grows leftward
	 * - Common pattern: WhatsApp, Telegram use this layout
	 */
	.user-message-container {
		display: flex;
		flex-direction: row-reverse; /* Avatar right, bubble left */
		align-items: flex-start;
		gap: 0.75rem;
		margin: 1rem 0;
		padding: 0 1rem;
	}

	/**
	 * User message bubble
	 *
	 * WHY max-width: 70%:
	 * - Readability: Wide text is hard to read (optimal line length = 50-75 characters)
	 * - Layout: Prevents bubble from spanning entire width
	 * - Common pattern: Chat apps use 60-80% max width
	 */
	.user-message-bubble {
		max-width: 70%;
		padding: 0.75rem 1rem;
		background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); /* Blue gradient */
		color: white;
		border-radius: 1rem 1rem 0 1rem; /* Rounded except bottom-right */
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	/**
	 * Message content
	 *
	 * WHY white-space: pre-wrap:
	 * - Preserve line breaks: User's Enter key creates new line
	 * - Word wrap: Long words wrap instead of overflow
	 * - No markdown: User messages are plain text
	 */
	.message-content {
		font-size: 0.9375rem;
		line-height: 1.5;
		white-space: pre-wrap;
		word-wrap: break-word;
	}

	/**
	 * Timestamp styling
	 *
	 * WHY right-aligned and small:
	 * - Non-intrusive: Doesn't distract from message content
	 * - Metadata: Secondary information
	 * - Scannable: Right alignment makes timestamps easy to compare
	 */
	.timestamp {
		margin-top: 0.5rem;
		font-size: 0.75rem;
		color: rgba(255, 255, 255, 0.8); /* Semi-transparent white */
		text-align: right;
	}

	/**
	 * User avatar
	 *
	 * WHY icon instead of profile picture:
	 * - Stage 1: No user authentication/profiles yet
	 * - Placeholder: Generic user icon
	 * - Future: Replace with actual profile picture (Stage 6)
	 */
	.user-avatar {
		flex-shrink: 0; /* Don't shrink avatar */
		width: 2rem;
		height: 2rem;
		display: flex;
		align-items: center;
		justify-content: center;
		background-color: #eff6ff; /* Blue 50 */
		color: #3b82f6; /* Blue 500 */
		border-radius: 50%;
	}

	/**
	 * Responsive: Full-width on mobile
	 *
	 * WHY increase max-width on mobile:
	 * - Screen space: Mobile screens are narrow, need more width
	 * - Readability: Still limited to prevent full-width text
	 */
	@media (max-width: 768px) {
		.user-message-bubble {
			max-width: 85%;
		}
	}
</style>
