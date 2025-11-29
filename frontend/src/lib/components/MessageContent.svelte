<script lang="ts">
/**
 * MessageContent component
 *
 * Purpose: Render markdown content with syntax highlighting
 *
 * Features:
 * - Markdown rendering with DOMPurify sanitization
 * - Syntax highlighting for code blocks (via Prism.js)
 * - Responsive typography
 *
 * Design decisions:
 * - Reactive rendering: Re-render when content changes (streaming)
 * - afterUpdate hook: Highlight code after {@html} renders
 * - Global styles: Markdown typography needs scoped styles
 */

import { afterUpdate } from 'svelte';
import { renderMarkdown, highlightCode } from '$lib/utils/markdown';
import { logger } from '$lib/utils/logger';

// Props
export let content: string;
export let isStreaming: boolean = false;

// Component state
let contentElement: HTMLElement;
let renderedContent: string = '';

/**
 * Render markdown when content changes
 *
 * WHY reactive statement:
 * - Re-render: Content changes during streaming
 * - Streaming: Tokens append to content, need re-render
 *
 * BUG-003 FIX: Pre-process short numeric responses
 * - Problem: " 4." gets parsed as empty ordered list <ol><li></li></ol>
 * - Solution: Detect short numeric pattern and wrap in inline code
 * - Pattern: optional whitespace + 1-3 digits + period + optional whitespace + end
 * - Example: " 4." → "`4.`" (renders as inline code, not empty list)
 * - Preserves legitimate lists: "1. First item\n2. Second item" passes through unchanged
 *
 * INLINE CODE ENHANCEMENT: Convert single-line code blocks to inline code
 * - Problem: LLM sometimes uses code blocks for single-line code despite system prompt
 * - Solution: Auto-convert single-line code blocks (```) to inline code (`)
 * - Example: "```python\nprint("hello")\n```" → "`print("hello")`"
 * - Preserves multi-line code blocks unchanged
 */
$: {
	if (content) {
		let processedContent = content;

		// Detect short numeric responses that markdown misinterprets as lists
		// Pattern: /^\s*\d+\.\s*$/
		// Matches: " 4.", "  99.  ", "1.", "1000.", but NOT "1. Item" or "The answer is 4."
		// Note: Markdown interprets ANY "number." at start as ordered list, so match all digits
		const shortNumericPattern = /^\s*\d+\.\s*$/;

		if (shortNumericPattern.test(content)) {
			// Wrap in inline code to prevent list parsing
			// " 4." → "`4.`" → renders as inline code element
			processedContent = '`' + content.trim() + '`';
		}

		// Convert single-line code blocks to inline code
		// Pattern: ```language\ncode\n``` or ```\ncode\n``` or ```code```
		// Match code blocks with optional language, single line of code, no additional newlines
		processedContent = processedContent.replace(
			/```(?:\w+)?\n?([^\n`]+)\n?```/g,
			(match, code) => {
				// Only convert if it's truly a single line (no newlines in the code itself)
				if (code && !code.includes('\n')) {
					return '`' + code.trim() + '`';
				}
				// Keep multi-line code blocks as-is
				return match;
			}
		);

		renderedContent = renderMarkdown(processedContent);
	}
}

/**
 * Highlight code blocks after content renders
 *
 * WHY afterUpdate instead of onMount:
 * - DOM timing: Need to wait for {@html} to render
 * - Streaming: Re-highlight as new code blocks appear
 */
afterUpdate(() => {
	if (contentElement) {
		highlightCode(contentElement);
		addCopyButtonsToInlineCode();
	}
});

/**
 * Add copy buttons to inline code elements
 *
 * WHY: User requested inline code (like "21 times 2 is 42.") to have copy buttons
 * - Click inline code to copy
 * - Visual feedback on copy
 */
function addCopyButtonsToInlineCode() {
	if (!contentElement) return;

	// Find all inline code elements (NOT inside <pre>)
	const inlineCodes = contentElement.querySelectorAll('code:not(pre code)');

	inlineCodes.forEach((codeEl) => {
		// Skip if already has click handler
		if (codeEl.classList.contains('copyable')) return;

		codeEl.classList.add('copyable');

		// Add click handler to copy
		codeEl.addEventListener('click', async () => {
			const textToCopy = codeEl.textContent || '';

			try {
				await navigator.clipboard.writeText(textToCopy);

				// Visual feedback: briefly change background
				const originalBg = codeEl.style.backgroundColor;
				codeEl.style.backgroundColor = '#10b981'; // Green
				codeEl.title = 'Copied!';

				setTimeout(() => {
					codeEl.style.backgroundColor = originalBg;
					codeEl.title = 'Click to copy';
				}, 1000);
			} catch (err) {
				logger.error('Failed to copy inline code:', { error: err });
			}
		});

		// Add hover hint
		codeEl.title = 'Click to copy';
		codeEl.style.cursor = 'pointer';
	});
}
</script>

<div class="message-content" bind:this={contentElement}>
	{@html renderedContent}
</div>

<style>
	/**
	 * Message content (markdown)
	 *
	 * WHY global styles in component:
	 * - Scoped markdown: Only affects this component's rendered markdown
	 * - Typography: Headings, lists, tables need styling
	 */
	.message-content {
		font-size: 0.9375rem;
		line-height: 1.6;
	}

	/* Markdown typography styles */
	.message-content :global(h1),
	.message-content :global(h2),
	.message-content :global(h3),
	.message-content :global(h4),
	.message-content :global(h5),
	.message-content :global(h6) {
		margin: 1rem 0 0.5rem 0;
		font-weight: 600;
		line-height: 1.3;
	}

	.message-content :global(h1) {
		font-size: 1.5rem;
	}
	.message-content :global(h2) {
		font-size: 1.25rem;
	}
	.message-content :global(h3) {
		font-size: 1.125rem;
	}

	.message-content :global(p) {
		margin: 0.75rem 0;
	}

	.message-content :global(ul),
	.message-content :global(ol) {
		margin: 0.75rem 0;
		padding-left: 1.5rem;
	}

	.message-content :global(li) {
		margin: 0.25rem 0;
	}

	.message-content :global(code) {
		padding: 0.25rem 0.5rem;
		background-color: #1f2937; /* Dark gray (almost black) - 黑底 */
		color: #f9fafb; /* White text - 白字 */
		border-radius: 0.375rem;
		font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
		font-size: 0.875em;
		transition: all 0.2s ease;
		/* Click to copy hint */
		cursor: pointer;
		user-select: none; /* Prevent text selection, click to copy instead */
	}

	.message-content :global(code:hover) {
		background-color: #374151; /* Lighter dark gray on hover */
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
	}

	.message-content :global(pre code) {
		padding: 0;
		background: none;
		color: inherit; /* Let Prism.js handle code block colors */
		cursor: default;
		user-select: text; /* Allow selection in code blocks */
	}

	.message-content :global(blockquote) {
		margin: 0.75rem 0;
		padding-left: 1rem;
		border-left: 3px solid #d1d5db; /* Gray 300 */
		color: #6b7280; /* Gray 500 */
		font-style: italic;
	}

	.message-content :global(table) {
		width: 100%;
		margin: 0.75rem 0;
		border-collapse: collapse;
	}

	.message-content :global(th),
	.message-content :global(td) {
		padding: 0.5rem;
		border: 1px solid #e5e7eb; /* Gray 200 */
		text-align: left;
	}

	.message-content :global(th) {
		background-color: #f3f4f6; /* Gray 100 */
		font-weight: 600;
	}
</style>
