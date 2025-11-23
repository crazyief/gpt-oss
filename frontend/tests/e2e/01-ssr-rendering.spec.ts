import { test, expect } from '@playwright/test';

/**
 * SSR Rendering Tests
 *
 * Purpose: Verify server-side rendering works without errors
 *
 * WHY THIS TEST IS CRITICAL:
 * - SvelteKit renders pages server-side first
 * - Code accessing window/document during SSR will crash
 * - This test would have caught the SearchInput.svelte bug!
 *
 * What we test:
 * - Pages load without 500 errors
 * - No console errors during rendering
 * - Page content appears correctly
 */

test.describe('SSR Rendering', () => {
	test('homepage loads without SSR errors', async ({ page }) => {
		// Track console errors
		const consoleErrors: string[] = [];
		page.on('console', (msg) => {
			if (msg.type() === 'error') {
				consoleErrors.push(msg.text());
			}
		});

		// Load homepage - THIS WOULD HAVE CAUGHT THE window UNDEFINED BUG!
		const response = await page.goto('/');

		// Verify HTTP 200 (not 500)
		expect(response?.status()).toBe(200);

		// Verify no console errors
		expect(consoleErrors).toEqual([]);

		// Verify page title
		await expect(page).toHaveTitle(/GPT-OSS/);
	});

	test('page renders with correct structure', async ({ page }) => {
		await page.goto('/');

		// Wait for page to fully render
		await page.waitForLoadState('networkidle');

		// Verify main layout elements exist
		await expect(page.locator('body')).toBeVisible();

		// Verify no "500 Internal Error" text
		const bodyText = await page.textContent('body');
		expect(bodyText).not.toContain('500');
		expect(bodyText).not.toContain('Internal Error');
	});

	test('all critical components render without errors', async ({ page }) => {
		const consoleErrors: string[] = [];
		page.on('console', (msg) => {
			if (msg.type() === 'error') {
				consoleErrors.push(msg.text());
			}
		});

		await page.goto('/');
		await page.waitForLoadState('domcontentloaded');

		// Wait a bit for all components to mount
		await page.waitForTimeout(1000);

		// Check for common SSR errors
		expect(consoleErrors).toEqual([]);

		// Verify page is interactive (not stuck in error state)
		const isInteractive = await page.evaluate(() => {
			return document.readyState === 'complete';
		});
		expect(isInteractive).toBe(true);
	});

	test('window-dependent code only runs in browser', async ({ page }) => {
		// This test verifies our fix to the SearchInput bug
		const windowErrors: string[] = [];
		page.on('pageerror', (error) => {
			if (error.message.includes('window is not defined')) {
				windowErrors.push(error.message);
			}
		});

		await page.goto('/');
		await page.waitForLoadState('networkidle');

		// Should have zero "window is not defined" errors
		expect(windowErrors.length).toBe(0);
	});
});
