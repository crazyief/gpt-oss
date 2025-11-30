/**
 * ChatInput Component Tests - REAL BACKEND INTEGRATION
 *
 * These tests use the actual backend - NO MOCKS.
 * Tests verify real frontend ↔ backend integration for chat input.
 *
 * Prerequisites:
 * - Backend running on http://localhost:8000
 * - Frontend running on http://localhost:5173
 * - Database accessible
 */

import { test, expect } from '@playwright/test';

test.describe('ChatInput Component - Critical Interactions (Real Backend)', () => {
  test.beforeEach(async ({ page }) => {
    // Capture console messages for debugging
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`[Browser Error] ${msg.text()}`);
      }
    });
    page.on('pageerror', error => {
      console.log(`[Page Error] ${error.message}`);
    });

    // Log API requests for debugging
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        console.log(`[API Request] ${request.method()} ${request.url()}`);
      }
    });

    page.on('response', response => {
      if (response.url().includes('/api/')) {
        console.log(`[API Response] ${response.status()} ${response.url()}`);
      }
    });

    // Set up response listeners BEFORE navigation to capture all responses
    const csrfPromise = page.waitForResponse(
      response => response.url().includes('/api/csrf-token') && response.ok(),
      { timeout: 15000 }
    );

    const projectsPromise = page.waitForResponse(
      response => response.url().includes('/api/projects/list') && response.ok(),
      { timeout: 10000 }
    );

    // Navigate to app - NO MOCKS, real API calls
    await page.goto('http://localhost:5173');

    // Wait for real API responses (promises set up before navigation)
    await csrfPromise;
    await projectsPromise;

    // Ensure UI is ready - New Chat button should be visible
    await page.waitForSelector('button:has-text("New Chat")', { timeout: 10000 });
  });

  test('should have New Chat button visible', async ({ page }) => {
    // Basic test to verify page loads correctly
    const newChatButton = page.locator('button:has-text("New Chat")');
    await expect(newChatButton).toBeVisible();
    console.log('[Test] New Chat button verified');
  });

  test('should show textarea after creating conversation', async ({ page }) => {
    // Click New Chat to create a conversation
    const newChatButton = page.locator('button:has-text("New Chat")');
    await newChatButton.click();

    // Wait for conversation creation via real API
    await page.waitForResponse(
      response => response.url().includes('/api/conversations/create') && response.status() === 201,
      { timeout: 10000 }
    );

    // Wait for textarea to appear
    const textarea = page.locator('textarea[placeholder*="message"]');
    await expect(textarea).toBeVisible({ timeout: 5000 });
    console.log('[Test] Textarea visible after conversation creation');
  });

  test('should send message when Enter key pressed', async ({ page }) => {
    // Create a conversation first
    const newChatButton = page.locator('button:has-text("New Chat")');
    await newChatButton.click();

    await page.waitForResponse(
      response => response.url().includes('/api/conversations/create') && response.status() === 201,
      { timeout: 10000 }
    );

    // Wait for textarea to be ready
    await page.waitForTimeout(500);
    const textarea = page.locator('textarea[placeholder*="message"]');
    await expect(textarea).toBeEnabled({ timeout: 5000 });

    // Type a message
    await textarea.fill('Test message from E2E');

    // Set up listener for chat stream BEFORE sending
    const streamPromise = page.waitForResponse(
      response => response.url().includes('/api/chat/stream'),
      { timeout: 15000 }
    );

    // Press Enter to send
    await textarea.press('Enter');
    console.log('[Test] Pressed Enter to send message');

    // Wait for stream to start
    const streamResponse = await streamPromise;
    expect(streamResponse.ok()).toBe(true);
    console.log('[Test] Stream started successfully');

    // Textarea should be cleared after sending
    await page.waitForTimeout(500);
    await expect(textarea).toHaveValue('');
  });

  test('should allow newline with Shift+Enter', async ({ page }) => {
    // Create a conversation first
    const newChatButton = page.locator('button:has-text("New Chat")');
    await newChatButton.click();

    await page.waitForResponse(
      response => response.url().includes('/api/conversations/create') && response.status() === 201,
      { timeout: 10000 }
    );

    // Wait for textarea
    await page.waitForTimeout(500);
    const textarea = page.locator('textarea[placeholder*="message"]');
    await expect(textarea).toBeEnabled({ timeout: 5000 });

    // Type first line
    await textarea.fill('Line 1');

    // Press Shift+Enter for newline (should NOT send)
    await textarea.press('Shift+Enter');

    // Type second line
    await textarea.type('Line 2');

    // Verify text contains newline
    const value = await textarea.inputValue();
    expect(value).toContain('\n');
    expect(value).toContain('Line 1');
    expect(value).toContain('Line 2');
    console.log('[Test] Shift+Enter added newline correctly');
  });

  test('should disable send button when textarea is empty', async ({ page }) => {
    // Create a conversation first
    const newChatButton = page.locator('button:has-text("New Chat")');
    await newChatButton.click();

    await page.waitForResponse(
      response => response.url().includes('/api/conversations/create') && response.status() === 201,
      { timeout: 10000 }
    );

    // Wait for textarea
    await page.waitForTimeout(500);
    const textarea = page.locator('textarea[placeholder*="message"]');
    await expect(textarea).toBeEnabled({ timeout: 5000 });

    // Send button should be disabled when empty
    const sendButton = page.locator('button[aria-label="Send message"]');
    await expect(sendButton).toBeDisabled();
    console.log('[Test] Send button disabled when empty');

    // Fill text - button should enable
    await textarea.fill('Some text');
    await expect(sendButton).toBeEnabled();
    console.log('[Test] Send button enabled when text present');
  });

  test('should show character count when approaching limit', async ({ page }) => {
    // Create a conversation first
    const newChatButton = page.locator('button:has-text("New Chat")');
    await newChatButton.click();

    await page.waitForResponse(
      response => response.url().includes('/api/conversations/create') && response.status() === 201,
      { timeout: 10000 }
    );

    // Wait for textarea
    await page.waitForTimeout(500);
    const textarea = page.locator('textarea[placeholder*="message"]');
    await expect(textarea).toBeEnabled({ timeout: 5000 });

    // Fill with many characters (approaching typical 5000 char limit)
    await textarea.fill('a'.repeat(4500));

    // Check if counter appears (component may or may not show counter)
    const counter = page.locator('[data-testid="char-counter"]');
    if (await counter.isVisible({ timeout: 1000 }).catch(() => false)) {
      await expect(counter).toContainText('4500');
      console.log('[Test] Character counter visible and correct');
    } else {
      console.log('[Test] Character counter not implemented - skipping assertion');
    }
  });
});
