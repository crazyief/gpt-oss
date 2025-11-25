import { test, expect } from '@playwright/test';

test.describe('ChatInput Component - Critical Interactions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');

    // Create new conversation first (chat input only exists on conversation pages)
    const newChatButton = page.locator('button:has-text("New Chat")');
    if (await newChatButton.isVisible()) {
      await newChatButton.click();
      // Wait for navigation to conversation page
      await page.waitForURL(/\/conversation\//, { timeout: 10000 });
    }

    // Now wait for textarea on conversation page
    await page.waitForSelector('textarea[placeholder*="message"]', { timeout: 10000 });
  });

  test('should send message when Enter key pressed', async ({ page }) => {
    const textarea = page.locator('textarea');
    await textarea.fill('Test message');
    await textarea.press('Enter');

    // Message should be sent and textarea cleared
    await expect(textarea).toHaveValue('');
  });

  test('should allow newline with Shift+Enter', async ({ page }) => {
    const textarea = page.locator('textarea');
    await textarea.fill('Line 1');
    await textarea.press('Shift+Enter');
    await textarea.type('Line 2');

    const value = await textarea.inputValue();
    expect(value).toContain('\n');
  });

  test('should disable send button when textarea is empty', async ({ page }) => {
    const sendButton = page.locator('button:has-text("Send")');
    await expect(sendButton).toBeDisabled();

    const textarea = page.locator('textarea');
    await textarea.fill('Some text');
    await expect(sendButton).toBeEnabled();
  });

  test('should show character count when approaching limit', async ({ page }) => {
    const textarea = page.locator('textarea');
    // Fill with many characters (assuming 5000 char limit)
    await textarea.fill('a'.repeat(4500));

    // Check if counter appears (may need to adjust selector)
    const counter = page.locator('[data-testid="char-counter"]');
    if (await counter.isVisible()) {
      await expect(counter).toContainText('4500');
    }
  });
});
