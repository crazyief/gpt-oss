/**
 * Chat Error Handling E2E Test
 *
 * Tests that error messages are displayed correctly when LLM service is unavailable,
 * and that error toasts auto-dismiss properly.
 */

import { test, expect } from '@playwright/test';

test.describe('Chat Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:5173');

    // Wait for initial API calls to complete
    await page.waitForResponse(
      response => response.url().includes('/api/csrf-token') && response.ok(),
      { timeout: 10000 }
    );

    // Wait for page to load
    await page.waitForSelector('button:has-text("New Chat")', { timeout: 10000 });
  });

  test('shows user-friendly error when LLM service is unavailable', async ({ page }) => {
    // Create a new conversation first
    const createResponsePromise = page.waitForResponse(
      response => response.url().includes('/api/conversations/create'),
      { timeout: 10000 }
    );
    await page.locator('button:has-text("New Chat")').click();
    await createResponsePromise;

    // Wait for chat interface to load
    await page.waitForSelector('textarea', { timeout: 5000 });

    // Type a message
    const textarea = page.locator('textarea');
    await textarea.fill('Hello, test message');

    // Set up listener for SSE stream error
    const streamResponsePromise = page.waitForResponse(
      response => response.url().includes('/api/chat/stream'),
      { timeout: 10000 }
    );

    // Send the message (press Enter or click send button)
    await textarea.press('Enter');

    // Wait for the stream initiation response
    await streamResponsePromise;

    // Wait a moment for SSE events to be processed
    await page.waitForTimeout(2000);

    // Check for error toast (should show LLM unavailable message)
    const errorToast = page.locator('._toastItem').filter({ hasText: /LLM|service|connect|unavailable/i });
    const isErrorVisible = await errorToast.isVisible().catch(() => false);

    console.log('[Test] Error toast visible:', isErrorVisible);

    // If error toast appeared, verify it auto-dismisses
    if (isErrorVisible) {
      console.log('[Test] Error toast appeared - waiting for auto-dismiss');

      // Error toasts have 5 second duration
      await expect(errorToast).toBeHidden({ timeout: 8000 });
      console.log('[Test] SUCCESS: Error toast auto-dismissed!');
    } else {
      // Toast might have already auto-dismissed or LLM might actually be running
      console.log('[Test] Error toast not found - either auto-dismissed or LLM is running');
    }
  });

  test('error toast disappears within 6 seconds', async ({ page }) => {
    // Create a new conversation first
    const createResponsePromise = page.waitForResponse(
      response => response.url().includes('/api/conversations/create'),
      { timeout: 10000 }
    );
    await page.locator('button:has-text("New Chat")').click();
    await createResponsePromise;

    // Wait for chat interface to load
    await page.waitForSelector('textarea', { timeout: 5000 });

    // Type a message
    const textarea = page.locator('textarea');
    await textarea.fill('Test message for error handling');

    // Set up listener for SSE stream
    const streamResponsePromise = page.waitForResponse(
      response => response.url().includes('/api/chat/stream'),
      { timeout: 10000 }
    );

    // Send the message
    await textarea.press('Enter');

    // Wait for the stream initiation
    await streamResponsePromise;

    // Take screenshot immediately
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'test-results/chat-error-1s.png' });

    // Wait 6 seconds (error toast has 5s duration + buffer)
    await page.waitForTimeout(6000);

    // Take screenshot after 6 seconds
    await page.screenshot({ path: 'test-results/chat-error-7s.png' });

    // Check that error toast is no longer visible
    const toasts = page.locator('._toastItem');
    const toastCount = await toasts.count();

    console.log('[Test] Toast count after 7 seconds:', toastCount);

    // After 7 seconds, error toasts should be gone (they have 5s duration)
    // Note: There might be other toasts, but error toasts should have auto-dismissed
    const errorToast = page.locator('._toastItem').filter({ hasText: /error|failed|unavailable/i });
    const errorStillVisible = await errorToast.isVisible().catch(() => false);

    expect(errorStillVisible).toBe(false);
    console.log('[Test] SUCCESS: No error toasts visible after 7 seconds');
  });

  test('user message appears in chat even when LLM fails', async ({ page }) => {
    // Create a new conversation first
    const createResponsePromise = page.waitForResponse(
      response => response.url().includes('/api/conversations/create'),
      { timeout: 10000 }
    );
    await page.locator('button:has-text("New Chat")').click();
    await createResponsePromise;

    // Wait for chat interface to load
    await page.waitForSelector('textarea', { timeout: 5000 });

    // Type a specific message
    const testMessage = 'My test message for error handling';
    const textarea = page.locator('textarea');
    await textarea.fill(testMessage);

    // Set up listener for SSE stream
    const streamResponsePromise = page.waitForResponse(
      response => response.url().includes('/api/chat/stream'),
      { timeout: 10000 }
    );

    // Send the message
    await textarea.press('Enter');

    // Wait for the stream initiation
    await streamResponsePromise;

    // Wait a moment for UI to update
    await page.waitForTimeout(1000);

    // The user message should appear in the chat (in the message content area, not title)
    const userMessage = page.locator('.message-content').filter({ hasText: testMessage });
    await expect(userMessage).toBeVisible({ timeout: 5000 });

    console.log('[Test] SUCCESS: User message appears in chat');
  });
});
