/**
 * Sidebar Fresh Test - Using new server on port 5180
 */
import { test, expect } from '@playwright/test';

test('test against fresh server on 5180', async ({ page }) => {
	console.log('\n========== FRESH SERVER TEST (port 5180) ==========\n');

	// Capture console logs from the page
	const pageLogs: string[] = [];
	page.on('console', (msg) => {
		const text = msg.text();
		if (text.includes('[sidebar.ts]')) {
			pageLogs.push(text);
			console.log('[PAGE]', text);
		}
	});

	// Navigate to fresh server
	await page.goto('http://localhost:5180', { waitUntil: 'networkidle' });
	await page.waitForTimeout(1000);

	// Initial state
	const initial = await page.evaluate(() => {
		return {
			localStorage: localStorage.getItem('gpt-oss-sidebar-open'),
			sidebarWidth: window.getComputedStyle(
				document.querySelector('.history-sidebar') as HTMLElement
			).width
		};
	});
	console.log('Initial state:', JSON.stringify(initial, null, 2));

	// Click collapse button
	console.log('Clicking collapse button...');
	await page.locator('.collapse-btn').click();
	await page.waitForTimeout(500);

	// Check after toggle
	const afterToggle = await page.evaluate(() => {
		return {
			localStorage: localStorage.getItem('gpt-oss-sidebar-open'),
			sidebarWidth: window.getComputedStyle(
				document.querySelector('.history-sidebar') as HTMLElement
			).width
		};
	});
	console.log('After toggle:', JSON.stringify(afterToggle, null, 2));

	// Print page logs
	console.log('\n=== PAGE CONSOLE LOGS ===');
	if (pageLogs.length === 0) {
		console.log('(no sidebar.ts logs captured)');
	} else {
		pageLogs.forEach((log) => console.log(log));
	}
	console.log('=========================\n');

	// Verify
	const sidebarCollapsed = parseInt(afterToggle.sidebarWidth, 10) < 50;
	const localStorageUpdated = afterToggle.localStorage === 'false';

	console.log('Sidebar collapsed:', sidebarCollapsed);
	console.log('localStorage updated:', localStorageUpdated);

	expect(localStorageUpdated, 'localStorage should be "false" after toggle').toBe(true);
	expect(sidebarCollapsed, 'Sidebar should be collapsed (width < 50)').toBe(true);
});
