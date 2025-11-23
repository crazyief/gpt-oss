<script lang="ts">
/**
 * StreamingIndicator component
 *
 * Purpose: Display typing animation during AI response generation
 *
 * Features:
 * - Animated dots (pulse effect)
 * - Token count display
 * - Completion time display
 *
 * Design decisions:
 * - Animated dots: Common pattern (iMessage, Slack)
 * - Staggered animation: Dots pulse at different times
 * - Metadata display: Token count, completion time
 *
 * WHY separate component:
 * - Reusability: Can be used in other message types
 * - Animation logic: Self-contained CSS animations
 * - Conditional rendering: Only shown when streaming
 */

import type { Message } from '$lib/types';

// Props
export let isStreaming: boolean;
export let tokenCount: number = 0;
export let completionTimeMs: number | undefined = undefined;
</script>

{#if isStreaming}
	<!-- Typing animation (animated dots) -->
	<div class="streaming-indicator">
		<span class="dot"></span>
		<span class="dot"></span>
		<span class="dot"></span>
	</div>
{/if}

<style>
	/**
	 * Streaming indicator (typing animation)
	 *
	 * WHY animated dots:
	 * - Feedback: User knows AI is "thinking"
	 * - Common pattern: iMessage, Slack use this
	 */
	.streaming-indicator {
		display: flex;
		gap: 0.375rem;
		margin-top: 0.5rem;
	}

	.dot {
		width: 0.5rem;
		height: 0.5rem;
		background-color: #9ca3af; /* Gray 400 */
		border-radius: 50%;
		animation: pulse 1.5s ease-in-out infinite;
	}

	/**
	 * Staggered animation
	 *
	 * WHY delays:
	 * - Wave effect: Dots pulse in sequence
	 * - Visual interest: More engaging than simultaneous pulse
	 */
	.dot:nth-child(2) {
		animation-delay: 0.2s;
	}

	.dot:nth-child(3) {
		animation-delay: 0.4s;
	}

	/**
	 * Pulse animation
	 *
	 * WHY scale + opacity:
	 * - Subtle: Not distracting
	 * - Smooth: Ease-in-out transition
	 */
	@keyframes pulse {
		0%,
		100% {
			opacity: 0.4;
			transform: scale(1);
		}
		50% {
			opacity: 1;
			transform: scale(1.2);
		}
	}
</style>
