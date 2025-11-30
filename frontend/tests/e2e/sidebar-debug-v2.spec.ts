/**
 * Sidebar Debug V2 - Direct inspection
 *
 * NOTE: Uses baseURL from playwright config (5173) but we also test
 * the Docker container on 18173 to see if there's a difference.
 */
import { test, expect } from '@playwright/test';

test('direct localStorage inspection', async ({ page }) => {
	console.log('\n========== DIRECT LOCALSTORAGE TEST ==========\n');

	// Capture console logs from the page
	const pageLogs: string[] = [];
	page.on('console', (msg) => {
		const text = msg.text();
		if (text.includes('[sidebar.ts]')) {
			pageLogs.push(text);
			console.log('[PAGE]', text);
		}
	});

	// Use baseURL from config (5173) for fresh code from dev server
	await page.goto('/', { waitUntil: 'networkidle' });
	await page.waitForTimeout(1000);

	// Initial state
	const initial = await page.evaluate(() => {
		return {
			localStorage: localStorage.getItem('gpt-oss-sidebar-open'),
			keys: Object.keys(localStorage)
		};
	});
	console.log('Initial localStorage:', JSON.stringify(initial, null, 2));

	// Try setting localStorage directly
	await page.evaluate(() => {
		localStorage.setItem('gpt-oss-sidebar-open', 'test-value');
	});

	// Read it back
	const after = await page.evaluate(() => {
		return localStorage.getItem('gpt-oss-sidebar-open');
	});
	console.log('After direct set:', after);

	expect(after).toBe('test-value');

	// Now click collapse button
	console.log('Clicking collapse button...');
	await page.locator('.collapse-btn').click();
	await page.waitForTimeout(500);

	// Check if localStorage was updated by the store
	const afterToggle = await page.evaluate(() => {
		return {
			localStorage: localStorage.getItem('gpt-oss-sidebar-open'),
			sidebarWidth: window.getComputedStyle(
				document.querySelector('.history-sidebar') as HTMLElement
			).width
		};
	});
	console.log('After toggle:', JSON.stringify(afterToggle, null, 2));

	// Print all captured page logs
	console.log('\n=== PAGE CONSOLE LOGS ===');
	if (pageLogs.length === 0) {
		console.log('(no sidebar.ts logs captured - HMR may not have reloaded the module)');
	} else {
		pageLogs.forEach((log) => console.log(log));
	}
	console.log('=========================\n');

	// localStorage should now be 'false' (updated by the store)
	// If it's still 'test-value', the store is not saving to localStorage
	if (afterToggle.localStorage === 'test-value') {
		console.log('\n*** BUG: localStorage NOT updated by store toggle() ***\n');
	} else if (afterToggle.localStorage === 'false') {
		console.log('\n*** SUCCESS: localStorage updated to false by store ***\n');
	} else {
		console.log('\n*** UNEXPECTED: localStorage =', afterToggle.localStorage, '***\n');
	}

	// Verify sidebar collapsed OR localStorage updated (one of them should work)
	const sidebarCollapsed = parseInt(afterToggle.sidebarWidth, 10) < 50;
	const localStorageUpdated = afterToggle.localStorage === 'false';

	console.log('Sidebar collapsed:', sidebarCollapsed);
	console.log('localStorage updated:', localStorageUpdated);

	// At minimum, expect localStorage to be updated
	expect(localStorageUpdated, 'localStorage should be "false" after toggle').toBe(true);
});

test('verify browser constant is true', async ({ page }) => {
	console.log('\n========== VERIFY BROWSER CONSTANT ==========\n');

	await page.goto('/', { waitUntil: 'networkidle' });

	// Inject a console log to check if browser is accessible
	const result = await page.evaluate(() => {
		// Try to check if window is defined
		const hasWindow = typeof window !== 'undefined';
		const hasLocalStorage = typeof localStorage !== 'undefined';

		// Try to write and read localStorage
		const testKey = '__test_localStorage__';
		try {
			localStorage.setItem(testKey, 'test');
			const readBack = localStorage.getItem(testKey);
			localStorage.removeItem(testKey);
			return {
				hasWindow,
				hasLocalStorage,
				canReadWrite: readBack === 'test'
			};
		} catch (e) {
			return {
				hasWindow,
				hasLocalStorage,
				canReadWrite: false,
				error: String(e)
			};
		}
	});

	console.log('Browser environment check:', JSON.stringify(result, null, 2));

	expect(result.hasWindow).toBe(true);
	expect(result.hasLocalStorage).toBe(true);
	expect(result.canReadWrite).toBe(true);
});
