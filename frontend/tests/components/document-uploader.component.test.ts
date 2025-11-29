/**
 * DocumentUploader component tests
 *
 * Tests for drag-and-drop file upload functionality
 */

import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('DocumentUploader Component', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('http://localhost:5173/test/document-uploader');
	});

	test('should render upload zone', async ({ page }) => {
		const uploadZone = page.locator('[role="button"][aria-label="Upload documents"]');
		await expect(uploadZone).toBeVisible();
		await expect(uploadZone).toContainText('Drag and drop files or click to browse');
	});

	test('should show file type and size constraints', async ({ page }) => {
		const uploadZone = page.locator('.upload-zone');
		await expect(uploadZone).toContainText('Supported: .pdf, .docx, .xlsx, .txt, .md');
		await expect(uploadZone).toContainText('max 200MB per file');
	});

	test('should open file picker when clicked', async ({ page }) => {
		const uploadZone = page.locator('[role="button"][aria-label="Upload documents"]');

		// Set up file chooser listener
		const [fileChooser] = await Promise.all([
			page.waitForEvent('filechooser'),
			uploadZone.click()
		]);

		expect(fileChooser).toBeTruthy();
	});

	test('should handle file selection via picker', async ({ page }) => {
		const uploadZone = page.locator('[role="button"][aria-label="Upload documents"]');

		// Create a test file
		const testFilePath = path.join(__dirname, '../fixtures/test-document.pdf');

		// Select file via file picker
		const [fileChooser] = await Promise.all([
			page.waitForEvent('filechooser'),
			uploadZone.click()
		]);

		await fileChooser.setFiles(testFilePath);

		// Wait for upload to start
		await expect(page.locator('.progress-container')).toBeVisible({ timeout: 5000 });
	});

	test('should show drag state when dragging over', async ({ page }) => {
		const uploadZone = page.locator('.upload-zone');

		// Simulate drag enter
		await uploadZone.dispatchEvent('dragenter');

		// Check for dragging class
		await expect(uploadZone).toHaveClass(/dragging/);
		await expect(uploadZone).toContainText('Drop files here');
	});

	test('should show progress bar during upload', async ({ page }) => {
		const uploadZone = page.locator('[role="button"][aria-label="Upload documents"]');
		const testFilePath = path.join(__dirname, '../fixtures/test-document.pdf');

		const [fileChooser] = await Promise.all([
			page.waitForEvent('filechooser'),
			uploadZone.click()
		]);

		await fileChooser.setFiles(testFilePath);

		// Wait for progress bar
		const progressBar = page.locator('.progress-bar-fill');
		await expect(progressBar).toBeVisible({ timeout: 5000 });
	});

	test('should validate file type', async ({ page }) => {
		const uploadZone = page.locator('[role="button"][aria-label="Upload documents"]');

		// Try to upload invalid file type (.exe)
		const invalidFilePath = path.join(__dirname, '../fixtures/invalid-file.exe');

		const [fileChooser] = await Promise.all([
			page.waitForEvent('filechooser'),
			uploadZone.click()
		]);

		await fileChooser.setFiles(invalidFilePath);

		// Should show error toast
		await expect(page.locator('.toast-error')).toBeVisible({ timeout: 2000 });
		await expect(page.locator('.toast-error')).toContainText('File type not allowed');
	});

	test('should validate file size', async ({ page }) => {
		// Test would require a large file fixture (>200MB)
		// Skipped in this demo but pattern would be:
		// 1. Create/select large file
		// 2. Attempt upload
		// 3. Verify error toast shows "File too large"
	});

	test('should handle multiple file selection', async ({ page }) => {
		const uploadZone = page.locator('[role="button"][aria-label="Upload documents"]');

		const testFiles = [
			path.join(__dirname, '../fixtures/test-document.pdf'),
			path.join(__dirname, '../fixtures/test-document.txt')
		];

		const [fileChooser] = await Promise.all([
			page.waitForEvent('filechooser'),
			uploadZone.click()
		]);

		await fileChooser.setFiles(testFiles);

		// Should show progress for both files
		const progressItems = page.locator('.progress-item');
		await expect(progressItems).toHaveCount(2, { timeout: 5000 });
	});

	test('should emit upload event on success', async ({ page }) => {
		const uploadZone = page.locator('[role="button"][aria-label="Upload documents"]');
		const testFilePath = path.join(__dirname, '../fixtures/test-document.pdf');

		const [fileChooser] = await Promise.all([
			page.waitForEvent('filechooser'),
			uploadZone.click()
		]);

		await fileChooser.setFiles(testFilePath);

		// Wait for upload to complete
		await expect(page.locator('.progress-bar-fill')).toHaveCSS('width', '100%', {
			timeout: 10000
		});

		// Verify success toast
		await expect(page.locator('.toast-success')).toBeVisible({ timeout: 2000 });
	});
});
