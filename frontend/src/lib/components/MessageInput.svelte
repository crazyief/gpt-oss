<script lang="ts">
/**
 * MessageInput - Auto-resize textarea with send button
 * Features: Auto-resize (up to 5 lines), Enter to send, Shift+Enter for newline
 * Disabled during streaming, character count display
 *
 * BUG-008/009 FIX: Reset state and focus when conversation changes
 * - conversationId prop tracks current conversation
 * - Reactive statement clears message and focuses when ID changes
 */
import { createEventDispatcher, tick, onMount } from 'svelte';
import { APP_CONFIG } from '$lib/config';

// Props
export let disabled: boolean = false; // Disable during streaming
export let placeholder: string = 'Type your message...';
export let conversationId: number | null = null; // Track conversation for state reset

// Event dispatcher
const dispatch = createEventDispatcher<{
	send: { message: string };
}>();

// Component state
let message = '';
let textareaElement: HTMLTextAreaElement;
let previousDisabledState = false;
let previousConversationId: number | null = null; // Track for change detection
let isMounted = false; // Prevent reset on initial mount

/**
 * Auto-focus input on mount
 *
 * WHY auto-focus on mount:
 * - UX: User can immediately start typing without clicking
 * - Expectation: Chat input should be ready to use
 * - Common pattern: Slack, Discord, Telegram auto-focus input
 */
onMount(() => {
	textareaElement?.focus();
	isMounted = true;
	previousConversationId = conversationId;
});

/**
 * Reset input state when conversation changes (BUG-008/009 FIX)
 *
 * WHY this reactive statement:
 * - BUG-008: Typing not showing after New Chat - focus was lost
 * - BUG-009: Old text persists after New Chat - message not cleared
 *
 * Flow:
 * 1. User clicks "New Chat"
 * 2. NewChatButton creates conversation and sets currentConversationId
 * 3. ChatInterface re-renders with new conversationId
 * 4. This reactive statement detects ID change
 * 5. Clear message and focus textarea
 *
 * WHY check isMounted:
 * - Prevent reset on initial render (no previous conversation to compare)
 * - Only reset when actively switching conversations
 *
 * WHY use tick():
 * - DOM must update before focusing (Svelte batches updates)
 * - Without tick, focus may happen before textarea is ready
 */
$: if (isMounted && conversationId !== previousConversationId) {
	// Conversation changed - reset input state
	message = '';

	// Reset textarea height
	if (textareaElement) {
		textareaElement.style.height = 'auto';
	}

	// Focus textarea after DOM update
	tick().then(() => {
		if (textareaElement && !disabled) {
			textareaElement.focus();
		}
	});

	// Update tracking variable
	previousConversationId = conversationId;
}

/**
 * Auto-focus input when it becomes enabled after streaming
 *
 * WHY watch disabled state:
 * - BUG-007 FIX: Input shows STOP cursor after sending message
 * - Root cause: disabled=true during streaming, focus happens before re-enabled
 * - Solution: Focus AFTER input becomes enabled (disabled: true → false)
 *
 * Flow:
 * 1. User sends message → disabled becomes true
 * 2. Streaming completes → disabled becomes false
 * 3. Reactive statement detects change → focus input
 *
 * WHY single reactive block:
 * - Ensures proper sequencing: check BEFORE updating previousDisabledState
 * - Prevents race condition from separate reactive statements
 */
$: {
	// Detect state transition from disabled (true) to enabled (false)
	if (previousDisabledState === true && disabled === false && textareaElement) {
		// Wait for DOM update, then focus
		tick().then(() => {
			textareaElement?.focus();

			// Extra safety: fallback focus after delay
			setTimeout(() => {
				if (document.activeElement !== textareaElement) {
					textareaElement?.focus();
				}
			}, 100); // Increased from 50ms to 100ms for more reliable focusing
		});
	}

	// Update tracking variable AFTER checking (must be last in this block)
	previousDisabledState = disabled;
}

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
 * 5. Refocus input after DOM update (async)
 *
 * WHY trim message:
 * - Remove whitespace: "   " is not a valid message
 * - Clean input: No leading/trailing spaces
 *
 * WHY async + tick() before focus:
 * - DOM updates: Svelte batches reactive updates (message = '')
 * - Timing: Focus must happen AFTER textarea value is cleared in DOM
 * - Bug fix: Without tick(), focus happens too early and gets lost
 * - UX: User can immediately continue typing without clicking
 */
async function handleSend() {
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

	// NOTE: Focus handling moved to reactive statement (lines 68-80)
	// Focus happens AFTER disabled changes from true → false
	// This fixes BUG-007: Input auto-focus after streaming completes
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
	<!-- Input row: Textarea + Send button (side by side) -->
	<div class="input-row">
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

	<!-- Character count (show when approaching limit) -->
	{#if message.length > APP_CONFIG.chat.maxMessageLength * 0.7}
		<div class="char-count" style="color: {getCharCountColor()}">
			{message.length}/{APP_CONFIG.chat.maxMessageLength}
		</div>
	{/if}
</div>

<style>
	/**
	 * Message input container - Transparent to match chat background
	 *
	 * Blends with chat background instead of white container
	 */
	.message-input-container {
		padding: 1.25rem 1.5rem;
		border-top: 1px solid rgba(226, 232, 240, 0.2);
		background: transparent;
		backdrop-filter: blur(10px);
		box-shadow: none;
	}

	/**
	 * Input row (textarea + send button side by side)
	 *
	 * WHY flexbox layout:
	 * - Side-by-side: Textarea on left, send button on right
	 * - Responsive: Textarea grows, button stays fixed width
	 * - Alignment: Both elements vertically aligned at bottom
	 */
	.input-row {
		display: flex;
		align-items: flex-end;
		gap: 0.5rem;
	}

	/**
	 * Message textarea - Modern elevated design with glow
	 */
	.message-textarea {
		flex: 1;
		min-height: 48px;
		padding: 0.875rem 1rem;
		border: 2px solid #e2e8f0;
		border-radius: 0.75rem;
		font-size: 0.9375rem;
		line-height: 1.6;
		font-family: inherit;
		resize: none;
		transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
		overflow-y: auto;
		background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.8);
		color: #1f2937; /* Explicit dark text color for visibility on white background */
	}

	/* Placeholder text styling */
	.message-textarea::placeholder {
		color: #9ca3af; /* Gray placeholder for visibility */
	}

	/**
	 * Textarea focus state - Vibrant glow effect
	 */
	.message-textarea:focus {
		outline: none;
		border-color: #6366f1;
		background: #ffffff;
		color: #1f2937; /* Ensure dark text on focus too */
		box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15), 0 4px 12px rgba(99, 102, 241, 0.2), inset 0 1px 0 rgba(255, 255, 255, 1);
		transform: translateY(-1px);
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
	 * Character count
	 *
	 * WHY show only when near limit:
	 * - Clean UI: Don't clutter interface
	 * - Warning: User notices when approaching limit
	 * - Progressive disclosure: Appears when needed
	 *
	 * WHY below input row:
	 * - Clean layout: Doesn't interfere with typing
	 * - Always visible: Not hidden by send button
	 */
	.char-count {
		margin-top: 0.5rem;
		font-size: 0.75rem;
		font-weight: 500;
		text-align: right;
	}

	/**
	 * Send button - Vibrant gradient with satisfying hover effect
	 */
	.send-button {
		flex-shrink: 0;
		padding: 0.875rem;
		min-width: 48px;
		min-height: 48px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #6366f1 0%, #4f46e5 50%, #4338ca 100%);
		color: white;
		border: none;
		border-radius: 0.75rem;
		cursor: pointer;
		transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
		box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4), 0 2px 6px rgba(79, 70, 229, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
		position: relative;
		overflow: hidden;
	}

	/* Shimmer effect on hover */
	.send-button::before {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%);
		transition: left 0.5s ease;
	}

	.send-button:hover:not(:disabled)::before {
		left: 100%;
	}

	.send-button:hover:not(:disabled) {
		background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 50%, #5b21b6 100%);
		transform: translateY(-2px) scale(1.02);
		box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5), 0 4px 12px rgba(79, 70, 229, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.3);
	}

	.send-button:active:not(:disabled) {
		transform: translateY(0) scale(0.98);
		box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
	}

	.send-button svg {
		position: relative;
		z-index: 1;
		transition: transform 0.25s ease;
	}

	.send-button:hover:not(:disabled) svg {
		transform: translateX(2px);
	}

	/**
	 * Send button disabled state
	 */
	.send-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}
</style>
