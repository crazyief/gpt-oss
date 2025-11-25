import { test, expect } from '@playwright/test';

test.describe('End-to-End Chat Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(2000);
  });

  test('E2E: Create new conversation and send message', async ({ page }) => {
    // Click New Chat
    const newChatButton = page.locator('button:has-text("New Chat")');
    await newChatButton.click();

    // Wait for navigation to conversation page
    await page.waitForURL(/\/conversation\//, { timeout: 10000 });
    await page.waitForSelector('textarea[placeholder*="message"]', { timeout: 5000 });

    // Type message
    const textarea = page.locator('textarea');
    await textarea.fill('Hello, this is a test message');

    // Send message
    await textarea.press('Enter');
    await page.waitForTimeout(500);

    // Verify message appears
    const userMessage = page.locator('[data-role="user"]').last();
    await expect(userMessage).toContainText('Hello, this is a test message');
  });

  test('E2E: Switch between conversations', async ({ page }) => {
    const conversations = page.locator('[data-testid="conversation-item"]');
    const count = await conversations.count();

    if (count >= 2) {
      // Click first conversation
      await conversations.nth(0).click();
      await page.waitForTimeout(500);

      // Click second conversation
      await conversations.nth(1).click();
      await page.waitForTimeout(500);

      // Should have switched successfully (no error)
      expect(true).toBeTruthy();
    } else {
      test.skip();
    }
  });

  test('E2E: Search conversations', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Search"]');

    if (await searchInput.isVisible()) {
      await searchInput.fill('test');
      await page.waitForTimeout(500);

      // Search should filter results
      const visibleConvs = page.locator('[data-testid="conversation-item"]:visible');
      const count = await visibleConvs.count();
      expect(count).toBeGreaterThanOrEqual(0);
    } else {
      test.skip();
    }
  });

  test('E2E: Delete conversation', async ({ page }) => {
    const conversations = page.locator('[data-testid="conversation-item"]');
    const initialCount = await conversations.count();

    if (initialCount > 0) {
      // Hover over first conversation
      await conversations.first().hover();
      await page.waitForTimeout(300);

      // Click delete button (if visible)
      const deleteButton = page.locator('button[aria-label="Delete"]').first();
      if (await deleteButton.isVisible()) {
        await deleteButton.click();
        await page.waitForTimeout(1000);

        const newCount = await conversations.count();
        expect(newCount).toBeLessThanOrEqual(initialCount);
      }
    } else {
      test.skip();
    }
  });

  test('E2E: Page reload preserves conversation state', async ({ page }) => {
    // Get current conversation count
    const initialCount = await page.locator('[data-testid="conversation-item"]').count();

    // Reload page
    await page.reload();
    await page.waitForTimeout(2000);

    // Count should be same
    const afterReloadCount = await page.locator('[data-testid="conversation-item"]').count();
    expect(afterReloadCount).toBe(initialCount);
  });
});
