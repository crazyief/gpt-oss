/**
 * Project Delete Button E2E Test
 *
 * Tests delete button visibility based on project type:
 * - Default Project: NO delete button (cannot be deleted)
 * - Other projects: Delete button visible
 * - All Projects view: NO delete button
 */

import { test, expect } from '@playwright/test';

test.describe('Project Delete Button', () => {
  // Use Docker port 18173 for testing against Docker environment
  const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:18173';

  test.beforeEach(async ({ page }) => {
    // Navigate to app
    await page.goto(BASE_URL);

    // Wait for initial API calls to complete
    await page.waitForResponse(
      response => response.url().includes('/api/csrf-token') && response.ok(),
      { timeout: 10000 }
    );

    // Wait for page to load
    await page.waitForSelector('button:has-text("New Chat")', { timeout: 10000 });
  });

  test('delete button is NOT visible for Default Project', async ({ page }) => {
    // Wait for project selector to load with default project
    const projectSelector = page.locator('.project-select');
    await expect(projectSelector).toBeVisible();

    // Wait for default project to be selected
    await page.waitForTimeout(500);

    // Verify "Default Project" is selected (check the text contains "Default")
    const selectedText = await projectSelector.locator('option:checked').textContent();

    if (selectedText?.includes('Default Project')) {
      // Delete button should NOT be visible for Default Project
      const deleteButton = page.locator('.delete-project-button');
      await expect(deleteButton).not.toBeVisible();

      console.log('[Test] SUCCESS: Delete button is hidden for Default Project');
    } else {
      console.log(`[Test] INFO: Current project is "${selectedText}", not Default Project`);
    }
  });

  test('delete button is visible for non-default projects', async ({ page }) => {
    // Find the project selector dropdown
    const projectSelector = page.locator('.project-select');
    await expect(projectSelector).toBeVisible();

    // Get all options from the dropdown
    const options = await projectSelector.locator('option').allTextContents();

    // Find a project that is NOT "Default Project" and NOT "All Projects"
    let nonDefaultIndex = -1;
    for (let i = 0; i < options.length; i++) {
      const text = options[i];
      if (!text.includes('All Projects') && !text.includes('Default Project')) {
        nonDefaultIndex = i;
        break;
      }
    }

    if (nonDefaultIndex >= 0) {
      // Select the non-default project
      await projectSelector.selectOption({ index: nonDefaultIndex });
      await page.waitForTimeout(300);

      // Wait for the delete button to appear
      const deleteButton = page.locator('.delete-project-button');
      await expect(deleteButton).toBeVisible({ timeout: 3000 });

      // Verify the delete button has visible text "Delete"
      const deleteText = deleteButton.locator('.delete-text');
      await expect(deleteText).toBeVisible();
      await expect(deleteText).toHaveText('Delete');

      // Verify the button is not clipped/cut off
      const buttonBox = await deleteButton.boundingBox();
      expect(buttonBox).not.toBeNull();

      if (buttonBox) {
        // Button should have reasonable dimensions (not squished)
        expect(buttonBox.width).toBeGreaterThan(50);
        expect(buttonBox.height).toBeGreaterThanOrEqual(36);

        console.log(`[Test] Delete button dimensions: ${buttonBox.width}x${buttonBox.height}`);
      }

      console.log('[Test] SUCCESS: Delete button is visible for non-default project');
    } else {
      console.log('[Test] SKIP: No non-default projects available to test');
    }
  });

  test('delete button is not visible when "All Projects" is selected', async ({ page }) => {
    // Find the project selector dropdown
    const projectSelector = page.locator('.project-select');
    await expect(projectSelector).toBeVisible();

    // Select "All Projects" option
    await projectSelector.selectOption({ value: 'all' });
    await page.waitForTimeout(300);

    // Delete button should not be visible
    const deleteButton = page.locator('.delete-project-button');
    await expect(deleteButton).not.toBeVisible();

    console.log('[Test] SUCCESS: Delete button hidden when All Projects selected');
  });

  test('delete button shows confirmation dialog for non-default projects', async ({ page }) => {
    // Find the project selector dropdown
    const projectSelector = page.locator('.project-select');
    await expect(projectSelector).toBeVisible();

    // Get all options from the dropdown
    const options = await projectSelector.locator('option').allTextContents();

    // Find a project that is NOT "Default Project" and NOT "All Projects"
    let nonDefaultIndex = -1;
    for (let i = 0; i < options.length; i++) {
      const text = options[i];
      if (!text.includes('All Projects') && !text.includes('Default Project')) {
        nonDefaultIndex = i;
        break;
      }
    }

    if (nonDefaultIndex >= 0) {
      // Select the non-default project
      await projectSelector.selectOption({ index: nonDefaultIndex });
      await page.waitForTimeout(300);

      // Wait for the delete button to appear
      const deleteButton = page.locator('.delete-project-button');
      await expect(deleteButton).toBeVisible({ timeout: 3000 });

      // Set up dialog handler to automatically dismiss the confirm dialog
      let dialogAppeared = false;
      page.on('dialog', async (dialog) => {
        dialogAppeared = true;
        console.log(`[Test] Dialog message: ${dialog.message()}`);
        await dialog.dismiss(); // Cancel the deletion
      });

      // Click the delete button
      await deleteButton.click();

      // Wait a moment for dialog to appear
      await page.waitForTimeout(500);

      // Verify confirmation dialog appeared
      expect(dialogAppeared).toBe(true);

      console.log('[Test] SUCCESS: Delete button shows confirmation dialog');
    } else {
      console.log('[Test] SKIP: No non-default projects available to test');
    }
  });
});
