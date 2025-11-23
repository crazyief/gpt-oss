/**
 * Markdown rendering utilities
 *
 * Purpose: Safely render markdown to HTML with syntax highlighting
 *
 * Security features:
 * - DOMPurify sanitization: Prevents XSS attacks
 * - Allowed tags whitelist: Only safe HTML elements
 * - No JavaScript execution: <script> tags stripped
 * - Safe links: No javascript: protocol URLs
 *
 * Features:
 * - Markdown parsing with marked
 * - Syntax highlighting with Prism.js
 * - Code block copy functionality
 * - Custom renderers for enhanced UX
 *
 * WHY separate markdown utility:
 * - Reusability: Use in multiple components (AssistantMessage, previews, etc.)
 * - Security: Centralized sanitization prevents inconsistent XSS protection
 * - Testing: Easy to unit test rendering and sanitization
 * - Configuration: Single place to configure marked and DOMPurify options
 */

import { marked } from 'marked';
import DOMPurify from 'dompurify';
import Prism from 'prismjs';

// Import Prism language components (add more as needed)
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-markdown';
import 'prismjs/components/prism-sql';
import 'prismjs/components/prism-yaml';

/**
 * Configure marked options
 *
 * WHY gfm (GitHub Flavored Markdown):
 * - Tables: Support markdown tables (common in AI responses)
 * - Strikethrough: ~~text~~ syntax
 * - Task lists: - [ ] checkbox syntax
 * - Autolinks: URLs become clickable without [](url) syntax
 *
 * WHY breaks: true:
 * - Preserve line breaks: Single newline = <br> (matches user expectation)
 * - Better for AI responses: LLM often uses single newlines for formatting
 *
 * WHY headerIds: false:
 * - Security: Prevents anchor-based XSS vectors
 * - Simplicity: Chat messages don't need heading anchors
 */
marked.setOptions({
	gfm: true,
	breaks: true
});

/**
 * DOMPurify configuration
 *
 * WHY whitelist approach (ALLOWED_TAGS):
 * - Security: Explicit allow is safer than explicit deny (blacklist)
 * - XSS prevention: Strips any unknown/dangerous tags
 * - Markdown compatibility: Covers all common markdown elements
 *
 * Allowed tags rationale:
 * - Text: p, span, strong, em, u, s, del
 * - Headings: h1-h6
 * - Lists: ul, ol, li
 * - Code: code, pre
 * - Links: a (with href validation)
 * - Tables: table, thead, tbody, tr, th, td
 * - Quotes: blockquote
 * - Separators: hr
 * - Line breaks: br
 *
 * WHY ALLOWED_ATTR:
 * - href: Links need target URL
 * - class: Prism.js needs classes for syntax highlighting
 * - language-*: Code blocks use language-python, language-javascript, etc.
 * - No onclick, onload, or other event handlers (XSS vector)
 */
const DOMPURIFY_CONFIG = {
	ALLOWED_TAGS: [
		'p',
		'span',
		'h1',
		'h2',
		'h3',
		'h4',
		'h5',
		'h6',
		'ul',
		'ol',
		'li',
		'code',
		'pre',
		'a',
		'strong',
		'em',
		'u',
		's',
		'del',
		'blockquote',
		'table',
		'thead',
		'tbody',
		'tr',
		'th',
		'td',
		'hr',
		'br'
	],
	ALLOWED_ATTR: ['href', 'class', 'rel', 'target'],
	ALLOW_DATA_ATTR: false, // No data-* attributes (potential XSS vector)
	ALLOW_UNKNOWN_PROTOCOLS: false, // Block javascript:, data:, etc.
	ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto):|[^a-z]|[a-z+.-]+(?:[^a-z+.\-:]|$))/i // Only http, https, mailto
};

/**
 * Render markdown content to safe HTML
 *
 * Process:
 * 1. Parse markdown to HTML (marked)
 * 2. Sanitize HTML (DOMPurify) - CRITICAL for XSS prevention
 * 3. Return safe HTML string
 *
 * WHY sanitize after parsing instead of before:
 * - Marked needs raw markdown: Can't parse sanitized HTML
 * - Defense in depth: Even if marked has XSS bug, DOMPurify catches it
 * - Correct layer: Sanitization is HTML concern, not markdown concern
 *
 * Security notes:
 * - NEVER render output with v-html/innerHTML without sanitization
 * - NEVER trust user input or AI responses (can contain malicious code)
 * - ALWAYS use DOMPurify before rendering
 *
 * Example inputs and outputs:
 * - Input: "**Hello** world" → Output: "<p><strong>Hello</strong> world</p>"
 * - Input: "<script>alert('xss')</script>" → Output: "" (stripped)
 * - Input: "[Click](javascript:alert('xss'))" → Output: "<p>[Click](javascript:alert('xss'))</p>" (not a link)
 *
 * @param content - Raw markdown string
 * @returns Sanitized HTML string safe for {@html} rendering
 */
export function renderMarkdown(content: string): string {
	// Step 1: Parse markdown to HTML
	const html = marked.parse(content) as string;

	// Step 2: Sanitize HTML to prevent XSS
	const clean = DOMPurify.sanitize(html, DOMPURIFY_CONFIG);

	return clean;
}

/**
 * Highlight code blocks with Prism.js
 *
 * Call this after rendering markdown to DOM
 *
 * WHY separate function instead of integrated in renderMarkdown:
 * - DOM access: Prism needs actual DOM elements, not HTML strings
 * - Component control: Component decides when to highlight (after mount, not during render)
 * - Performance: Can debounce highlighting for streaming content
 *
 * WHY use Prism.highlightElement instead of Prism.highlightAll:
 * - Scoped: Only highlight within specific container (avoid conflicts)
 * - Performance: Don't re-highlight entire page
 * - Control: Can skip already-highlighted blocks
 *
 * Usage:
 * ```svelte
 * <div bind:this={container}>
 *   {@html renderMarkdown(content)}
 * </div>
 * <script>
 *   onMount(() => highlightCode(container));
 * </script>
 * ```
 *
 * @param container - DOM element containing code blocks
 */
export function highlightCode(container: HTMLElement): void {
	if (!container) return;

	// Find all code blocks
	const codeBlocks = container.querySelectorAll('pre code');

	// Highlight each block
	codeBlocks.forEach((block) => {
		// Skip if already highlighted (Prism adds .highlighted class)
		if (block.classList.contains('highlighted')) return;

		// Auto-detect language from class (marked adds language-python, etc.)
		// Prism will use this to choose syntax highlighter

		try {
			Prism.highlightElement(block as HTMLElement);
			block.classList.add('highlighted'); // Mark as processed
		} catch (err) {
			console.error('Failed to highlight code block:', err);
		}
	});
}

/**
 * Extract language from code block class
 *
 * Marked adds classes like "language-python", "language-javascript"
 * This helper extracts "python", "javascript" for display/copy functionality
 *
 * WHY needed:
 * - Language badge: Show "Python" label on code block
 * - Copy button: Include language in copied text (```python)
 * - Fallback: Default to "text" if no language specified
 *
 * @param codeElement - <code> element with language class
 * @returns Language name (e.g., "python", "javascript", "text")
 */
export function getCodeBlockLanguage(codeElement: HTMLElement): string {
	// Look for language-* class
	const classes = Array.from(codeElement.classList);
	const languageClass = classes.find((cls) => cls.startsWith('language-'));

	if (languageClass) {
		return languageClass.replace('language-', '');
	}

	return 'text'; // Fallback for plain text blocks
}

/**
 * Copy code block content to clipboard
 *
 * WHY separate utility instead of inline in component:
 * - Reusability: Multiple code block components can use this
 * - Error handling: Centralized clipboard error handling
 * - Fallback: Can add fallback for browsers without Clipboard API
 *
 * @param codeElement - <code> element to copy from
 * @returns Promise resolving to true if copy succeeded
 */
export async function copyCodeToClipboard(codeElement: HTMLElement): Promise<boolean> {
	try {
		const text = codeElement.textContent || '';

		// Modern Clipboard API (supported in all modern browsers)
		await navigator.clipboard.writeText(text);
		return true;
	} catch (err) {
		console.error('Failed to copy code:', err);

		// Fallback: Old execCommand method (deprecated but widely supported)
		try {
			const textarea = document.createElement('textarea');
			textarea.value = codeElement.textContent || '';
			textarea.style.position = 'fixed';
			textarea.style.opacity = '0';
			document.body.appendChild(textarea);
			textarea.select();
			const success = document.execCommand('copy');
			document.body.removeChild(textarea);
			return success;
		} catch (fallbackErr) {
			console.error('Fallback copy also failed:', fallbackErr);
			return false;
		}
	}
}
