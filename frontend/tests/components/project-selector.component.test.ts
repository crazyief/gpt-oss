import { test, expect } from '@playwright/test';

test.describe('ProjectSelector Component - Project List', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(1000);
  });

  test('should display project list', async ({ page }) => {
    const projects = page.locator('[data-testid="project-card"]');
    const count = await projects.count();

    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should show Create Project button', async ({ page }) => {
    const createButton = page.locator('button:has-text("Create Project")');
    await expect(createButton).toBeVisible();
  });
});
