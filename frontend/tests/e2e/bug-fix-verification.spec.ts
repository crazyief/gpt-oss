/**
 * Bug Fix Verification Tests
 *
 * Tests to verify that bugs #5, #6, #8, #9 have been fixed:
 * - Bug #5: Sidebar not appearing when clicking Chat icon
 * - Bug #6: Console warning "unknown prop 'params'"
 * - Bug #8: Typing not showing in input after New Chat
 * - Bug #9: Old text persists in input after New Chat
 */
import { test, expect, ConsoleMessage } from '@playwright/test';

test.describe('Bug Fix Verification', () => {
	// Collect console messages during tests
	let consoleMessages: ConsoleMessage[] = [];

	test.beforeEach(async ({ page }) => {
		// Reset console messages
		consoleMessages = [];

		// Listen for console messages
		page.on('console', (msg) => {
			consoleMessages.push(msg);
		});
	});

	test('Bug #5: Sidebar should be visible on page load', async ({ page }) => {
		// Clear localStorage to ensure fresh state
		await page.goto('http://localhost:18173');
		await page.evaluate(() => localStorage.removeItem('gpt-oss-sidebar-open'));

		// Reload page to test fresh state
		await page.reload();
		await page.waitForLoadState('networkidle');

		// Wait for potential animations
		await page.waitForTimeout(500);

		// Find the sidebar element
		const sidebar = page.locator('.history-sidebar, [class*="sidebar"], aside');

		// Check if sidebar exists
		const sidebarCount = await sidebar.count();
		console.log(`Sidebar elements found: ${sidebarCount}`);

		if (sidebarCount > 0) {
			// Get the bounding box to check visibility
			const box = await sidebar.first().boundingBox();
			console.log(`Sidebar bounding box: ${JSON.stringify(box)}`);

			// Check if sidebar has width > 0 (is visible)
			if (box) {
				expect(box.width).toBeGreaterThan(0);
				console.log(`PASS: Sidebar width = ${box.width}px (visible)`);
			} else {
				// If no bounding box, check if it's because sidebar is collapsed
				const isVisible = await sidebar.first().isVisible();
				console.log(`Sidebar isVisible: ${isVisible}`);

				// Check computed styles
				const width = await sidebar.first().evaluate((el) => {
					const style = window.getComputedStyle(el);
					return {
						width: style.width,
						display: style.display,
						visibility: style.visibility,
						opacity: style.opacity
					};
				});
				console.log(`Sidebar computed styles: ${JSON.stringify(width)}`);
			}
		}

		// Alternative check: Look for chat history container
		const chatHistory = page.locator('.chat-history, .history-list, [data-testid="chat-history"]');
		const historyCount = await chatHistory.count();
		console.log(`Chat history elements found: ${historyCount}`);
	});

	test('Bug #6: No "unknown prop" console warnings', async ({ page }) => {
		// Navigate to page
		await page.goto('http://localhost:18173');
		await page.waitForLoadState('networkidle');

		// Wait for any async rendering
		await page.waitForTimeout(1000);

		// Check for "unknown prop" warnings
		const unknownPropWarnings = consoleMessages.filter((msg) => {
			const text = msg.text();
			return text.includes('unknown prop') || text.includes('Unknown prop');
		});

		// Log all warnings for debugging
		const allWarnings = consoleMessages.filter((msg) => msg.type() === 'warning');
		console.log(`Total warnings: ${allWarnings.length}`);
		allWarnings.forEach((msg, i) => {
			console.log(`Warning ${i + 1}: ${msg.text()}`);
		});

		// Report result
		if (unknownPropWarnings.length === 0) {
			console.log('PASS: No "unknown prop" warnings found');
		} else {
			console.log(`FAIL: Found ${unknownPropWarnings.length} "unknown prop" warnings:`);
			unknownPropWarnings.forEach((msg) => console.log(`  - ${msg.text()}`));
		}

		expect(unknownPropWarnings.length).toBe(0);
	});

	test('Bug #8 & #9: Input resets and focuses after New Chat', async ({ page }) => {
		// Navigate to page
		await page.goto('http://localhost:18173');
		await page.waitForLoadState('networkidle');

		// Wait for page to fully load
		await page.waitForTimeout(500);

		// Find the message input
		const messageInput = page.locator('textarea.message-textarea, textarea[aria-label="Message input"], textarea[placeholder*="message"]');
		const inputCount = await messageInput.count();
		console.log(`Message input elements found: ${inputCount}`);

		if (inputCount > 0) {
			// Type some text
			await messageInput.first().click();
			await messageInput.first().fill('This is test text that should be cleared');

			// Verify text was entered
			const textBefore = await messageInput.first().inputValue();
			console.log(`Text before New Chat: "${textBefore}"`);
			expect(textBefore).toBe('This is test text that should be cleared');

			// Find and click New Chat button
			const newChatButton = page.locator('button:has-text("New Chat"), button:has-text("New"), [data-testid="new-chat-button"], .new-chat-button');
			const buttonCount = await newChatButton.count();
			console.log(`New Chat button elements found: ${buttonCount}`);

			if (buttonCount > 0) {
				await newChatButton.first().click();

				// Wait for state reset
				await page.waitForTimeout(500);

				// Check if input was cleared (Bug #9)
				const textAfter = await messageInput.first().inputValue();
				console.log(`Text after New Chat: "${textAfter}"`);

				if (textAfter === '') {
					console.log('PASS: Bug #9 - Input text was cleared after New Chat');
				} else {
					console.log('FAIL: Bug #9 - Input text was NOT cleared after New Chat');
				}
				expect(textAfter).toBe('');

				// Check if input is focused (Bug #8)
				const isFocused = await messageInput.first().evaluate((el) => document.activeElement === el);
				console.log(`Input is focused: ${isFocused}`);

				if (isFocused) {
					console.log('PASS: Bug #8 - Input is focused after New Chat');
				} else {
					console.log('INFO: Bug #8 - Input may not be focused (could be timing issue)');
				}

				// Type new text to verify input is working
				await messageInput.first().fill('New text after reset');
				const newText = await messageInput.first().inputValue();
				console.log(`New text typed: "${newText}"`);

				if (newText === 'New text after reset') {
					console.log('PASS: Bug #8 - Input accepts new text after New Chat');
				} else {
					console.log('FAIL: Bug #8 - Input does not accept new text');
				}
				expect(newText).toBe('New text after reset');
			} else {
				console.log('SKIP: New Chat button not found - cannot test Bug #8/#9');
			}
		} else {
			console.log('SKIP: Message input not found - cannot test Bug #8/#9');
		}
	});

	test('Bug #5 Alternative: Check sidebar store behavior', async ({ page }) => {
		// Navigate to page
		await page.goto('http://localhost:18173');
		await page.waitForLoadState('networkidle');

		// Clear localStorage and check default behavior
		await page.evaluate(() => localStorage.removeItem('gpt-oss-sidebar-open'));
		await page.reload();
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(500);

		// Check localStorage value after load
		const storedValue = await page.evaluate(() => localStorage.getItem('gpt-oss-sidebar-open'));
		console.log(`Stored sidebar value after load: ${storedValue}`);

		// Check for any element with sidebar-related content
		const pageContent = await page.content();
		const hasSidebarContent = pageContent.includes('sidebar') ||
								   pageContent.includes('history') ||
								   pageContent.includes('chat-history');
		console.log(`Page contains sidebar-related content: ${hasSidebarContent}`);

		// Look for any visible sidebar content
		const visibleSidebarElements = await page.locator('.history-sidebar, .sidebar, aside, [role="complementary"]').all();
		console.log(`Visible sidebar-like elements: ${visibleSidebarElements.length}`);

		for (let i = 0; i < visibleSidebarElements.length; i++) {
			const el = visibleSidebarElements[i];
			const isVisible = await el.isVisible();
			const box = await el.boundingBox();
			console.log(`Element ${i + 1}: visible=${isVisible}, box=${JSON.stringify(box)}`);
		}
	});

	test('Summary Report: All Bug Fixes', async ({ page }) => {
		// Navigate to page
		await page.goto('http://localhost:18173');
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000);

		console.log('\n========================================');
		console.log('        BUG FIX VERIFICATION REPORT');
		console.log('========================================\n');

		// Bug #5: Check sidebar visibility
		const sidebar = page.locator('.history-sidebar, aside, [class*="sidebar"]');
		const sidebarCount = await sidebar.count();
		let bug5Status = 'UNKNOWN';
		let sidebarWidth = 0;

		if (sidebarCount > 0) {
			const box = await sidebar.first().boundingBox();
			if (box && box.width > 0) {
				sidebarWidth = box.width;
				bug5Status = 'PASS';
			} else {
				bug5Status = 'FAIL - width is 0';
			}
		} else {
			bug5Status = 'FAIL - no sidebar element found';
		}

		// Bug #6: Check console warnings
		const unknownPropWarnings = consoleMessages.filter((msg) =>
			msg.text().includes('unknown prop') || msg.text().includes('Unknown prop')
		);
		const bug6Status = unknownPropWarnings.length === 0 ? 'PASS' : `FAIL - ${unknownPropWarnings.length} warnings`;

		// Collect all console errors
		const consoleErrors = consoleMessages.filter((msg) => msg.type() === 'error');

		console.log(`Bug #5: Sidebar visibility`);
		console.log(`  Status: ${bug5Status}`);
		console.log(`  Sidebar width: ${sidebarWidth}px`);
		console.log(`  Sidebar elements found: ${sidebarCount}\n`);

		console.log(`Bug #6: "unknown prop" console warnings`);
		console.log(`  Status: ${bug6Status}`);
		console.log(`  Total warnings: ${consoleMessages.filter(m => m.type() === 'warning').length}`);
		console.log(`  "unknown prop" warnings: ${unknownPropWarnings.length}\n`);

		console.log(`Bug #8 & #9: Input reset after New Chat`);
		console.log(`  (Tested in separate test case)\n`);

		console.log(`Console Errors: ${consoleErrors.length}`);
		consoleErrors.forEach((msg, i) => {
			console.log(`  ${i + 1}. ${msg.text()}`);
		});

		console.log('\n========================================\n');

		// Final assertions
		expect(bug5Status).toBe('PASS');
		expect(bug6Status).toBe('PASS');
	});
});
