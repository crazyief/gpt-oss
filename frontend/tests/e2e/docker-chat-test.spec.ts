import { test, expect } from '@playwright/test';

/**
 * Test directly against Docker container on port 18173
 * This bypasses Playwright's webServer and tests the actual Docker deployment
 */

test.describe('Docker Container - Chat Tab Test', () => {
	test('Chat icon click should show sidebar and content', async ({ page }) => {
		// Go directly to Docker container
		await page.goto('http://localhost:18173');
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(3000); // Wait for Docker container to fully load

		// Take initial screenshot
		await page.screenshot({ path: 'tests/e2e/screenshots/docker-initial.png', fullPage: true });

		// Check if page loaded
		const body = page.locator('body');
		await expect(body).toBeVisible();
		console.log('Page loaded successfully');

		// Check for vertical nav
		const verticalNav = page.locator('.vertical-nav');
		const navExists = await verticalNav.isVisible();
		console.log('Vertical nav exists:', navExists);

		// Check for chat tab button
		const chatTab = page.locator('#chat-tab');
		const chatTabExists = await chatTab.isVisible();
		console.log('Chat tab button exists:', chatTabExists);

		if (!chatTabExists) {
			console.log('ERROR: Chat tab button not found!');
			await page.screenshot({ path: 'tests/e2e/screenshots/docker-no-chat-tab.png', fullPage: true });
			throw new Error('Chat tab button not found');
		}

		// Click the chat tab
		await chatTab.click();
		await page.waitForTimeout(1000);
		console.log('Clicked chat tab');

		// Take screenshot after clicking
		await page.screenshot({ path: 'tests/e2e/screenshots/docker-after-chat-click.png', fullPage: true });

		// Check for chat panel
		const chatPanel = page.locator('#chat-panel');
		const chatPanelExists = await chatPanel.isVisible();
		console.log('Chat panel visible:', chatPanelExists);

		// Check for sidebar
		const sidebar = page.locator('.history-sidebar');
		const sidebarExists = await sidebar.isVisible();
		console.log('Sidebar visible:', sidebarExists);

		// Check for project header in sidebar
		const projectHeader = page.locator('.project-header');
		const projectHeaderExists = await projectHeader.isVisible();
		console.log('Project header visible:', projectHeaderExists);

		// Check for project selector
		const projectSelect = page.locator('.project-select');
		const projectSelectExists = await projectSelect.isVisible();
		console.log('Project selector visible:', projectSelectExists);

		// Check for New Chat button
		const newChatBtn = page.locator('button:has-text("New Chat")');
		const newChatExists = await newChatBtn.isVisible();
		console.log('New Chat button visible:', newChatExists);

		// Check for chat content area
		const chatMain = page.locator('.chat-main');
		const chatMainExists = await chatMain.isVisible();
		console.log('Chat main area visible:', chatMainExists);

		// Final screenshot
		await page.screenshot({ path: 'tests/e2e/screenshots/docker-chat-tab-final.png', fullPage: true });

		// Assert all elements are visible
		expect(chatPanelExists).toBeTruthy();
		expect(sidebarExists).toBeTruthy();
		expect(projectHeaderExists).toBeTruthy();

		console.log('✓ All chat tab elements are visible');
	});

	test('Navigate from Documents to Chat - sidebar should appear', async ({ page }) => {
		await page.goto('http://localhost:18173');
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(3000);

		// First, click on Documents tab (if enabled)
		const docsTab = page.locator('#documents-tab');
		const isDocsDisabled = await docsTab.getAttribute('aria-disabled');

		if (isDocsDisabled !== 'true') {
			await docsTab.click();
			await page.waitForTimeout(500);
			console.log('Navigated to Documents tab');

			// Now click Chat tab
			const chatTab = page.locator('#chat-tab');
			await chatTab.click();
			await page.waitForTimeout(500);
			console.log('Navigated back to Chat tab');

			// Verify sidebar is visible
			const sidebar = page.locator('.history-sidebar');
			await expect(sidebar).toBeVisible();
			console.log('✓ Sidebar is visible after navigating from Documents to Chat');

			await page.screenshot({ path: 'tests/e2e/screenshots/docker-docs-to-chat.png', fullPage: true });
		} else {
			console.log('Documents tab disabled, skipping navigation test');
		}
	});
});
