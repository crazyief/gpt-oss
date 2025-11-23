<script lang="ts">
/**
 * BUG-003 Visual Test Page
 *
 * Purpose: Manually verify that short numeric responses render correctly
 * and don't display as empty markdown lists
 *
 * Usage:
 * 1. Start dev server: npm run dev
 * 2. Navigate to: http://localhost:5173/test-bug-003
 * 3. Verify all test cases display visible content (no blank boxes)
 */

import MessageContent from '$lib/components/MessageContent.svelte';

// Test cases: content and expected behavior
const testCases = [
	{
		category: 'Short Numeric Responses (BUG FIX)',
		cases: [
			{ content: ' 4.', expected: 'Should display "4." as inline code (gray background)' },
			{ content: '2.', expected: 'Should display "2." as inline code' },
			{ content: ' 99.', expected: 'Should display "99." as inline code' },
			{ content: '  1.  ', expected: 'Should display "1." as inline code' },
			{ content: '999.', expected: 'Should display "999." as inline code (3 digits)' }
		]
	},
	{
		category: 'Legitimate Ordered Lists (NO REGRESSION)',
		cases: [
			{
				content: '1. First item\n2. Second item\n3. Third item',
				expected: 'Should display as ordered list with 3 items'
			},
			{
				content: '1. Only item with content',
				expected: 'Should display as ordered list with 1 item'
			}
		]
	},
	{
		category: 'Normal Text with Numbers (NO REGRESSION)',
		cases: [
			{
				content: 'The answer is 4.',
				expected: 'Should display as plain paragraph (NOT inline code)'
			},
			{
				content: '4.5 is the average',
				expected: 'Should display as plain paragraph'
			},
			{
				content: 'Version 2.0 released',
				expected: 'Should display as plain paragraph'
			}
		]
	},
	{
		category: 'Edge Cases',
		cases: [
			{ content: '4', expected: 'Should display "4" as plain text (no period)' },
			{
				content: '1000.',
				expected: 'Should display "1000." as plain text (4 digits, pattern only matches 1-3)'
			},
			{ content: '', expected: 'Empty content - should be blank' },
			{ content: '   ', expected: 'Whitespace only - should be blank' }
		]
	},
	{
		category: 'Other Markdown Features (NO REGRESSION)',
		cases: [
			{ content: '# Heading 1', expected: 'Should render as H1' },
			{ content: '**bold** and *italic*', expected: 'Should render bold and italic' },
			{ content: '```python\nprint("hello")\n```', expected: 'Should render as code block' },
			{
				content: '[Click here](https://example.com)',
				expected: 'Should render as clickable link'
			},
			{
				content: '- Item 1\n- Item 2\n- Item 3',
				expected: 'Should render as unordered list'
			}
		]
	}
];
</script>

<div class="container mx-auto p-8 max-w-4xl">
	<h1 class="text-3xl font-bold mb-4">BUG-003 Visual Test Page</h1>
	<p class="mb-6 text-gray-600">
		This page tests the fix for BUG-003: Short numeric responses rendering as empty markdown
		lists. All test cases below should display visible content (no blank message bubbles).
	</p>

	{#each testCases as category}
		<div class="mb-8">
			<h2 class="text-2xl font-semibold mb-4 text-blue-600">{category.category}</h2>

			{#each category.cases as testCase, index}
				<div class="mb-6 border border-gray-300 rounded-lg p-4 bg-white shadow-sm">
					<div class="mb-2">
						<span class="font-mono text-sm bg-gray-100 px-2 py-1 rounded">Test {index + 1}</span>
					</div>

					<!-- Expected behavior -->
					<div class="mb-3 text-sm text-gray-600">
						<strong>Expected:</strong>
						{testCase.expected}
					</div>

					<!-- Input content (show as code) -->
					<div class="mb-3">
						<strong class="text-sm text-gray-700">Input:</strong>
						<pre class="bg-gray-50 p-2 rounded text-xs overflow-x-auto border border-gray-200"><code>{JSON.stringify(
								testCase.content
							)}</code></pre>
					</div>

					<!-- Rendered output -->
					<div class="mb-3">
						<strong class="text-sm text-gray-700">Rendered Output:</strong>
						<div
							class="border-2 border-blue-300 rounded p-3 bg-blue-50 min-h-[3rem] flex items-center"
						>
							<MessageContent content={testCase.content} isStreaming={false} />
						</div>
					</div>

					<!-- Validation info -->
					<div class="text-xs text-gray-500">
						<strong>Validation:</strong>
						<ul class="list-disc ml-5 mt-1">
							<li>Content should be visible (not blank)</li>
							<li>
								For short numeric (e.g., "4."), should have gray background (inline code style)
							</li>
							<li>For lists, should show numbered or bulleted items</li>
							<li>For plain text, should be regular paragraph</li>
						</ul>
					</div>
				</div>
			{/each}
		</div>
	{/each}

	<!-- Summary and instructions -->
	<div class="mt-12 p-6 bg-green-50 border border-green-300 rounded-lg">
		<h2 class="text-xl font-bold mb-3 text-green-800">Manual Testing Checklist</h2>
		<div class="space-y-2">
			<label class="flex items-center">
				<input type="checkbox" class="mr-2" />
				<span>All "Short Numeric Responses" display with gray background (inline code style)</span>
			</label>
			<label class="flex items-center">
				<input type="checkbox" class="mr-2" />
				<span>No blank message bubbles visible</span>
			</label>
			<label class="flex items-center">
				<input type="checkbox" class="mr-2" />
				<span>Legitimate ordered lists render with numbered items (1, 2, 3...)</span>
			</label>
			<label class="flex items-center">
				<input type="checkbox" class="mr-2" />
				<span>Normal text with numbers displays as plain paragraphs (not code)</span>
			</label>
			<label class="flex items-center">
				<input type="checkbox" class="mr-2" />
				<span>All other markdown features work (headings, bold, italic, links, code blocks)</span>
			</label>
		</div>

		<div class="mt-4 p-4 bg-white rounded border border-green-200">
			<h3 class="font-semibold mb-2">Browser Console Verification</h3>
			<p class="text-sm text-gray-700 mb-2">
				Open browser console (F12) and run these commands to verify DOM structure:
			</p>
			<pre
				class="bg-gray-100 p-3 rounded text-xs overflow-x-auto"
			><code>// Check if short numeric responses render as code (not empty lists)
const codeElements = document.querySelectorAll('.message-content code');
console.log('Code elements found:', codeElements.length);
codeElements.forEach(el => console.log('  Content:', el.textContent));

// Check for empty ordered list items (should be 0 for short numeric)
const emptyLists = document.querySelectorAll('.message-content ol li:empty');
console.log('Empty list items found:', emptyLists.length); // Should be 0

// Check all content is visible
const allContent = document.querySelectorAll('.message-content');
allContent.forEach((el, i) => {{
  const text = el.textContent.trim();
  console.log(`Content ${i + 1}: ${text.length > 0 ? 'VISIBLE' : 'EMPTY'} (${text.length} chars)`);
}});</code></pre>
		</div>
	</div>

	<!-- Return to main app -->
	<div class="mt-8 text-center">
		<a href="/" class="text-blue-600 hover:underline">← Return to Main App</a>
	</div>
</div>

<style>
	:global(body) {
		background: #f9fafb;
	}
</style>
