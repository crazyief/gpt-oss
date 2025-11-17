<script lang="ts">
/**
 * CodeBlock component
 *
 * Purpose: Display code blocks with syntax highlighting and copy functionality
 *
 * Features:
 * - Syntax highlighting via Prism.js
 * - Language badge (shows "Python", "JavaScript", etc.)
 * - Copy button with feedback (icon changes to checkmark)
 * - Line numbers (optional)
 * - Scrollable for long code
 *
 * Design decisions:
 * - Header with language + copy button
 * - Dark theme (common for code blocks)
 * - Hover reveals copy button (clean UI)
 * - Temporary success feedback (2 seconds)
 *
 * WHY separate CodeBlock component:
 * - Reusability: Can use outside chat (code examples, docs)
 * - Encapsulation: Copy logic, styling in one place
 * - Customization: Easy to add features (download, expand, etc.)
 */

import { onMount } from 'svelte';
import { copyCodeToClipboard, getCodeBlockLanguage } from '$lib/utils/markdown';

// Props
export let code: string; // Raw code content
export let language: string = 'text'; // Programming language
export let showLineNumbers: boolean = false; // Optional line numbers

// Component state
let codeElement: HTMLElement;
let copySuccess = false; // Show checkmark after copy

/**
 * Copy code to clipboard
 *
 * Flow:
 * 1. Call clipboard API utility
 * 2. Show success feedback (checkmark icon)
 * 3. Reset after 2 seconds
 *
 * WHY 2 second feedback timeout:
 * - Long enough: User sees confirmation
 * - Short enough: Doesn't clutter UI
 * - Industry standard: GitHub, VSCode use similar timing
 */
async function handleCopy() {
	const success = await copyCodeToClipboard(codeElement);

	if (success) {
		copySuccess = true;

		// Reset after 2 seconds
		setTimeout(() => {
			copySuccess = false;
		}, 2000);
	}
}

/**
 * Format language name for display
 *
 * Examples:
 * - "python" → "Python"
 * - "javascript" → "JavaScript"
 * - "typescript" → "TypeScript"
 *
 * WHY capitalize:
 * - Readability: "Python" is more readable than "python"
 * - Professional: Matches official language names
 */
function formatLanguageName(lang: string): string {
	if (!lang || lang === 'text') return 'Text';

	// Special cases (common capitalizations)
	const specialCases: Record<string, string> = {
		javascript: 'JavaScript',
		typescript: 'TypeScript',
		csharp: 'C#',
		cplusplus: 'C++',
		objectivec: 'Objective-C'
	};

	if (specialCases[lang.toLowerCase()]) {
		return specialCases[lang.toLowerCase()];
	}

	// Default: Capitalize first letter
	return lang.charAt(0).toUpperCase() + lang.slice(1);
}
</script>

<div class="code-block">
	<!-- Header: Language badge + Copy button -->
	<div class="code-header">
		<!-- Language badge -->
		<span class="language-badge">
			{formatLanguageName(language)}
		</span>

		<!-- Copy button (hover to reveal) -->
		<button
			type="button"
			on:click={handleCopy}
			class="copy-button"
			aria-label="Copy code"
		>
			{#if copySuccess}
				<!-- Checkmark icon (success state) -->
				<svg
					width="16"
					height="16"
					viewBox="0 0 16 16"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M13 4L6 11L3 8"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
				</svg>
				<span>Copied!</span>
			{:else}
				<!-- Copy icon (default state) -->
				<svg
					width="16"
					height="16"
					viewBox="0 0 16 16"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<rect
						x="5"
						y="5"
						width="9"
						height="9"
						rx="1"
						stroke="currentColor"
						stroke-width="1.5"
					/>
					<path
						d="M3 11V3a1 1 0 0 1 1-1h8"
						stroke="currentColor"
						stroke-width="1.5"
						stroke-linecap="round"
					/>
				</svg>
				<span>Copy</span>
			{/if}
		</button>
	</div>

	<!-- Code content -->
	<pre class="code-content" class:line-numbers={showLineNumbers}><code
			bind:this={codeElement}
			class="language-{language}"
		>{code}</code
		></pre>
</div>

<style>
	/**
	 * Code block container
	 *
	 * WHY dark background:
	 * - Contrast: Light text on dark = easier to read code
	 * - Common pattern: GitHub, VSCode, Prism themes use dark
	 * - Differentiation: Stands out from regular message text
	 */
	.code-block {
		margin: 0.75rem 0;
		border-radius: 0.5rem;
		overflow: hidden;
		background-color: #1e1e1e; /* Dark gray (VSCode theme) */
		border: 1px solid #333333;
	}

	/**
	 * Code header (language + copy button)
	 *
	 * WHY sticky header:
	 * - Long code: Header visible when scrolling
	 * - Always accessible: Copy button available without scrolling up
	 */
	.code-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.5rem 0.75rem;
		background-color: #2d2d2d; /* Slightly lighter than background */
		border-bottom: 1px solid #333333;
	}

	/**
	 * Language badge styling
	 *
	 * WHY show language explicitly:
	 * - Context: User knows what language they're reading
	 * - Copying: User can include language in pasted code (```python)
	 */
	.language-badge {
		font-size: 0.75rem;
		font-weight: 500;
		color: #9ca3af; /* Gray 400 */
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	/**
	 * Copy button styling
	 *
	 * WHY hover reveal:
	 * - Clean: Button doesn't clutter header until needed
	 * - Progressive disclosure: User discovers feature on hover
	 */
	.copy-button {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.375rem 0.75rem;
		background-color: #3b3b3b;
		color: #9ca3af;
		border: 1px solid #4b4b4b;
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
		opacity: 0.7;
	}

	.copy-button:hover {
		background-color: #4b4b4b;
		color: #ffffff;
		opacity: 1;
	}

	/**
	 * Success state (after successful copy)
	 *
	 * WHY green color:
	 * - Feedback: User knows copy succeeded
	 * - Universal: Green = success (traffic lights, etc.)
	 */
	.copy-button:has(svg path[d*='L6 11L3 8']) {
		color: #10b981; /* Green 500 */
		border-color: #10b981;
	}

	/**
	 * Code content styling
	 *
	 * WHY specific overflow settings:
	 * - overflow-x: auto = horizontal scroll for long lines
	 * - overflow-y: hidden = no vertical scroll (entire block scrolls in message list)
	 *
	 * WHY max-height:
	 * - Prevents extremely long code from dominating screen
	 * - User can expand if needed (future enhancement)
	 */
	.code-content {
		margin: 0;
		padding: 1rem;
		overflow-x: auto;
		overflow-y: hidden;
		max-height: 500px;
		background-color: #1e1e1e;
		color: #d4d4d4; /* Light gray text */
		font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
		font-size: 0.875rem;
		line-height: 1.5;
	}

	/**
	 * Code element styling
	 *
	 * WHY display: block:
	 * - Full width: Code takes entire horizontal space
	 * - Prevents inline gaps: No whitespace issues
	 */
	.code-content code {
		display: block;
		padding: 0;
		background: none;
		color: inherit;
		font-size: inherit;
		font-family: inherit;
	}

	/**
	 * Line numbers styling (optional feature)
	 *
	 * WHY counter-based line numbers instead of hardcoded:
	 * - Automatic: CSS counts lines, no manual numbering
	 * - Copy-friendly: Line numbers aren't selected when copying code
	 * - Accurate: Always matches actual line count
	 */
	.code-content.line-numbers {
		counter-reset: line;
	}

	.code-content.line-numbers code {
		counter-increment: line;
	}

	.code-content.line-numbers code::before {
		content: counter(line);
		display: inline-block;
		width: 2rem;
		margin-right: 1rem;
		text-align: right;
		color: #6b7280; /* Gray 500 */
		user-select: none; /* Prevent selection when copying */
	}

	/**
	 * Scrollbar styling (WebKit browsers)
	 *
	 * WHY custom scrollbar:
	 * - Theme consistency: Matches dark code block
	 * - Visibility: Dark scrollbar on dark background needs contrast
	 */
	.code-content::-webkit-scrollbar {
		height: 8px;
	}

	.code-content::-webkit-scrollbar-track {
		background: #2d2d2d;
	}

	.code-content::-webkit-scrollbar-thumb {
		background: #4b4b4b;
		border-radius: 4px;
	}

	.code-content::-webkit-scrollbar-thumb:hover {
		background: #5b5b5b;
	}
</style>
