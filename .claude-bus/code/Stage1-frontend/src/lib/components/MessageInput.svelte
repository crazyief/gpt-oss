<script lang="ts">
/**
 * MessageInput component
 *
 * Purpose: Input textarea for composing messages with auto-resize
 *
 * Features:
 * - Auto-resize textarea (grows up to 5 lines)
 * - Send button with loading state
 * - Enter to send, Shift+Enter for new line
 * - Character count (max 10,000 chars)
 * - Disabled during streaming
 *
 * Design decisions:
 * - Textarea instead of input (multi-line support)
 * - Auto-resize for better UX (see more context)
 * - Max height to prevent screen domination
 * - Send button always visible (not just on hover)
 *
 * WHY auto-resize textarea:
 * - Context: User can see full message while typing
 * - Better than fixed height: Adapts to content length
 * - UX pattern: Slack, Discord, WhatsApp use this
 */

import { createEventDispatcher } from 'svelte';
import { APP_CONFIG } from '$lib/config';

// Props
export let disabled: boolean = false; // Disable during streaming
export let placeholder: string = 'Type your message...';

// Event dispatcher
const dispatch = createEventDispatcher<{
	send: { message: string };
}>();

// Component state
let message = '';
let textareaElement: HTMLTextAreaElement;

/**
 * Auto-resize textarea as content changes
 *
 * WHY reset height before measuring:
 * - Correct measurement: Height auto doesn't shrink without reset
 * - Prevents growth-only: Can shrink when user deletes lines
 *
 * WHY use scrollHeight:
 * - Actual content height: Includes all text, not just visible area
 * - Browser calculates: No need to count lines manually
 */
function autoResize() {
	if (!textareaElement) return;

	// Reset height to auto to get accurate scrollHeight
	textareaElement.style.height = 'auto';

	// Set height to scrollHeight (content height)
	textareaElement.style.height = `${textareaElement.scrollHeight}px`;
}

/**
 * Handle textarea input
 *
 * WHY call autoResize on every input:
 * - Immediate feedback: Textarea grows as user types
 * - Smooth animation: CSS transition handles resize
 */
function handleInput() {
	autoResize();
}

/**
 * Handle Enter key press
 *
 * WHY Shift+Enter for new line:
 * - Common pattern: Slack, Discord, Telegram use this
 * - User expectation: Enter = send, Shift+Enter = new line
 * - Accessibility: Keyboard-only users can send easily
 *
 * @param event - Keyboard event
 */
function handleKeydown(event: KeyboardEvent) {
	if (event.key === 'Enter' && !event.shiftKey) {
		event.preventDefault(); // Prevent default Enter behavior (new line)
		handleSend();
	}
}

/**
 * Send message
 *
 * Flow:
 * 1. Validate message (not empty, under max length)
 * 2. Dispatch send event
 * 3. Clear textarea
 * 4. Reset textarea height
 *
 * WHY trim message:
 * - Remove whitespace: "   " is not a valid message
 * - Clean input: No leading/trailing spaces
 */
function handleSend() {
	const trimmedMessage = message.trim();

	// Validate message
	if (!trimmedMessage) return;
	if (trimmedMessage.length > APP_CONFIG.chat.maxMessageLength) return;

	// Dispatch send event to parent
	dispatch('send', { message: trimmedMessage });

	// Clear input
	message = '';

	// Reset textarea height
	if (textareaElement) {
		textareaElement.style.height = 'auto';
	}

	// Focus textarea for next message
	textareaElement?.focus();
}

/**
 * Calculate character count color
 *
 * WHY different colors for different thresholds:
 * - Green: Under 80% (safe)
 * - Yellow: 80-95% (warning)
 * - Red: Over 95% (danger, near limit)
 */
function getCharCountColor(): string {
	const ratio = message.length / APP_CONFIG.chat.maxMessageLength;
	if (ratio < 0.8) return '#6b7280'; // Gray
	if (ratio < 0.95) return '#f59e0b'; // Yellow
	return '#ef4444'; // Red
}
</script>

<div class="message-input-container">
	<!-- Textarea -->
	<textarea
		bind:this={textareaElement}
		bind:value={message}
		on:input={handleInput}
		on:keydown={handleKeydown}
		{placeholder}
		{disabled}
		class="message-textarea"
		style="max-height: {APP_CONFIG.chat.inputMaxHeight};"
		aria-label="Message input"
		rows="1"
	></textarea>

	<!-- Send button + character count -->
	<div class="input-footer">
		<!-- Character count (show when approaching limit) -->
		{#if message.length > APP_CONFIG.chat.maxMessageLength * 0.7}
			<div class="char-count" style="color: {getCharCountColor()}">
				{message.length}/{APP_CONFIG.chat.maxMessageLength}
			</div>
		{/if}

		<!-- Send button -->
		<button
			type="button"
			on:click={handleSend}
			disabled={disabled || !message.trim()}
			class="send-button"
			aria-label="Send message"
		>
			<svg
				width="20"
				height="20"
				viewBox="0 0 20 20"
				fill="none"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M18 2L9 11M18 2l-6 16-3-7-7-3 16-6z"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				/>
			</svg>
		</button>
	</div>
</div>

<style>
	/**
	 * Message input container
	 *
	 * Layout: Textarea + footer (char count + send button)
	 * WHY fixed at bottom:
	 * - Always accessible: User can always send message
	 * - Common pattern: Chat apps fix input at bottom
	 */
	.message-input-container {
		padding: 1rem;
		border-top: 1px solid #e5e7eb; /* Gray 200 */
		background-color: #ffffff;
	}

	/**
	 * Message textarea
	 *
	 * WHY min-height + max-height:
	 * - Min: Comfortable typing area (not cramped)
	 * - Max: Prevents dominating screen (5 lines ≈ 120px)
	 * - Auto-resize: Grows between min and max
	 *
	 * WHY resize: none:
	 * - Auto-resize: Component handles sizing
	 * - Prevents manual resize: User can't break layout
	 */
	.message-textarea {
		width: 100%;
		min-height: 44px; /* Single line + padding */
		padding: 0.75rem;
		border: 1px solid #e5e7eb; /* Gray 200 */
		border-radius: 0.5rem;
		font-size: 0.9375rem;
		line-height: 1.5;
		font-family: inherit; /* Use app font, not monospace */
		resize: none; /* Disable manual resize */
		transition: all 0.2s ease;
		overflow-y: auto; /* Scroll if exceeds max-height */
	}

	/**
	 * Textarea focus state
	 */
	.message-textarea:focus {
		outline: none;
		border-color: #3b82f6; /* Blue 500 */
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	/**
	 * Textarea disabled state
	 */
	.message-textarea:disabled {
		background-color: #f9fafb; /* Gray 50 */
		color: #9ca3af; /* Gray 400 */
		cursor: not-allowed;
	}

	/**
	 * Input footer (char count + send button)
	 */
	.input-footer {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-top: 0.5rem;
	}

	/**
	 * Character count
	 *
	 * WHY show only when near limit:
	 * - Clean UI: Don't clutter interface
	 * - Warning: User notices when approaching limit
	 * - Progressive disclosure: Appears when needed
	 */
	.char-count {
		font-size: 0.75rem;
		font-weight: 500;
	}

	/**
	 * Send button
	 *
	 * WHY prominent styling:
	 * - Primary action: Most common user action
	 * - Visual hierarchy: Blue stands out
	 * - Accessibility: Large touch target
	 */
	.send-button {
		padding: 0.75rem;
		background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); /* Blue gradient */
		color: white;
		border: none;
		border-radius: 0.5rem;
		cursor: pointer;
		transition: all 0.2s ease;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.send-button:hover:not(:disabled) {
		background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
		transform: translateY(-1px);
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
	}

	.send-button:active:not(:disabled) {
		transform: translateY(0);
	}

	/**
	 * Send button disabled state
	 */
	.send-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}
</style>
