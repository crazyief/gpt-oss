/**
 * Bug #8/#9 Detailed Test: Input reset after New Chat
 *
 * Bug #8: Typing not showing in input after New Chat
 * Bug #9: Old text persists in input after New Chat
 *
 * NOTE: The chat input only appears when BOTH a project AND conversation are selected.
 * This test first creates a conversation to make the input visible.
 */
import { test, expect } from '@playwright/test';

test.describe('New Chat Input Reset (Bug #8 & #9)', () => {
	test('Message input should clear and focus after New Chat', async ({ page }) => {
		// Navigate to the app
		await page.goto('http://localhost:18173');
		await page.waitForLoadState('networkidle');

		// Wait for page to fully render
		await page.waitForTimeout(1000);

		// Take a screenshot to see the current state
		await page.screenshot({ path: 'test-results/input-test-initial.png' });

		// First, we need to create a conversation to see the chat input
		// Find and click "New Chat" button first
		const newChatBtn = page.locator('button:has-text("New Chat"), button:has-text("New"), [data-testid="new-chat-button"], .new-chat-button, .new-chat-btn');
		const initialBtnCount = await newChatBtn.count();
		console.log(`Initial New Chat buttons found: ${initialBtnCount}`);

		if (initialBtnCount > 0) {
			// Click to create initial conversation
			await newChatBtn.first().click();
			await page.waitForTimeout(1000);
			console.log('Created initial conversation');
		} else {
			console.log('No New Chat button found - need to select a project first');
			// Try to click on first project if available
			const projectItems = page.locator('.project-item, [data-testid="project-item"]');
			const projectCount = await projectItems.count();
			if (projectCount > 0) {
				await projectItems.first().click();
				await page.waitForTimeout(500);
				// Now try New Chat again
				const newBtn = page.locator('button:has-text("New Chat")');
				if (await newBtn.count() > 0) {
					await newBtn.first().click();
					await page.waitForTimeout(1000);
				}
			}
		}

		// Take screenshot after creating first conversation
		await page.screenshot({ path: 'test-results/input-test-after-first-newchat.png' });

		// Find message input - try multiple selectors
		const selectors = [
			'textarea.message-textarea',
			'textarea[aria-label="Message input"]',
			'textarea[placeholder*="message"]',
			'.message-input-container textarea',
			'textarea'
		];

		let messageInput = null;
		for (const selector of selectors) {
			const element = page.locator(selector).first();
			const count = await element.count();
			if (count > 0) {
				const isVisible = await element.isVisible();
				if (isVisible) {
					messageInput = element;
					console.log(`Found message input using selector: ${selector}`);
					break;
				}
			}
		}

		if (!messageInput) {
			// Take a screenshot to debug
			await page.screenshot({ path: 'test-results/input-not-found.png' });

			// List all textareas on the page
			const allTextareas = await page.locator('textarea').all();
			console.log(`Total textareas found: ${allTextareas.length}`);

			for (let i = 0; i < allTextareas.length; i++) {
				const ta = allTextareas[i];
				const classes = await ta.getAttribute('class');
				const placeholder = await ta.getAttribute('placeholder');
				const visible = await ta.isVisible();
				console.log(`Textarea ${i}: class="${classes}", placeholder="${placeholder}", visible=${visible}`);
			}

			// Check if there's a message that we need to select project
			const pageText = await page.locator('body').textContent();
			if (pageText?.includes('Select or create a project')) {
				console.log('Page shows: Select or create a project - need to create project first');
			}
			if (pageText?.includes('Start a Conversation')) {
				console.log('Page shows: Start a Conversation - need to click New Chat');
			}

			test.skip(true, 'Message input not found - may need project/conversation setup');
			return;
		}

		// Type some text
		console.log('Typing test text...');
		await messageInput.click();
		await messageInput.fill('This text should be cleared after New Chat');

		// Verify text was entered
		const textBefore = await messageInput.inputValue();
		console.log(`Text before New Chat: "${textBefore}"`);
		expect(textBefore).toBe('This text should be cleared after New Chat');

		// Take screenshot showing text in input
		await page.screenshot({ path: 'test-results/input-test-with-text.png' });

		// Find New Chat button
		const newChatButton = page.locator('button:has-text("New Chat"), button:has-text("New"), [data-testid="new-chat-button"], .new-chat-button, .new-chat-btn');
		const buttonCount = await newChatButton.count();
		console.log(`New Chat buttons found: ${buttonCount}`);

		if (buttonCount === 0) {
			// Try to find any button that might be the new chat button
			const allButtons = await page.locator('button').all();
			console.log(`Total buttons on page: ${allButtons.length}`);
			for (let i = 0; i < allButtons.length; i++) {
				const btn = allButtons[i];
				const text = await btn.textContent();
				const classes = await btn.getAttribute('class');
				console.log(`Button ${i}: text="${text?.trim()}", class="${classes}"`);
			}

			test.skip(true, 'New Chat button not found on page');
			return;
		}

		// Click New Chat button
		console.log('Clicking New Chat button...');
		await newChatButton.first().click();

		// Wait for conversation to be created and state to reset
		await page.waitForTimeout(1000);

		// Check if input was cleared (Bug #9)
		const textAfter = await messageInput.inputValue();
		console.log(`Text after New Chat: "${textAfter}"`);

		// Take screenshot after new chat
		await page.screenshot({ path: 'test-results/input-test-after-newchat.png' });

		// Verify input is cleared
		if (textAfter === '') {
			console.log('PASS: Bug #9 - Input text was cleared after New Chat');
		} else {
			console.log('FAIL: Bug #9 - Input text was NOT cleared after New Chat');
		}
		expect(textAfter).toBe('');

		// Verify input can receive new text (Bug #8)
		console.log('Testing new text input...');
		await messageInput.fill('New message after reset');
		const newText = await messageInput.inputValue();

		if (newText === 'New message after reset') {
			console.log('PASS: Bug #8 - Input accepts new text after New Chat');
		} else {
			console.log('FAIL: Bug #8 - Input does not accept new text after New Chat');
		}
		expect(newText).toBe('New message after reset');
	});
});
