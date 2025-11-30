/**
 * Sidebar Debug Test
 *
 * Purpose: Diagnose why sidebar is not appearing when clicking Chat icon
 *
 * This test will:
 * 1. Navigate to the app
 * 2. Check localStorage state
 * 3. Click on Chat tab
 * 4. Verify sidebar visibility via CSS computed width
 * 5. Report detailed diagnostic information
 */
import { test, expect } from '@playwright/test';

test.describe('Sidebar Visibility Debug', () => {
	// Use longer timeout for debugging
	test.setTimeout(60000);

	test('should diagnose sidebar visibility issue', async ({ page }) => {
		// Enable console logging to capture any JS errors
		const consoleLogs: string[] = [];
		const consoleErrors: string[] = [];
		page.on('console', (msg) => {
			if (msg.type() === 'error') {
				consoleErrors.push(msg.text());
			} else {
				consoleLogs.push(`[${msg.type()}] ${msg.text()}`);
			}
		});

		console.log('\n========== SIDEBAR DEBUG TEST ==========\n');

		// Step 1: Navigate to the app
		console.log('Step 1: Navigating to http://localhost:18173...');
		await page.goto('http://localhost:18173', { waitUntil: 'networkidle' });

		// Wait for app to fully load
		await page.waitForLoadState('domcontentloaded');
		await page.waitForTimeout(1000); // Extra wait for Svelte hydration

		// Step 2: Check localStorage state BEFORE any interaction
		console.log('\nStep 2: Checking localStorage state (before interaction)...');
		const localStorageBefore = await page.evaluate(() => {
			return {
				sidebarOpen: localStorage.getItem('gpt-oss-sidebar-open'),
				allKeys: Object.keys(localStorage)
			};
		});
		console.log('localStorage before interaction:', JSON.stringify(localStorageBefore, null, 2));

		// Step 3: Check which tab is currently active
		console.log('\nStep 3: Checking current active tab...');
		const activeTabBefore = await page.evaluate(() => {
			const chatTab = document.querySelector('#chat-tab');
			const chatTabPanel = document.querySelector('#chat-panel');
			return {
				chatTabAriaSelected: chatTab?.getAttribute('aria-selected'),
				chatPanelExists: !!chatTabPanel,
				activeTabClass: chatTab?.classList.contains('active')
			};
		});
		console.log('Active tab state before click:', JSON.stringify(activeTabBefore, null, 2));

		// Step 4: Check if ChatTab component is rendered
		console.log('\nStep 4: Checking if ChatTab is rendered...');
		const chatTabState = await page.evaluate(() => {
			const chatTab = document.querySelector('.chat-tab');
			const historySidebar = document.querySelector('.history-sidebar');
			const chatMain = document.querySelector('.chat-main');
			return {
				chatTabExists: !!chatTab,
				chatTabClasses: chatTab?.className || 'NOT FOUND',
				historySidebarExists: !!historySidebar,
				chatMainExists: !!chatMain
			};
		});
		console.log('ChatTab render state:', JSON.stringify(chatTabState, null, 2));

		// Step 5: Check sidebar CSS computed styles
		console.log('\nStep 5: Checking sidebar CSS computed styles...');
		const sidebarStyles = await page.evaluate(() => {
			const sidebar = document.querySelector('.history-sidebar') as HTMLElement;
			if (!sidebar) {
				return { error: 'Sidebar element not found!' };
			}
			const computed = window.getComputedStyle(sidebar);
			return {
				width: computed.width,
				display: computed.display,
				visibility: computed.visibility,
				opacity: computed.opacity,
				overflow: computed.overflow,
				position: computed.position,
				left: computed.left,
				transform: computed.transform,
				parentClass: sidebar.parentElement?.className || 'unknown'
			};
		});
		console.log('Sidebar computed styles:', JSON.stringify(sidebarStyles, null, 2));

		// Step 6: Check if parent has sidebar-collapsed class
		console.log('\nStep 6: Checking if parent has sidebar-collapsed class...');
		const parentClassState = await page.evaluate(() => {
			const chatTab = document.querySelector('.chat-tab');
			return {
				className: chatTab?.className || 'NOT FOUND',
				hasSidebarCollapsed: chatTab?.classList.contains('sidebar-collapsed'),
				dataset: (chatTab as HTMLElement)?.dataset || {}
			};
		});
		console.log('Parent class state:', JSON.stringify(parentClassState, null, 2));

		// Step 7: Click on Chat tab in navigation
		console.log('\nStep 7: Clicking Chat tab in VerticalNav...');
		const chatNavButton = page.locator('#chat-tab');
		await expect(chatNavButton).toBeVisible();
		await chatNavButton.click();
		await page.waitForTimeout(500); // Wait for state updates

		// Step 8: Check localStorage after click
		console.log('\nStep 8: Checking localStorage after click...');
		const localStorageAfter = await page.evaluate(() => {
			return localStorage.getItem('gpt-oss-sidebar-open');
		});
		console.log('localStorage after click:', localStorageAfter);

		// Step 9: Check sidebar visibility after click
		console.log('\nStep 9: Checking sidebar after click...');
		const sidebarAfterClick = await page.evaluate(() => {
			const sidebar = document.querySelector('.history-sidebar') as HTMLElement;
			const chatTab = document.querySelector('.chat-tab');
			if (!sidebar || !chatTab) {
				return { error: 'Elements not found after click!' };
			}
			const computed = window.getComputedStyle(sidebar);
			return {
				sidebarWidth: computed.width,
				parentClasses: chatTab.className,
				hasSidebarCollapsed: chatTab.classList.contains('sidebar-collapsed'),
				sidebarOverflow: computed.overflow
			};
		});
		console.log('Sidebar state after click:', JSON.stringify(sidebarAfterClick, null, 2));

		// Step 10: Try to manually set localStorage and reload
		console.log('\nStep 10: Setting localStorage to true and reloading...');
		await page.evaluate(() => {
			localStorage.setItem('gpt-oss-sidebar-open', 'true');
		});
		await page.reload({ waitUntil: 'networkidle' });
		await page.waitForTimeout(1000);

		const afterReload = await page.evaluate(() => {
			const sidebar = document.querySelector('.history-sidebar') as HTMLElement;
			const chatTab = document.querySelector('.chat-tab');
			const computed = sidebar ? window.getComputedStyle(sidebar) : null;
			return {
				localStorage: localStorage.getItem('gpt-oss-sidebar-open'),
				sidebarWidth: computed?.width || 'N/A',
				hasSidebarCollapsed: chatTab?.classList.contains('sidebar-collapsed')
			};
		});
		console.log('After localStorage fix and reload:', JSON.stringify(afterReload, null, 2));

		// Step 11: Check for any console errors
		console.log('\nStep 11: Console errors during test:');
		if (consoleErrors.length > 0) {
			consoleErrors.forEach((err) => console.log('  ERROR:', err));
		} else {
			console.log('  No console errors detected');
		}

		// Step 12: Take a screenshot for visual inspection
		console.log('\nStep 12: Taking screenshot...');
		await page.screenshot({ path: 'test-results/sidebar-debug-screenshot.png', fullPage: true });

		// Final assertion to verify the fix worked
		console.log('\n========== TEST CONCLUSION ==========\n');

		const finalState = await page.evaluate(() => {
			const sidebar = document.querySelector('.history-sidebar') as HTMLElement;
			return sidebar ? window.getComputedStyle(sidebar).width : '0px';
		});
		const widthValue = parseInt(finalState, 10);

		console.log(`Final sidebar width: ${finalState} (parsed: ${widthValue}px)`);
		console.log(`Expected: ~260px`);
		console.log(`Result: ${widthValue > 200 ? 'PASS - Sidebar is visible' : 'FAIL - Sidebar is hidden'}`);

		// This will fail if sidebar is not visible, providing clear feedback
		expect(widthValue, 'Sidebar should have width >= 200px when visible').toBeGreaterThanOrEqual(200);
	});

	test('should test SSR hydration issue', async ({ page }) => {
		console.log('\n========== SSR HYDRATION DEBUG ==========\n');

		// Clear localStorage first
		await page.goto('http://localhost:18173');
		await page.evaluate(() => {
			localStorage.removeItem('gpt-oss-sidebar-open');
		});

		// Now reload without localStorage
		await page.reload({ waitUntil: 'networkidle' });
		await page.waitForTimeout(500);

		// Check initial state (SSR)
		const ssrState = await page.evaluate(() => {
			const chatTab = document.querySelector('.chat-tab');
			const sidebar = document.querySelector('.history-sidebar') as HTMLElement;
			return {
				hasCollapsedClass: chatTab?.classList.contains('sidebar-collapsed'),
				sidebarWidth: sidebar
					? window.getComputedStyle(sidebar).width
					: 'not found',
				localStorage: localStorage.getItem('gpt-oss-sidebar-open')
			};
		});

		console.log('Initial SSR state (no localStorage):', JSON.stringify(ssrState, null, 2));

		// Wait for potential hydration
		await page.waitForTimeout(2000);

		const afterHydration = await page.evaluate(() => {
			const chatTab = document.querySelector('.chat-tab');
			const sidebar = document.querySelector('.history-sidebar') as HTMLElement;
			return {
				hasCollapsedClass: chatTab?.classList.contains('sidebar-collapsed'),
				sidebarWidth: sidebar
					? window.getComputedStyle(sidebar).width
					: 'not found',
				localStorage: localStorage.getItem('gpt-oss-sidebar-open')
			};
		});

		console.log('After 2s wait (post-hydration):', JSON.stringify(afterHydration, null, 2));

		// The sidebar should be open by default (no localStorage means default to open)
		const widthValue = parseInt(afterHydration.sidebarWidth as string, 10);
		expect(widthValue, 'Sidebar should default to open when no localStorage exists').toBeGreaterThanOrEqual(200);
	});

	test('should verify store reactivity', async ({ page }) => {
		console.log('\n========== STORE REACTIVITY DEBUG ==========\n');

		await page.goto('http://localhost:18173', { waitUntil: 'networkidle' });
		await page.waitForTimeout(1000);

		// Inject a test script that manually triggers store updates
		const result = await page.evaluate(() => {
			// Check if Svelte stores are accessible (they won't be directly, but we can test the outcome)
			const sidebar = document.querySelector('.history-sidebar') as HTMLElement;
			const chatTab = document.querySelector('.chat-tab');

			// Get initial state
			const initialWidth = sidebar ? window.getComputedStyle(sidebar).width : 'not found';
			const initialCollapsed = chatTab?.classList.contains('sidebar-collapsed');

			// Simulate clicking the collapse button if it exists
			const collapseBtn = document.querySelector('.collapse-btn') as HTMLElement;
			const btnExists = !!collapseBtn;

			if (collapseBtn) {
				collapseBtn.click();
			}

			return {
				initialWidth,
				initialCollapsed,
				collapseButtonExists: btnExists,
				message: 'Clicked collapse button if it existed'
			};
		});

		console.log('Initial state and collapse button test:', JSON.stringify(result, null, 2));

		// Wait for toggle to take effect
		await page.waitForTimeout(500);

		const afterToggle = await page.evaluate(() => {
			const sidebar = document.querySelector('.history-sidebar') as HTMLElement;
			const chatTab = document.querySelector('.chat-tab');
			return {
				width: sidebar ? window.getComputedStyle(sidebar).width : 'not found',
				hasCollapsedClass: chatTab?.classList.contains('sidebar-collapsed'),
				localStorage: localStorage.getItem('gpt-oss-sidebar-open')
			};
		});

		console.log('After toggle:', JSON.stringify(afterToggle, null, 2));

		// Click again to toggle back
		await page.locator('.collapse-btn').click();
		await page.waitForTimeout(500);

		const afterSecondToggle = await page.evaluate(() => {
			const sidebar = document.querySelector('.history-sidebar') as HTMLElement;
			const chatTab = document.querySelector('.chat-tab');
			return {
				width: sidebar ? window.getComputedStyle(sidebar).width : 'not found',
				hasCollapsedClass: chatTab?.classList.contains('sidebar-collapsed'),
				localStorage: localStorage.getItem('gpt-oss-sidebar-open')
			};
		});

		console.log('After second toggle (should be open):', JSON.stringify(afterSecondToggle, null, 2));
	});
});
