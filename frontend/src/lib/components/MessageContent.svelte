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
 */
$: {
	if (content) {
		let processedContent = content;

		// Detect short numeric responses that markdown misinterprets as lists
		// Pattern: /^\s*\d{1,3}\.\s*$/
		// Matches: " 4.", "  99.  ", "1.", but NOT "1. Item" or "The answer is 4."
		const shortNumericPattern = /^\s*\d{1,3}\.\s*$/;

		if (shortNumericPattern.test(content)) {
			// Wrap in inline code to prevent list parsing
			// " 4." → "`4.`" → renders as inline code element
			processedContent = '`' + content.trim() + '`';
		}

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
	}
});
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
		padding: 0.125rem 0.375rem;
		background-color: #e5e7eb; /* Gray 200 */
		border-radius: 0.25rem;
		font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
		font-size: 0.875em;
	}

	.message-content :global(pre code) {
		padding: 0;
		background: none;
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
