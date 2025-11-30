import { test, expect } from '@playwright/test';

test.describe('UI Fixes Verification', () => {
	test('Chat tab should show content when clicked', async ({ page }) => {
		await page.goto('http://localhost:18173');
		await page.waitForLoadState('networkidle');

		// Wait for page to load
		await page.waitForTimeout(2000);

		// Take screenshot of initial state
		await page.screenshot({ path: 'tests/e2e/screenshots/initial-state.png', fullPage: true });

		// Click the chat icon in the left nav
		const chatTab = page.locator('#chat-tab');
		await expect(chatTab).toBeVisible();
		console.log('Chat tab visible:', await chatTab.isVisible());

		await chatTab.click();
		await page.waitForTimeout(500);

		// Verify chat panel is visible
		const chatPanel = page.locator('#chat-panel');
		const chatPanelVisible = await chatPanel.isVisible();
		console.log('Chat panel visible:', chatPanelVisible);

		// Check for ChatTab content - sidebar
		const sidebar = page.locator('.history-sidebar');
		const sidebarVisible = await sidebar.isVisible();
		console.log('Sidebar visible:', sidebarVisible);

		// Take screenshot of chat tab
		await page.screenshot({ path: 'tests/e2e/screenshots/chat-tab.png', fullPage: true });

		// Verify project selector in sidebar
		const projectHeader = page.locator('.project-header');
		const projectHeaderVisible = await projectHeader.isVisible();
		console.log('Project header visible:', projectHeaderVisible);

		// Click Documents tab
		const docsTab = page.locator('#documents-tab');
		if (await docsTab.getAttribute('aria-disabled') !== 'true') {
			await docsTab.click();
			await page.waitForTimeout(500);

			// Take screenshot of documents tab
			await page.screenshot({ path: 'tests/e2e/screenshots/documents-tab.png', fullPage: true });

			// Check for project name subtitle
			const projectSubtitle = page.locator('.project-name-subtitle');
			const subtitleVisible = await projectSubtitle.isVisible();
			console.log('Project name subtitle visible:', subtitleVisible);
			if (subtitleVisible) {
				const subtitleText = await projectSubtitle.textContent();
				console.log('Project name:', subtitleText);
			}
		}

		expect(chatPanelVisible || sidebarVisible).toBeTruthy();
	});
});
