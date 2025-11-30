import { test, expect } from '@playwright/test';

/**
 * Test: After clicking "New Chat", user should be able to type immediately
 * and see text appear in the chat input textarea
 */

test.describe('New Chat - Input Test', () => {
	test('After clicking New Chat, user can type and see text in input', async ({ page }) => {
		// Go to Docker container
		await page.goto('http://localhost:18173');
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(3000);

		console.log('Page loaded');

		// Take initial screenshot
		await page.screenshot({ path: 'tests/e2e/screenshots/new-chat-1-initial.png', fullPage: true });

		// First, ensure a project is selected
		const projectSelect = page.locator('.project-select');
		await expect(projectSelect).toBeVisible();
		console.log('Project selector visible');

		// Click project selector to open dropdown
		await projectSelect.click();
		await page.waitForTimeout(500);

		// Select first project option if available
		const projectOptions = page.locator('.project-option');
		const optionCount = await projectOptions.count();
		console.log('Project options:', optionCount);

		if (optionCount > 0) {
			await projectOptions.first().click();
			await page.waitForTimeout(500);
			console.log('Selected first project');
		}

		// Take screenshot after project selection
		await page.screenshot({ path: 'tests/e2e/screenshots/new-chat-2-project-selected.png', fullPage: true });

		// Now click "New Chat" button
		const newChatBtn = page.locator('button:has-text("New Chat")');
		await expect(newChatBtn).toBeVisible();
		console.log('New Chat button visible');

		await newChatBtn.click();
		await page.waitForTimeout(1000);
		console.log('Clicked New Chat');

		// Take screenshot after clicking New Chat
		await page.screenshot({ path: 'tests/e2e/screenshots/new-chat-3-clicked.png', fullPage: true });

		// Check if chat interface appeared
		const chatInterface = page.locator('.chat-interface');
		const chatInterfaceExists = await chatInterface.isVisible();
		console.log('Chat interface visible:', chatInterfaceExists);

		// Check for message input area
		const messageInput = page.locator('.message-textarea, textarea[aria-label="Message input"]');
		const inputExists = await messageInput.isVisible();
		console.log('Message input visible:', inputExists);

		if (!inputExists) {
			console.log('ERROR: Message input not found after clicking New Chat');
			await page.screenshot({ path: 'tests/e2e/screenshots/new-chat-ERROR-no-input.png', fullPage: true });

			// Check what elements ARE visible
			const chatMain = await page.locator('.chat-main').isVisible();
			const emptyState = await page.locator('.empty-state').isVisible();
			const messageList = await page.locator('.message-list').isVisible();

			console.log('Chat main visible:', chatMain);
			console.log('Empty state visible:', emptyState);
			console.log('Message list visible:', messageList);
		}

		expect(inputExists).toBeTruthy();

		// Check if input is focused (should auto-focus)
		const isFocused = await messageInput.evaluate(el => document.activeElement === el);
		console.log('Input is focused:', isFocused);

		// Type a test message
		const testMessage = 'Hello, this is a test message!';
		await messageInput.fill(testMessage);
		console.log('Typed test message');

		// Take screenshot after typing
		await page.screenshot({ path: 'tests/e2e/screenshots/new-chat-4-typed.png', fullPage: true });

		// Verify the text is visible in the input
		const inputValue = await messageInput.inputValue();
		console.log('Input value:', inputValue);

		expect(inputValue).toBe(testMessage);
		console.log('✓ Text is visible in input');

		// Verify input text is actually rendered (visible to user)
		// Check if the input has the typed text
		await expect(messageInput).toHaveValue(testMessage);
		console.log('✓ Input has correct value');

		// Final screenshot
		await page.screenshot({ path: 'tests/e2e/screenshots/new-chat-5-final.png', fullPage: true });
	});

	test('Message input should be visible and editable', async ({ page }) => {
		await page.goto('http://localhost:18173');
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(3000);

		// Select a project
		const projectSelect = page.locator('.project-select');
		await projectSelect.click();
		await page.waitForTimeout(300);

		const firstOption = page.locator('.project-option').first();
		if (await firstOption.isVisible()) {
			await firstOption.click();
			await page.waitForTimeout(500);
		}

		// Click New Chat
		const newChatBtn = page.locator('button:has-text("New Chat")');
		await newChatBtn.click();
		await page.waitForTimeout(1000);

		// Find the textarea
		const textarea = page.locator('textarea.message-textarea');

		if (await textarea.isVisible()) {
			// Click to focus
			await textarea.click();
			await page.waitForTimeout(100);

			// Type using keyboard
			await page.keyboard.type('Testing keyboard input');
			await page.waitForTimeout(500);

			// Verify
			const value = await textarea.inputValue();
			console.log('Typed via keyboard:', value);
			expect(value).toContain('Testing keyboard input');

			await page.screenshot({ path: 'tests/e2e/screenshots/input-keyboard-test.png', fullPage: true });
		} else {
			console.log('Textarea not visible, checking for chat interface...');

			// Debug: what's on the page
			const bodyHtml = await page.locator('body').innerHTML();
			console.log('Page contains textarea:', bodyHtml.includes('textarea'));
			console.log('Page contains message-textarea:', bodyHtml.includes('message-textarea'));
		}
	});

	test('Chat input text should be visible (not white on white)', async ({ page }) => {
		await page.goto('http://localhost:18173');
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(3000);

		// Select project and create new chat
		const projectSelect = page.locator('.project-select');
		await projectSelect.click();
		await page.waitForTimeout(300);

		const firstOption = page.locator('.project-option').first();
		if (await firstOption.isVisible()) {
			await firstOption.click();
			await page.waitForTimeout(500);
		}

		const newChatBtn = page.locator('button:has-text("New Chat")');
		await newChatBtn.click();
		await page.waitForTimeout(1000);

		const textarea = page.locator('textarea.message-textarea');

		if (await textarea.isVisible()) {
			// Get computed styles
			const styles = await textarea.evaluate(el => {
				const computed = window.getComputedStyle(el);
				return {
					color: computed.color,
					backgroundColor: computed.backgroundColor,
					fontSize: computed.fontSize
				};
			});

			console.log('Textarea styles:');
			console.log('  Color:', styles.color);
			console.log('  Background:', styles.backgroundColor);
			console.log('  Font size:', styles.fontSize);

			// Type some text
			await textarea.fill('Testing text visibility');

			// Take screenshot to visually verify text is visible
			await page.screenshot({ path: 'tests/e2e/screenshots/text-visibility-test.png', fullPage: true });

			// Color should be dark (not white)
			// rgb(31, 41, 55) is #1f2937 (dark gray)
			expect(styles.color).not.toBe('rgb(255, 255, 255)'); // Not white
			console.log('✓ Text color is not white');
		}
	});
});
