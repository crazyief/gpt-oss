/**
 * DocumentActions component tests
 *
 * Tests for document action buttons (download, delete)
 */

import { test, expect } from '@playwright/test';

test.describe('DocumentActions Component', () => {
	test.beforeEach(async ({ page }) => {
		// Navigate to component test page (this would need to be created)
		await page.goto('http://localhost:5173/test/document-actions');
	});

	test('should render download and delete buttons', async ({ page }) => {
		const downloadButton = page.locator('button[aria-label="Download document"]');
		const deleteButton = page.locator('button[aria-label="Delete document"]');

		await expect(downloadButton).toBeVisible();
		await expect(deleteButton).toBeVisible();
	});

	test('should emit download event when download button clicked', async ({ page }) => {
		const downloadButton = page.locator('button[aria-label="Download document"]');

		// Click download button
		await downloadButton.click();

		// Verify download event was emitted (would check via test harness)
		// This is a placeholder - actual implementation depends on test harness
		await expect(page.locator('[data-testid="event-log"]')).toContainText('download');
	});

	test('should emit delete event when delete button clicked', async ({ page }) => {
		const deleteButton = page.locator('button[aria-label="Delete document"]');

		// Click delete button
		await deleteButton.click();

		// Verify delete event was emitted (would check via test harness)
		await expect(page.locator('[data-testid="event-log"]')).toContainText('delete');
	});

	test('should show hover state on download button', async ({ page }) => {
		const downloadButton = page.locator('button[aria-label="Download document"]');

		// Hover over download button
		await downloadButton.hover();

		// Check that button has hover styling (color change)
		const color = await downloadButton.evaluate((el) => {
			return window.getComputedStyle(el).color;
		});

		// Expect color to be indigo (RGB values for indigo-500)
		expect(color).toContain('99, 102, 241');
	});

	test('should show hover state on delete button', async ({ page }) => {
		const deleteButton = page.locator('button[aria-label="Delete document"]');

		// Hover over delete button
		await deleteButton.hover();

		// Check that button has hover styling (color change to red)
		const color = await deleteButton.evaluate((el) => {
			return window.getComputedStyle(el).color;
		});

		// Expect color to be red (RGB values for red-500)
		expect(color).toContain('239, 68, 68');
	});

	test('should be keyboard accessible', async ({ page }) => {
		const downloadButton = page.locator('button[aria-label="Download document"]');

		// Tab to download button
		await page.keyboard.press('Tab');
		await expect(downloadButton).toBeFocused();

		// Press Enter to trigger download
		await page.keyboard.press('Enter');

		// Verify download event was emitted
		await expect(page.locator('[data-testid="event-log"]')).toContainText('download');
	});
});
