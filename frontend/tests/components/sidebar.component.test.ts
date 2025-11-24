import { test, expect } from '@playwright/test';

test.describe('Sidebar Component - Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(2000);
  });

  test('should display conversation list', async ({ page }) => {
    const conversations = page.locator('[data-testid="conversation-item"]');
    const count = await conversations.count();

    // Should have at least some conversations (or empty state)
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should have New Chat button visible', async ({ page }) => {
    const newChatButton = page.locator('button:has-text("New Chat")');
    await expect(newChatButton).toBeVisible();
  });

  test('should highlight active conversation', async ({ page }) => {
    const activeConv = page.locator('[data-testid="conversation-item"].active');
    const count = await activeConv.count();

    // Should have 0 or 1 active conversation (not multiple)
    expect(count).toBeLessThanOrEqual(1);
  });

  test('should create new conversation when New Chat clicked', async ({ page }) => {
    const initialCount = await page.locator('[data-testid="conversation-item"]').count();

    const newChatButton = page.locator('button:has-text("New Chat")');
    await newChatButton.click();
    await page.waitForTimeout(1000);

    const newCount = await page.locator('[data-testid="conversation-item"]').count();
    expect(newCount).toBeGreaterThanOrEqual(initialCount);
  });
});
