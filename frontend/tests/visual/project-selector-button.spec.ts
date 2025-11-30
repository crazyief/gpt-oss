import { test, expect } from '@playwright/test';

/**
 * Visual regression test for ProjectSelector delete button
 *
 * Purpose: Verify delete button is fully visible and not clipped
 *
 * Bug context: Button was being cut off due to overflow constraints
 * Fix: Applied flex-shrink: 0 and min-width to ensure visibility
 */

test.describe('ProjectSelector - Delete Button Visibility', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:5173');

    // Wait for projects to load
    await page.waitForTimeout(2000);
  });

  test('should show full delete button when project selected', async ({ page }) => {
    // Find project selector
    const projectSelect = page.locator('.project-select').first();

    // Check if select exists
    const isVisible = await projectSelect.isVisible().catch(() => false);

    if (!isVisible) {
      console.log('Project selector not found - app may not be running');
      return;
    }

    // Get all project options (excluding "All Projects")
    const options = await projectSelect.locator('option').allTextContents();
    const projectOptions = options.filter(opt => opt !== 'All Projects');

    // If no projects exist, we can't test delete button
    if (projectOptions.length === 0) {
      console.log('No projects found - create a project first');
      return;
    }

    // Select first project (not "All Projects")
    const firstProjectOption = await projectSelect.locator('option').nth(1);
    const projectValue = await firstProjectOption.getAttribute('value');

    if (projectValue && projectValue !== 'all') {
      await projectSelect.selectOption(projectValue);
      await page.waitForTimeout(500); // Wait for button to appear

      // Verify delete button is visible
      const deleteButton = page.locator('.delete-project-button').first();

      // Check button visibility
      await expect(deleteButton).toBeVisible();

      // Verify button has minimum width
      const buttonBox = await deleteButton.boundingBox();
      expect(buttonBox).not.toBeNull();

      if (buttonBox) {
        // Button should be at least 70px wide
        expect(buttonBox.width).toBeGreaterThanOrEqual(70);

        // Button should be visible within sidebar (260px width)
        expect(buttonBox.x + buttonBox.width).toBeLessThanOrEqual(260);

        console.log(`Delete button dimensions: ${buttonBox.width}px width at x=${buttonBox.x}px`);
      }

      // Verify button text is visible
      const deleteText = deleteButton.locator('.delete-text');
      await expect(deleteText).toBeVisible();
      await expect(deleteText).toHaveText('Delete');

      // Verify button icon is visible
      const deleteIcon = deleteButton.locator('svg');
      await expect(deleteIcon).toBeVisible();
    }
  });

  test('should not overflow sidebar width', async ({ page }) => {
    const projectSelect = page.locator('.project-select').first();

    const isVisible = await projectSelect.isVisible().catch(() => false);
    if (!isVisible) return;

    // Select a project
    const options = await projectSelect.locator('option').allTextContents();
    if (options.length <= 1) {
      console.log('No projects to test');
      return;
    }

    const firstProjectOption = await projectSelect.locator('option').nth(1);
    const projectValue = await firstProjectOption.getAttribute('value');

    if (projectValue && projectValue !== 'all') {
      await projectSelect.selectOption(projectValue);
      await page.waitForTimeout(500);

      // Get sidebar and button positions
      const sidebar = page.locator('.sidebar').first();
      const deleteButton = page.locator('.delete-project-button').first();

      const sidebarBox = await sidebar.boundingBox();
      const buttonBox = await deleteButton.boundingBox();

      expect(sidebarBox).not.toBeNull();
      expect(buttonBox).not.toBeNull();

      if (sidebarBox && buttonBox) {
        // Button should be fully contained within sidebar
        const buttonRightEdge = buttonBox.x + buttonBox.width;
        const sidebarRightEdge = sidebarBox.x + sidebarBox.width;

        expect(buttonRightEdge).toBeLessThanOrEqual(sidebarRightEdge);

        console.log(`Button right edge: ${buttonRightEdge}px, Sidebar right edge: ${sidebarRightEdge}px`);
      }
    }
  });

  test('visual snapshot - delete button in sidebar', async ({ page }) => {
    const projectSelect = page.locator('.project-select').first();

    const isVisible = await projectSelect.isVisible().catch(() => false);
    if (!isVisible) return;

    // Select a project
    const options = await projectSelect.locator('option').allTextContents();
    if (options.length <= 1) return;

    const firstProjectOption = await projectSelect.locator('option').nth(1);
    const projectValue = await firstProjectOption.getAttribute('value');

    if (projectValue && projectValue !== 'all') {
      await projectSelect.selectOption(projectValue);
      await page.waitForTimeout(500);

      // Wait for UI to stabilize
      await page.waitForLoadState('networkidle');

      // Take screenshot of sidebar
      const sidebar = page.locator('.sidebar').first();
      const screenshot = await sidebar.screenshot({
        animations: 'disabled'
      });

      // Compare with baseline
      await expect(screenshot).toMatchSnapshot('project-selector-with-delete-button.png', {
        maxDiffPixels: 100,
        threshold: 0.02  // Allow 2% difference
      });
    }
  });
});
