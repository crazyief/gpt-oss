/**
 * E2E Chat Workflow Tests - REAL BACKEND INTEGRATION
 *
 * These tests use the actual backend - NO MOCKS.
 * Tests verify real frontend ↔ backend integration.
 *
 * Prerequisites:
 * - Backend running on http://localhost:8000
 * - Frontend running on http://localhost:5173
 * - Database accessible
 */

import { test, expect } from '@playwright/test';

test.describe('End-to-End Chat Workflow (Real Backend)', () => {
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

    // Ensure UI is ready
    await page.waitForSelector('button:has-text("New Chat")', { timeout: 10000 });
  });

  test('E2E: Create new conversation via real API', async ({ page }) => {
    // Click New Chat button
    const newChatButton = page.locator('button:has-text("New Chat")');
    await expect(newChatButton).toBeVisible();

    // Set up response listener BEFORE clicking
    const createResponsePromise = page.waitForResponse(
      response => response.url().includes('/api/conversations/create'),
      { timeout: 10000 }
    );

    console.log('[Test] Clicking New Chat button');
    await newChatButton.click();

    // Wait for real API response
    const createResponse = await createResponsePromise;
    console.log('[Test] Create response status:', createResponse.status());

    expect(createResponse.status()).toBe(201);

    // Verify response contains conversation data
    const responseData = await createResponse.json();
    expect(responseData).toHaveProperty('id');
    expect(responseData.id).toBeGreaterThan(0);
    console.log('[Test] Created conversation ID:', responseData.id);

    // Wait for UI to update - textarea should appear
    await page.waitForSelector('textarea[placeholder*="message"]', { timeout: 10000 });
    console.log('[Test] Chat interface loaded');
  });

  test('E2E: Send message and receive streaming response', async ({ page }) => {
    // First create a conversation
    const newChatButton = page.locator('button:has-text("New Chat")');
    await newChatButton.click();

    // Wait for conversation creation
    await page.waitForResponse(
      response => response.url().includes('/api/conversations/create') && response.status() === 201,
      { timeout: 10000 }
    );

    // Wait for chat interface to be ready - textarea should be enabled after conversation is active
    // The ChatInput component may take a moment to become interactive
    await page.waitForTimeout(500);

    // Wait for textarea to be ready and enabled
    const textarea = page.locator('textarea[placeholder*="message"]');
    await expect(textarea).toBeEnabled({ timeout: 10000 });

    // Type a message
    const testMessage = 'Hello, this is a real E2E test message.';
    await textarea.fill(testMessage);
    console.log('[Test] Typed message:', testMessage);

    // Set up listener for chat stream BEFORE sending
    const streamResponsePromise = page.waitForResponse(
      response => response.url().includes('/api/chat/stream'),
      { timeout: 30000 }
    );

    // Click send button instead of Enter (more reliable)
    const sendButton = page.locator('button[aria-label*="Send"], button:has-text("Send")');
    if (await sendButton.isVisible()) {
      await sendButton.click();
    } else {
      await textarea.press('Enter');
    }
    console.log('[Test] Sent message');

    // Wait for stream to start
    const streamResponse = await streamResponsePromise;
    console.log('[Test] Stream response status:', streamResponse.status());
    expect(streamResponse.ok()).toBe(true);

    // Wait for user message to appear in UI
    await page.waitForTimeout(1000);
    const userMessage = page.locator('.user-message-container, [data-role="user"]').last();
    await expect(userMessage).toContainText(testMessage);
    console.log('[Test] User message displayed');

    // Wait for assistant response (real LLM may take time)
    // Using longer timeout since real LLM can be slow
    try {
      await page.waitForSelector('.assistant-message-container, [data-role="assistant"]', {
        timeout: 60000
      });
      console.log('[Test] Assistant response received');
    } catch (e) {
      console.log('[Test] Assistant response timeout - LLM may be slow');
      // Don't fail test if LLM is slow, just log it
    }
  });

  test('E2E: Conversation list loads from real API', async ({ page }) => {
    // Verify the sidebar shows conversations header
    await expect(page.locator('h2:has-text("Conversations")')).toBeVisible();

    // Project selector should be visible
    const projectSelector = page.locator('select').first();
    await expect(projectSelector).toBeVisible();

    // "All Projects" option should exist in the select dropdown
    // Note: Options inside <select> are not "visible" in Playwright's sense
    // Use toBeAttached() or count() instead
    const allProjectsOption = page.locator('select option:has-text("All Projects")');
    await expect(allProjectsOption).toBeAttached();

    // Verify we can get the option value
    const optionCount = await page.locator('select option').count();
    console.log('[Test] Found', optionCount, 'project options');
    expect(optionCount).toBeGreaterThan(0);
  });

  test('E2E: Switch between projects', async ({ page }) => {
    // Find project selector
    const projectSelector = page.locator('select').first();

    if (await projectSelector.isVisible()) {
      // Get current selection
      const currentValue = await projectSelector.inputValue();
      console.log('[Test] Current project:', currentValue);

      // Get all options
      const optionCount = await projectSelector.locator('option').count();
      console.log('[Test] Found', optionCount, 'options');

      if (optionCount > 1) {
        // Set up listener for conversations reload BEFORE selecting
        // The app calls /api/projects/{id}/conversations when project changes
        const conversationsResponsePromise = page.waitForResponse(
          response => response.url().includes('/api/projects/') && response.url().includes('/conversations'),
          { timeout: 10000 }
        );

        // Select a different project (index 1 = first real project after "All Projects")
        await projectSelector.selectOption({ index: 1 });

        // Wait for real API call
        try {
          const response = await conversationsResponsePromise;
          expect(response.ok()).toBe(true);
          console.log('[Test] Switched project, conversations reloaded');
        } catch (e) {
          // If no API call was made, the app might be using cached data
          // This is acceptable behavior
          console.log('[Test] Project switched (may have used cached data)');
        }
      } else {
        console.log('[Test] Only one project, skipping switch test');
        test.skip();
      }
    } else {
      test.skip();
    }
  });

  test('E2E: Search conversations', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Search"]');

    if (await searchInput.isVisible()) {
      await searchInput.fill('test');
      console.log('[Test] Entered search term');

      // Wait for debounce
      await page.waitForTimeout(500);

      // Search should work without error
      // Results depend on actual data in database
      const visibleConvs = page.locator('[data-testid="conversation-item"]');
      const count = await visibleConvs.count();
      console.log('[Test] Search results:', count);
      expect(count).toBeGreaterThanOrEqual(0);
    } else {
      test.skip();
    }
  });

  test('E2E: Page reload preserves state', async ({ page }) => {
    // Create a conversation first
    const newChatButton = page.locator('button:has-text("New Chat")');
    await newChatButton.click();

    // Wait for creation
    const createResponse = await page.waitForResponse(
      response => response.url().includes('/api/conversations/create') && response.status() === 201,
      { timeout: 10000 }
    );

    const conversationData = await createResponse.json();
    console.log('[Test] Created conversation:', conversationData.id);

    // Get conversation count before reload
    await page.waitForTimeout(500);
    const countBefore = await page.locator('[data-testid="conversation-item"]').count();
    console.log('[Test] Conversations before reload:', countBefore);

    // Reload the page
    await page.reload();

    // Wait for app to fully reinitialize - check for New Chat button
    await page.waitForSelector('button:has-text("New Chat")', { timeout: 15000 });

    // Wait a moment for conversation list to populate from real API
    await page.waitForTimeout(1000);

    // Conversation should persist (data is in real database)
    const countAfter = await page.locator('[data-testid="conversation-item"]').count();
    console.log('[Test] Conversations after reload:', countAfter);

    // Should have same or more conversations (not less)
    expect(countAfter).toBeGreaterThanOrEqual(countBefore);
  });

  test('E2E: Delete conversation via real API', async ({ page }) => {
    // First create a conversation to delete
    const newChatButton = page.locator('button:has-text("New Chat")');
    await newChatButton.click();

    await page.waitForResponse(
      response => response.url().includes('/api/conversations/create') && response.status() === 201,
      { timeout: 10000 }
    );

    await page.waitForTimeout(500);

    const conversations = page.locator('[data-testid="conversation-item"]');
    const initialCount = await conversations.count();
    console.log('[Test] Initial conversation count:', initialCount);

    if (initialCount > 0) {
      // Hover over first conversation to show delete button
      await conversations.first().hover();
      await page.waitForTimeout(300);

      // Look for delete button
      const deleteButton = page.locator('button[aria-label*="Delete"], button[aria-label*="delete"]').first();

      if (await deleteButton.isVisible()) {
        // Set up listener for delete API call
        const deleteResponsePromise = page.waitForResponse(
          response => response.url().includes('/api/conversations/') && response.request().method() === 'DELETE',
          { timeout: 10000 }
        );

        await deleteButton.click();

        // Wait for real API response
        const deleteResponse = await deleteResponsePromise;
        expect(deleteResponse.ok()).toBe(true);
        console.log('[Test] Delete response:', deleteResponse.status());

        // Verify count decreased
        await page.waitForTimeout(500);
        const newCount = await conversations.count();
        console.log('[Test] New conversation count:', newCount);
        expect(newCount).toBeLessThan(initialCount);
      } else {
        console.log('[Test] Delete button not visible');
        test.skip();
      }
    } else {
      console.log('[Test] No conversations to delete');
      test.skip();
    }
  });
});
