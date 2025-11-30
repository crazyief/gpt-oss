/**
 * E2E Test: UI Fixes Verification
 *
 * Tests the following UI fixes:
 * 1. No "ID:" text displayed in chat header
 * 2. Input area has transparent background (matches chat)
 * 3. Header area has transparent background (no white box)
 * 4. Delete button removed from sidebar (only in Settings)
 * 5. Double-click nav icon returns to Chat tab
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:18173';

test.describe('UI Fixes Verification', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto(BASE_URL);

    // Wait for app to load
    await page.waitForSelector('.project-select', { timeout: 10000 });
    await page.waitForTimeout(500);
  });

  test('Chat header should NOT display conversation ID', async ({ page }) => {
    // Click New Chat to create a conversation
    const newChatButton = page.locator('button:has-text("New Chat")');
    await expect(newChatButton).toBeVisible();
    await newChatButton.click();

    // Wait for conversation to be created
    await page.waitForTimeout(1000);

    // Verify no "ID:" text anywhere in the chat interface
    const chatInterface = page.locator('.chat-interface');
    await expect(chatInterface).toBeVisible();

    // Check that "ID:" text does NOT exist in the header
    const idText = page.locator('text=/ID:\\s*\\d+/');
    await expect(idText).toHaveCount(0);

    // Also check using getByText
    const idTextAlt = page.getByText(/^ID:\s*\d+$/);
    await expect(idTextAlt).toHaveCount(0);

    console.log('[TEST PASSED] No ID text displayed in chat header');
  });

  test('Message input container should have transparent background', async ({ page }) => {
    // Click New Chat
    await page.locator('button:has-text("New Chat")').click();
    await page.waitForTimeout(1000);

    // Get the message input container
    const inputContainer = page.locator('.message-input-container');
    await expect(inputContainer).toBeVisible();

    // Check computed background style
    const bgColor = await inputContainer.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });

    // Transparent background should be 'rgba(0, 0, 0, 0)' or 'transparent'
    const isTransparent = bgColor === 'rgba(0, 0, 0, 0)' || bgColor === 'transparent';
    expect(isTransparent).toBe(true);

    console.log(`[TEST PASSED] Input container background: ${bgColor} (transparent)`);
  });

  test('Chat header should have transparent background', async ({ page }) => {
    // Click New Chat
    await page.locator('button:has-text("New Chat")').click();
    await page.waitForTimeout(1000);

    // Get the chat header
    const chatHeader = page.locator('.chat-header');
    await expect(chatHeader).toBeVisible();

    // Check computed background style
    const bgColor = await chatHeader.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });

    // Transparent background
    const isTransparent = bgColor === 'rgba(0, 0, 0, 0)' || bgColor === 'transparent';
    expect(isTransparent).toBe(true);

    // Also verify no box-shadow
    const boxShadow = await chatHeader.evaluate((el) => {
      return window.getComputedStyle(el).boxShadow;
    });
    expect(boxShadow).toBe('none');

    console.log(`[TEST PASSED] Chat header background: ${bgColor}, box-shadow: ${boxShadow}`);
  });

  test('Sidebar should NOT have Delete button next to project selector', async ({ page }) => {
    // Wait for project selector to be visible
    const projectSelector = page.locator('.project-select');
    await expect(projectSelector).toBeVisible();

    // Check there's no delete button as sibling to project selector in the header area
    // The delete button should only exist in conversation items, not in project row
    const projectSelectorContainer = page.locator('.project-selector-container');
    await expect(projectSelectorContainer).toBeVisible();

    // Get the parent row and check for delete buttons
    const projectRow = projectSelectorContainer.locator('..');
    const deleteButtonInRow = projectRow.locator('button:has-text("Delete")');
    await expect(deleteButtonInRow).toHaveCount(0);

    // Verify no standalone delete button near project selector
    const nearbyDeleteButton = page.locator('.project-select + button:has-text("Delete")');
    await expect(nearbyDeleteButton).toHaveCount(0);

    console.log('[TEST PASSED] No delete button in sidebar project area');
  });

  test('Double-click on Documents tab should return to Chat tab', async ({ page }) => {
    // First, ensure we're on Chat tab
    const chatTab = page.locator('nav[aria-label="Main navigation"] button').first();
    await expect(chatTab).toHaveAttribute('aria-selected', 'true');

    // Click Documents tab to switch to it
    const docsTab = page.locator('nav[aria-label="Main navigation"] button').nth(1);
    await docsTab.click();
    await page.waitForTimeout(300);

    // Verify we're now on Documents tab
    await expect(docsTab).toHaveAttribute('aria-selected', 'true');

    // Double-click on Documents tab (should return to Chat)
    await docsTab.dblclick();
    await page.waitForTimeout(300);

    // Verify we're back on Chat tab
    await expect(chatTab).toHaveAttribute('aria-selected', 'true');

    console.log('[TEST PASSED] Double-click returns to Chat tab');
  });

  test('Double-click on Settings tab should return to Chat tab', async ({ page }) => {
    // Click Settings tab
    const settingsTab = page.locator('nav[aria-label="Main navigation"] button').nth(2);
    await settingsTab.click();
    await page.waitForTimeout(300);

    // Verify we're on Settings tab
    await expect(settingsTab).toHaveAttribute('aria-selected', 'true');

    // Double-click on Settings tab
    await settingsTab.dblclick();
    await page.waitForTimeout(300);

    // Verify we're back on Chat tab
    const chatTab = page.locator('nav[aria-label="Main navigation"] button').first();
    await expect(chatTab).toHaveAttribute('aria-selected', 'true');

    console.log('[TEST PASSED] Double-click on Settings returns to Chat tab');
  });

  test('Input textarea should be visible and functional after New Chat', async ({ page }) => {
    // Click New Chat
    await page.locator('button:has-text("New Chat")').click();
    await page.waitForTimeout(1000);

    // Verify textarea is visible
    const textarea = page.locator('textarea[aria-label="Message input"]');
    await expect(textarea).toBeVisible();
    await expect(textarea).toBeEnabled();

    // Type a message
    await textarea.fill('Hello, this is a test message');

    // Verify the text was entered
    await expect(textarea).toHaveValue('Hello, this is a test message');

    // Verify send button is enabled
    const sendButton = page.locator('button[aria-label="Send message"]');
    await expect(sendButton).toBeEnabled();

    console.log('[TEST PASSED] Input textarea is visible and functional');
  });

  test('Full UI flow: Create conversation and verify all UI elements', async ({ page }) => {
    // 1. Create new conversation
    await page.locator('button:has-text("New Chat")').click();
    await page.waitForTimeout(1000);

    // 2. Verify chat interface structure
    const chatInterface = page.locator('.chat-interface');
    await expect(chatInterface).toBeVisible();

    // 3. Verify NO ID text
    const pageContent = await page.content();
    expect(pageContent).not.toMatch(/ID:\s*\d+/);

    // 4. Verify input area exists
    const inputArea = page.locator('.message-input-container');
    await expect(inputArea).toBeVisible();

    // 5. Verify token usage is NOT shown (no messages yet)
    const tokenUsage = page.locator('.token-usage');
    await expect(tokenUsage).toHaveCount(0);

    // 6. Verify the input has proper styling
    const textarea = page.locator('textarea.message-textarea');
    await expect(textarea).toBeVisible();

    // Check textarea has a light/white background for readability
    // (the CONTAINER is transparent, but textarea itself should be readable)
    const textareaBg = await textarea.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    // Textarea should have white or near-white background
    expect(textareaBg).toMatch(/rgb\(255,\s*255,\s*255\)|rgba\(255,\s*255,\s*255/);

    console.log('[TEST PASSED] Full UI flow verification complete');
  });
});
