/**
 * ProjectSettings component tests
 *
 * Tests for project editing and deletion functionality
 */

import { test, expect } from '@playwright/test';

test.describe('ProjectSettings Component', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('http://localhost:5173/test/project-settings');
	});

	test('should render project settings form', async ({ page }) => {
		await expect(page.locator('h2')).toContainText('Project Settings');
		await expect(page.locator('#project-name')).toBeVisible();
		await expect(page.locator('#project-description')).toBeVisible();
	});

	test('should populate form with project data', async ({ page }) => {
		const nameInput = page.locator('#project-name');
		const descriptionInput = page.locator('#project-description');

		// Verify initial values (from test data)
		await expect(nameInput).toHaveValue('Test Project');
		await expect(descriptionInput).toHaveValue('Test Description');
	});

	test('should enable save button when changes made', async ({ page }) => {
		const nameInput = page.locator('#project-name');
		const saveButton = page.locator('button[type="submit"]');

		// Initially disabled (no changes)
		await expect(saveButton).toBeDisabled();

		// Make a change
		await nameInput.fill('Updated Project Name');

		// Now enabled
		await expect(saveButton).toBeEnabled();
	});

	test('should disable save button when no changes', async ({ page }) => {
		const saveButton = page.locator('button[type="submit"]');

		// No changes made
		await expect(saveButton).toBeDisabled();
	});

	test('should disable save button when name is empty', async ({ page }) => {
		const nameInput = page.locator('#project-name');
		const saveButton = page.locator('button[type="submit"]');

		// Clear name
		await nameInput.fill('');

		// Save button should be disabled
		await expect(saveButton).toBeDisabled();
	});

	test('should show character count for description', async ({ page }) => {
		const descriptionInput = page.locator('#project-description');
		const charCount = page.locator('.char-count');

		// Initial count
		await expect(charCount).toContainText('16/1000'); // "Test Description" = 16 chars

		// Type more text
		await descriptionInput.fill('A longer description for testing purposes');

		// Updated count
		await expect(charCount).toContainText('43/1000');
	});

	test('should emit save event when form submitted', async ({ page }) => {
		const nameInput = page.locator('#project-name');
		const saveButton = page.locator('button[type="submit"]');

		// Make a change
		await nameInput.fill('Updated Project Name');

		// Submit form
		await saveButton.click();

		// Verify save event was emitted (via test harness)
		await expect(page.locator('[data-testid="event-log"]')).toContainText('save');
	});

	test('should reset form when cancel clicked', async ({ page }) => {
		const nameInput = page.locator('#project-name');
		const cancelButton = page.locator('button.button-cancel');

		// Original value
		const originalName = await nameInput.inputValue();

		// Make a change
		await nameInput.fill('Changed Name');

		// Cancel
		await cancelButton.click();

		// Should revert to original
		await expect(nameInput).toHaveValue(originalName);
	});

	test('should render danger zone', async ({ page }) => {
		const dangerZone = page.locator('.danger-zone');
		await expect(dangerZone).toBeVisible();
		await expect(dangerZone).toContainText('Delete Project');
	});

	test('should open delete confirmation modal', async ({ page }) => {
		const deleteButton = page.locator('button.button-delete');

		// Click delete button
		await deleteButton.click();

		// Modal should appear
		const modal = page.locator('[role="dialog"]');
		await expect(modal).toBeVisible();
		await expect(modal).toContainText('Delete Project');
	});

	test('should require typing project name to confirm deletion', async ({ page }) => {
		const deleteButton = page.locator('button.button-delete');

		// Open modal
		await deleteButton.click();

		// Confirm button should be disabled initially
		const confirmButton = page.locator('button.button-confirm');
		await expect(confirmButton).toBeDisabled();

		// Type project name
		const confirmInput = page.locator('#confirm-input');
		await confirmInput.fill('Test Project');

		// Confirm button should be enabled
		await expect(confirmButton).toBeEnabled();
	});

	test('should close modal when cancel clicked', async ({ page }) => {
		const deleteButton = page.locator('button.button-delete');

		// Open modal
		await deleteButton.click();

		// Click cancel
		const cancelButton = page.locator('.modal-footer button.button-cancel');
		await cancelButton.click();

		// Modal should be closed
		const modal = page.locator('[role="dialog"]');
		await expect(modal).not.toBeVisible();
	});

	test('should emit delete event when confirmed', async ({ page }) => {
		const deleteButton = page.locator('button.button-delete');

		// Open modal
		await deleteButton.click();

		// Type project name
		const confirmInput = page.locator('#confirm-input');
		await confirmInput.fill('Test Project');

		// Confirm deletion
		const confirmButton = page.locator('button.button-confirm');
		await confirmButton.click();

		// Verify delete event was emitted
		await expect(page.locator('[data-testid="event-log"]')).toContainText('delete');
	});

	test('should close modal with Escape key', async ({ page }) => {
		const deleteButton = page.locator('button.button-delete');

		// Open modal
		await deleteButton.click();

		// Press Escape
		await page.keyboard.press('Escape');

		// Modal should be closed
		const modal = page.locator('[role="dialog"]');
		await expect(modal).not.toBeVisible();
	});
});
