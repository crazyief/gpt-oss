/**
 * Unit tests for markdown rendering utilities
 *
 * Tests markdown parsing, sanitization, and utility functions.
 * Follows AAA pattern (Arrange, Act, Assert) for clarity.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderMarkdown, highlightCode, getCodeBlockLanguage, copyCodeToClipboard } from './markdown';

describe('markdown.ts - renderMarkdown', () => {
	it('converts markdown headings to HTML', () => {
		// Arrange
		const markdown = '# Heading 1\n## Heading 2\n### Heading 3';

		// Act
		const result = renderMarkdown(markdown);

		// Assert
		expect(result).toContain('<h1');
		expect(result).toContain('Heading 1');
		expect(result).toContain('<h2');
		expect(result).toContain('Heading 2');
		expect(result).toContain('<h3');
		expect(result).toContain('Heading 3');
	});

	it('converts markdown bold/italic to HTML', () => {
		// Arrange
		const markdown = '**bold text** and *italic text*';

		// Act
		const result = renderMarkdown(markdown);

		// Assert
		expect(result).toContain('<strong>bold text</strong>');
		expect(result).toContain('<em>italic text</em>');
	});

	it('sanitizes dangerous HTML (script tags removed)', () => {
		// Arrange
		const maliciousMarkdown = '<script>alert("XSS")</script>\n**Safe text**';

		// Act
		const result = renderMarkdown(maliciousMarkdown);

		// Assert
		expect(result).not.toContain('<script>');
		expect(result).not.toContain('alert');
		expect(result).toContain('<strong>Safe text</strong>');
	});

	it('returns empty string for invalid input', () => {
		// Arrange
		const emptyMarkdown = '';

		// Act
		const result = renderMarkdown(emptyMarkdown);

		// Assert
		expect(result).toBe('');
	});
});

describe('markdown.ts - highlightCode', () => {
	beforeEach(() => {
		// Clear DOM before each test
		document.body.innerHTML = '';
	});

	it('highlights code blocks with Prism.js', () => {
		// Arrange
		const container = document.createElement('div');
		container.innerHTML = '<pre><code class="language-python">print("hello")</code></pre>';
		document.body.appendChild(container);

		// Act
		highlightCode(container);

		// Assert
		const codeBlock = container.querySelector('code');
		expect(codeBlock?.classList.contains('highlighted')).toBe(true);
	});

	it('does not re-highlight already-highlighted blocks', () => {
		// Arrange
		const container = document.createElement('div');
		const codeBlock = document.createElement('code');
		codeBlock.className = 'language-javascript highlighted';
		codeBlock.textContent = 'console.log("test")';
		const pre = document.createElement('pre');
		pre.appendChild(codeBlock);
		container.appendChild(pre);
		document.body.appendChild(container);

		const spy = vi.spyOn(codeBlock.classList, 'add');

		// Act
		highlightCode(container);

		// Assert
		// Should not add 'highlighted' class again (already present)
		expect(spy).not.toHaveBeenCalledWith('highlighted');
	});

	it('handles multiple code blocks', () => {
		// Arrange
		const container = document.createElement('div');
		container.innerHTML = `
			<pre><code class="language-python">print("test1")</code></pre>
			<pre><code class="language-javascript">console.log("test2")</code></pre>
		`;
		document.body.appendChild(container);

		// Act
		highlightCode(container);

		// Assert
		const codeBlocks = container.querySelectorAll('code');
		expect(codeBlocks).toHaveLength(2);
		expect(codeBlocks[0].classList.contains('highlighted')).toBe(true);
		expect(codeBlocks[1].classList.contains('highlighted')).toBe(true);
	});

	it('handles empty container gracefully', () => {
		// Arrange
		const container = document.createElement('div');
		document.body.appendChild(container);

		// Act & Assert (should not throw)
		expect(() => highlightCode(container)).not.toThrow();
	});
});

describe('markdown.ts - getCodeBlockLanguage', () => {
	it('extracts language from language-* class', () => {
		// Arrange
		const codeElement = document.createElement('code');
		codeElement.className = 'language-python';

		// Act
		const result = getCodeBlockLanguage(codeElement);

		// Assert
		expect(result).toBe('python');
	});

	it('handles javascript language', () => {
		// Arrange
		const codeElement = document.createElement('code');
		codeElement.className = 'language-javascript';

		// Act
		const result = getCodeBlockLanguage(codeElement);

		// Assert
		expect(result).toBe('javascript');
	});

	it('returns "text" for plain code blocks without language', () => {
		// Arrange
		const codeElement = document.createElement('code');
		codeElement.className = '';

		// Act
		const result = getCodeBlockLanguage(codeElement);

		// Assert
		expect(result).toBe('text');
	});

	it('ignores non-language classes', () => {
		// Arrange
		const codeElement = document.createElement('code');
		codeElement.className = 'highlighted some-other-class';

		// Act
		const result = getCodeBlockLanguage(codeElement);

		// Assert
		expect(result).toBe('text');
	});
});

describe('markdown.ts - copyCodeToClipboard', () => {
	it('copies code content to clipboard', async () => {
		// Arrange
		const codeElement = document.createElement('code');
		codeElement.textContent = 'print("hello world")';

		// Mock clipboard API
		const mockWriteText = vi.fn().mockResolvedValue(undefined);
		Object.assign(navigator, {
			clipboard: {
				writeText: mockWriteText
			}
		});

		// Act
		const result = await copyCodeToClipboard(codeElement);

		// Assert
		expect(mockWriteText).toHaveBeenCalledWith('print("hello world")');
		expect(result).toBe(true);
	});

	it('returns true on successful copy', async () => {
		// Arrange
		const codeElement = document.createElement('code');
		codeElement.textContent = 'test code';

		// Mock clipboard API
		Object.assign(navigator, {
			clipboard: {
				writeText: vi.fn().mockResolvedValue(undefined)
			}
		});

		// Act
		const result = await copyCodeToClipboard(codeElement);

		// Assert
		expect(result).toBe(true);
	});

	it('returns false on clipboard API failure', async () => {
		// Arrange
		const codeElement = document.createElement('code');
		codeElement.textContent = 'test code';

		// Mock clipboard API failure
		Object.assign(navigator, {
			clipboard: {
				writeText: vi.fn().mockRejectedValue(new Error('Clipboard access denied'))
			}
		});

		// Mock execCommand fallback to also fail
		document.execCommand = vi.fn().mockReturnValue(false);

		// Act
		const result = await copyCodeToClipboard(codeElement);

		// Assert
		expect(result).toBe(false);
	});

	it('handles empty code blocks', async () => {
		// Arrange
		const codeElement = document.createElement('code');
		codeElement.textContent = '';

		// Mock clipboard API
		const mockWriteText = vi.fn().mockResolvedValue(undefined);
		Object.assign(navigator, {
			clipboard: {
				writeText: mockWriteText
			}
		});

		// Act
		const result = await copyCodeToClipboard(codeElement);

		// Assert
		expect(mockWriteText).toHaveBeenCalledWith('');
		expect(result).toBe(true);
	});
});
