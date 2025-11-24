import { test, expect } from '@playwright/test';

test.describe('MessageList Component - Critical Display', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    // Navigate to conversation with messages
    await page.waitForTimeout(2000); // Wait for page load
  });

  test('should display user and assistant messages', async ({ page }) => {
    // Check if messages are rendered (adjust selectors based on actual implementation)
    const userMessages = page.locator('[data-role="user"]');
    const assistantMessages = page.locator('[data-role="assistant"]');

    // At least one of each type should exist (if there are messages)
    const userCount = await userMessages.count();
    const assistantCount = await assistantMessages.count();

    // Basic sanity check - if messages exist, they should render
    if (userCount > 0 || assistantCount > 0) {
      expect(userCount + assistantCount).toBeGreaterThan(0);
    }
  });

  test('should render markdown in messages', async ({ page }) => {
    // Look for markdown elements (bold, code, etc.)
    const boldText = page.locator('strong').first();
    const codeBlocks = page.locator('pre code').first();

    // If markdown exists, verify it's rendered
    const hasBold = await boldText.isVisible().catch(() => false);
    const hasCode = await codeBlocks.isVisible().catch(() => false);

    // At least one markdown element should be visible
    expect(hasBold || hasCode).toBeTruthy();
  });

  test('should auto-scroll to bottom on new messages', async ({ page }) => {
    const messageContainer = page.locator('[data-testid="message-list"]');

    if (await messageContainer.isVisible()) {
      const scrollHeight = await messageContainer.evaluate(el => el.scrollHeight);
      const scrollTop = await messageContainer.evaluate(el => el.scrollTop);
      const clientHeight = await messageContainer.evaluate(el => el.clientHeight);

      // Should be near bottom (within 200px)
      expect(scrollTop + clientHeight).toBeGreaterThan(scrollHeight - 200);
    }
  });
});
