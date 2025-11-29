/**
 * BUG-003 Test Suite: Markdown Short Numeric Response Fix
 *
 * Purpose: Verify that short numeric responses display correctly
 * and don't render as empty ordered lists
 *
 * Bug Description:
 * - Short responses like " 4." were rendered as <ol><li></li></ol>
 * - Resulted in blank message bubbles visible to users
 * - Caused by marked.js interpreting "4." as ordered list item #4
 *
 * Fix Implementation:
 * - Pre-process content in MessageContent.svelte
 * - Detect pattern /^\s*\d{1,3}\.\s*$/
 * - Wrap matched content in backticks (inline code)
 * - Example: " 4." → "`4.`" → renders as <code>4.</code>
 */

import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import MessageContent from '$lib/components/MessageContent.svelte';

describe('BUG-003: Short Numeric Response Fix', () => {
	/**
	 * Test Case 1: Basic Short Numeric Response
	 *
	 * The original bug scenario - LLM responds with just a number and period
	 */
	describe('Short numeric responses', () => {
		it('should render " 4." as visible content (not empty list)', () => {
			const { container } = render(MessageContent, { content: ' 4.' });

			// Should NOT create empty ordered list
			const emptyList = container.querySelector('ol li:empty');
			expect(emptyList).toBeNull();

			// Should have visible text content
			const textContent = container.textContent?.trim();
			expect(textContent).toBeTruthy();
			expect(textContent).toContain('4.');

			// Should render as inline code (the fix wraps it in backticks)
			const codeElement = container.querySelector('code');
			expect(codeElement).toBeTruthy();
			expect(codeElement?.textContent).toBe('4.');
		});

		it('should render "2." as visible content', () => {
			const { container } = render(MessageContent, { content: '2.' });

			const textContent = container.textContent?.trim();
			expect(textContent).toBeTruthy();
			expect(textContent).toContain('2.');

			// Should not be an empty ordered list
			const emptyList = container.querySelector('ol li:empty');
			expect(emptyList).toBeNull();
		});

		it('should render " 99." as visible content', () => {
			const { container } = render(MessageContent, { content: ' 99.' });

			const textContent = container.textContent?.trim();
			expect(textContent).toBeTruthy();
			expect(textContent).toContain('99.');
		});

		it('should render "  1.  " (with extra whitespace) as visible content', () => {
			const { container } = render(MessageContent, { content: '  1.  ' });

			const textContent = container.textContent?.trim();
			expect(textContent).toBeTruthy();
			expect(textContent).toContain('1.');
		});
	});

	/**
	 * Test Case 2: Regression Prevention - Legitimate Lists
	 *
	 * Ensure the fix doesn't break normal ordered list functionality
	 */
	describe('Legitimate ordered lists (should NOT be affected by fix)', () => {
		it('should render multi-item ordered list correctly', () => {
			const content = '1. First item\n2. Second item\n3. Third item';
			const { container } = render(MessageContent, { content });

			// Should create ordered list
			const ol = container.querySelector('ol');
			expect(ol).toBeTruthy();

			// Should have 3 list items with content
			const listItems = container.querySelectorAll('li');
			expect(listItems.length).toBe(3);

			// Items should have content
			expect(listItems[0].textContent).toContain('First item');
			expect(listItems[1].textContent).toContain('Second item');
			expect(listItems[2].textContent).toContain('Third item');
		});

		it('should render single-item ordered list correctly', () => {
			const content = '1. Only item with actual content';
			const { container } = render(MessageContent, { content });

			// Should create ordered list
			const ol = container.querySelector('ol');
			expect(ol).toBeTruthy();

			// Should have 1 list item with content
			const listItems = container.querySelectorAll('li');
			expect(listItems.length).toBe(1);
			expect(listItems[0].textContent).toContain('Only item with actual content');
		});
	});

	/**
	 * Test Case 3: Regression Prevention - Normal Text
	 *
	 * Ensure normal text containing numbers isn't affected
	 */
	describe('Normal text with numbers (should NOT be affected by fix)', () => {
		it('should render "The answer is 4." as plain text', () => {
			const content = 'The answer is 4.';
			const { container } = render(MessageContent, { content });

			// Should render as paragraph, not code or list
			const p = container.querySelector('p');
			expect(p).toBeTruthy();
			expect(p?.textContent).toContain('The answer is 4.');

			// Should NOT wrap in code
			const code = container.querySelector('code');
			expect(code).toBeNull();
		});

		it('should render "4.5 is the average" as plain text', () => {
			const content = '4.5 is the average';
			const { container } = render(MessageContent, { content });

			const textContent = container.textContent?.trim();
			expect(textContent).toContain('4.5 is the average');

			// Should not trigger the fix (no match on /^\s*\d{1,3}\.\s*$/)
			const code = container.querySelector('code');
			expect(code).toBeNull();
		});

		it('should render "Version 2.0 released" as plain text', () => {
			const content = 'Version 2.0 released';
			const { container } = render(MessageContent, { content });

			const textContent = container.textContent?.trim();
			expect(textContent).toContain('Version 2.0 released');
		});
	});

	/**
	 * Test Case 4: Edge Cases
	 *
	 * Test boundary conditions and unusual inputs
	 */
	describe('Edge cases', () => {
		it('should handle single digit "4" (no period) normally', () => {
			const content = '4';
			const { container } = render(MessageContent, { content });

			const textContent = container.textContent?.trim();
			expect(textContent).toBe('4');

			// No period, so shouldn't match pattern - no code wrapper
			// (This is normal text, not the bug pattern)
		});

		it('should handle three-digit number "999." as short numeric', () => {
			const content = '999.';
			const { container } = render(MessageContent, { content });

			const textContent = container.textContent?.trim();
			expect(textContent).toBeTruthy();
			expect(textContent).toContain('999.');

			// Should match pattern (\d{1,3}) and be wrapped in code
			const code = container.querySelector('code');
			expect(code).toBeTruthy();
		});

		it('should treat four-digit number "1000." as short numeric', () => {
			const content = '1000.';
			const { container } = render(MessageContent, { content });

			const textContent = container.textContent?.trim();
			expect(textContent).toContain('1000.');

			// Pattern matches any digits, so 1000. SHOULD be wrapped in code
			// This prevents markdown from interpreting it as an ordered list
			const code = container.querySelector('code');
			expect(code).toBeTruthy();
		});

		it('should handle empty content gracefully', () => {
			const { container } = render(MessageContent, { content: '' });

			const textContent = container.textContent?.trim();
			expect(textContent).toBe('');
		});

		it('should handle whitespace-only content', () => {
			const { container } = render(MessageContent, { content: '   ' });

			const textContent = container.textContent?.trim();
			expect(textContent).toBe('');
		});
	});

	/**
	 * Test Case 5: Markdown Features (Regression Prevention)
	 *
	 * Ensure other markdown features still work correctly
	 */
	describe('Other markdown features (regression check)', () => {
		it('should render headings correctly', () => {
			const content = '# Heading 1\n## Heading 2';
			const { container } = render(MessageContent, { content });

			const h1 = container.querySelector('h1');
			const h2 = container.querySelector('h2');
			expect(h1).toBeTruthy();
			expect(h2).toBeTruthy();
			expect(h1?.textContent).toContain('Heading 1');
			expect(h2?.textContent).toContain('Heading 2');
		});

		it('should render code blocks correctly', () => {
			// Use multi-line code block (single-line gets converted to inline code)
			const content = '```python\nprint("hello")\nprint("world")\n```';
			const { container } = render(MessageContent, { content });

			const pre = container.querySelector('pre');
			const code = container.querySelector('code');
			expect(pre).toBeTruthy();
			expect(code).toBeTruthy();
			expect(code?.textContent).toContain('print("hello")');
			expect(code?.textContent).toContain('print("world")');
		});

		it('should render bold and italic correctly', () => {
			const content = '**bold** and *italic*';
			const { container } = render(MessageContent, { content });

			const strong = container.querySelector('strong');
			const em = container.querySelector('em');
			expect(strong).toBeTruthy();
			expect(em).toBeTruthy();
			expect(strong?.textContent).toBe('bold');
			expect(em?.textContent).toBe('italic');
		});

		it('should render links correctly', () => {
			const content = '[Click here](https://example.com)';
			const { container } = render(MessageContent, { content });

			const link = container.querySelector('a');
			expect(link).toBeTruthy();
			expect(link?.textContent).toBe('Click here');
			expect(link?.getAttribute('href')).toBe('https://example.com');
		});

		it('should render unordered lists correctly', () => {
			const content = '- Item 1\n- Item 2\n- Item 3';
			const { container } = render(MessageContent, { content });

			const ul = container.querySelector('ul');
			const listItems = container.querySelectorAll('li');
			expect(ul).toBeTruthy();
			expect(listItems.length).toBe(3);
		});
	});

	/**
	 * Test Case 6: Real-World Scenarios
	 *
	 * Test actual use cases from bug reports
	 */
	describe('Real-world scenarios from bug reports', () => {
		it('should handle arithmetic question: "What is 2+2?"', () => {
			// User asks: "What is 2+2? Please answer briefly."
			// LLM responds: " 4."
			const content = ' 4.';
			const { container } = render(MessageContent, { content });

			// Should display visible content (not blank)
			const textContent = container.textContent?.trim();
			expect(textContent).toBeTruthy();
			expect(textContent.length).toBeGreaterThan(0);

			// Should not create empty list
			const emptyList = container.querySelector('ol li:empty');
			expect(emptyList).toBeNull();

			// User should see "4." in some form
			expect(textContent).toContain('4.');
		});

		it('should handle enumeration response: " 1."', () => {
			const content = ' 1.';
			const { container } = render(MessageContent, { content });

			const textContent = container.textContent?.trim();
			expect(textContent).toBeTruthy();
			expect(textContent).toContain('1.');

			// Should not be empty
			expect(textContent.length).toBeGreaterThan(0);
		});

		it('should handle longer response with number: "The answer is 42."', () => {
			const content = 'The answer is 42.';
			const { container } = render(MessageContent, { content });

			const textContent = container.textContent?.trim();
			expect(textContent).toBe('The answer is 42.');

			// Should NOT trigger short numeric fix (has text before/after number)
			const code = container.querySelector('code');
			expect(code).toBeNull();
		});
	});

	/**
	 * Test Case 7: Visual Verification Helpers
	 *
	 * Tests to verify the fix produces visible content
	 */
	describe('Visual verification (textContent checks)', () => {
		it('short numeric content should have non-zero visible text length', () => {
			const testCases = [' 4.', '2.', ' 99.', '  1.  '];

			testCases.forEach((content) => {
				const { container } = render(MessageContent, { content });
				const textContent = container.textContent?.trim() || '';

				// CRITICAL: textContent must be visible (length > 0)
				expect(textContent.length, `Content "${content}" should be visible`).toBeGreaterThan(
					0
				);

				// Should contain the number
				const numberMatch = content.match(/\d+/);
				if (numberMatch) {
					expect(textContent).toContain(numberMatch[0]);
				}
			});
		});

		it('should NOT produce empty <ol> elements for short numeric responses', () => {
			const testCases = [' 4.', '2.', ' 99.', '  1.  '];

			testCases.forEach((content) => {
				const { container } = render(MessageContent, { content });

				// Should NOT have empty list items
				const emptyListItems = container.querySelectorAll('ol li:empty');
				expect(
					emptyListItems.length,
					`Content "${content}" should not produce empty <li>`
				).toBe(0);

				// Should NOT have <ol> containing only empty <li>
				const orderedLists = container.querySelectorAll('ol');
				orderedLists.forEach((ol) => {
					const items = ol.querySelectorAll('li');
					const allEmpty = Array.from(items).every(
						(item) => item.textContent?.trim() === ''
					);
					expect(
						allEmpty,
						`Content "${content}" should not have <ol> with all empty items`
					).toBe(false);
				});
			});
		});
	});
});
