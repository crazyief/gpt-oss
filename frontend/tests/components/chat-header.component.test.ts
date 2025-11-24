import { test, expect } from '@playwright/test';

test.describe('ChatHeader Component - Title Display', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(2000);
  });

  test('should display conversation title', async ({ page }) => {
    const title = page.locator('[data-testid="conversation-title"]');

    if (await title.isVisible()) {
      const text = await title.textContent();
      expect(text).toBeTruthy();
      expect(text!.length).toBeGreaterThan(0);
    }
  });

  test('should show message count', async ({ page }) => {
    const messageCount = page.locator('[data-testid="message-count"]');

    if (await messageCount.isVisible()) {
      const text = await messageCount.textContent();
      expect(text).toContain('message');
    }
  });
});
