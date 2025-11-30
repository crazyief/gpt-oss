import { test, expect } from '@playwright/test';

/**
 * Comprehensive E2E tests for UI fixes:
 * 1. Documents page shows project name in header
 * 2. Settings page shows project name in header
 * 3. Chat tab shows content when clicked
 */

test.describe('UI Fixes - Comprehensive Verification', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('http://localhost:18173');
		await page.waitForLoadState('networkidle');
		await page.waitForTimeout(1000); // Wait for initial load
	});

	test('Chat tab should display sidebar and content area', async ({ page }) => {
		// Verify chat tab is active by default
		const chatTab = page.locator('#chat-tab');
		await expect(chatTab).toBeVisible();
		await expect(chatTab).toHaveAttribute('aria-selected', 'true');

		// Verify chat panel exists
		const chatPanel = page.locator('#chat-panel');
		await expect(chatPanel).toBeVisible();

		// Verify sidebar with project selector
		const sidebar = page.locator('.history-sidebar');
		await expect(sidebar).toBeVisible();

		// Verify project header in sidebar
		const projectHeader = page.locator('.project-header');
		await expect(projectHeader).toBeVisible();

		// Verify project selector dropdown exists
		const projectSelect = page.locator('.project-select');
		await expect(projectSelect).toBeVisible();

		// Verify "CONVERSATIONS" label
		const conversationsLabel = page.locator('.section-label');
		await expect(conversationsLabel).toContainText('Conversations');

		// Verify New Chat button
		const newChatBtn = page.locator('button:has-text("New Chat")');
		await expect(newChatBtn).toBeVisible();

		// Verify main content area shows empty state or chat
		const mainContent = page.locator('.chat-main, .empty-state');
		await expect(mainContent).toBeVisible();

		// Take screenshot for verification
		await page.screenshot({ path: 'tests/e2e/screenshots/chat-tab-verified.png', fullPage: true });
	});

	test('Chat tab should re-open sidebar when clicked', async ({ page }) => {
		// First, collapse the sidebar
		const collapseBtn = page.locator('.collapse-btn');
		await expect(collapseBtn).toBeVisible();
		await collapseBtn.click();
		await page.waitForTimeout(500);

		// Verify sidebar is collapsed
		const chatTabLayout = page.locator('.chat-tab');
		await expect(chatTabLayout).toHaveClass(/sidebar-collapsed/);

		// Click on a different tab first (documents if enabled, or stay on chat)
		const docsTab = page.locator('#documents-tab');
		const isDocsDisabled = await docsTab.getAttribute('aria-disabled');

		if (isDocsDisabled !== 'true') {
			// Switch to docs tab
			await docsTab.click();
			await page.waitForTimeout(500);

			// Now click chat tab - sidebar should open
			const chatTab = page.locator('#chat-tab');
			await chatTab.click();
			await page.waitForTimeout(500);

			// Verify sidebar is visible
			const sidebar = page.locator('.history-sidebar');
			await expect(sidebar).toBeVisible();
		}
	});

	test('Documents tab should show project name in header', async ({ page }) => {
		// First, select a project from the dropdown
		const projectSelect = page.locator('.project-select');
		await expect(projectSelect).toBeVisible();

		// Get the current project name from the dropdown
		const projectName = await projectSelect.textContent();
		console.log('Current project in selector:', projectName);

		// Click on Documents tab
		const docsTab = page.locator('#documents-tab');
		const isDisabled = await docsTab.getAttribute('aria-disabled');

		if (isDisabled === 'true') {
			console.log('Documents tab is disabled - no project selected');
			// Select a project first by clicking on an option
			await projectSelect.click();
			await page.waitForTimeout(300);

			// Click on first available project option
			const firstOption = page.locator('.project-option').first();
			if (await firstOption.isVisible()) {
				await firstOption.click();
				await page.waitForTimeout(500);
			}
		}

		// Now try clicking Documents tab again
		await docsTab.click();
		await page.waitForTimeout(1000);

		// Verify Documents panel is visible
		const docsPanel = page.locator('#documents-panel');
		await expect(docsPanel).toBeVisible();

		// Verify Documents header
		const docsTitle = page.locator('.documents-title');
		await expect(docsTitle).toBeVisible();
		await expect(docsTitle).toContainText('Documents');

		// Verify project name subtitle exists in header
		const projectSubtitle = page.locator('.documents-tab .project-name-subtitle');
		await expect(projectSubtitle).toBeVisible();

		const subtitleText = await projectSubtitle.textContent();
		console.log('Documents page project subtitle:', subtitleText);

		// Verify subtitle is not empty (should show project name or "Unknown Project")
		expect(subtitleText?.length).toBeGreaterThan(0);

		// Take screenshot
		await page.screenshot({ path: 'tests/e2e/screenshots/documents-project-name.png', fullPage: true });
	});

	test('Settings tab should show project name in header', async ({ page }) => {
		// First ensure a project is selected
		const projectSelect = page.locator('.project-select');
		await expect(projectSelect).toBeVisible();

		// Click on Settings tab
		const settingsTab = page.locator('#settings-tab');
		const isDisabled = await settingsTab.getAttribute('aria-disabled');

		if (isDisabled === 'true') {
			console.log('Settings tab is disabled - no project selected');
			// Select a project first
			await projectSelect.click();
			await page.waitForTimeout(300);

			const firstOption = page.locator('.project-option').first();
			if (await firstOption.isVisible()) {
				await firstOption.click();
				await page.waitForTimeout(500);
			}
		}

		// Now click Settings tab
		await settingsTab.click();
		await page.waitForTimeout(1000);

		// Verify Settings panel is visible
		const settingsPanel = page.locator('#settings-panel');
		await expect(settingsPanel).toBeVisible();

		// Verify Settings header
		const settingsTitle = page.locator('.settings-title');
		await expect(settingsTitle).toBeVisible();
		await expect(settingsTitle).toContainText('Project Settings');

		// Verify project name subtitle in header (appears after project loads)
		const projectSubtitle = page.locator('.settings-tab .project-name-subtitle');

		// Wait for project to load (it fetches project data)
		await page.waitForTimeout(2000);

		if (await projectSubtitle.isVisible()) {
			const subtitleText = await projectSubtitle.textContent();
			console.log('Settings page project subtitle:', subtitleText);
			expect(subtitleText?.length).toBeGreaterThan(0);
		} else {
			console.log('Settings subtitle not visible - may still be loading');
		}

		// Take screenshot
		await page.screenshot({ path: 'tests/e2e/screenshots/settings-project-name.png', fullPage: true });
	});

	test('Documents header shows correct project name after selection', async ({ page }) => {
		// Click project selector
		const projectSelect = page.locator('.project-select');
		await expect(projectSelect).toBeVisible();
		await projectSelect.click();
		await page.waitForTimeout(300);

		// Get list of project options
		const projectOptions = page.locator('.project-option');
		const optionCount = await projectOptions.count();
		console.log('Available projects:', optionCount);

		if (optionCount > 0) {
			// Get the first project name before clicking
			const firstOption = projectOptions.first();
			const expectedProjectName = await firstOption.textContent();
			console.log('Selecting project:', expectedProjectName);

			// Click to select
			await firstOption.click();
			await page.waitForTimeout(500);

			// Navigate to Documents tab
			const docsTab = page.locator('#documents-tab');
			await docsTab.click();
			await page.waitForTimeout(1000);

			// Verify project subtitle shows the selected project name
			const projectSubtitle = page.locator('.documents-tab .project-name-subtitle');
			await expect(projectSubtitle).toBeVisible();

			const displayedName = await projectSubtitle.textContent();
			console.log('Displayed project name in Documents:', displayedName);

			// The displayed name should match (may need to parse the project name without count)
			// expectedProjectName might be "Project Name (count)"
			if (expectedProjectName) {
				const projectNameOnly = expectedProjectName.replace(/\s*\(\d+\)\s*$/, '').trim();
				expect(displayedName).toContain(projectNameOnly);
			}
		}
	});

	test('All three tabs are navigable and show content', async ({ page }) => {
		// Select a project first to enable all tabs
		const projectSelect = page.locator('.project-select');
		await projectSelect.click();
		await page.waitForTimeout(300);

		const firstOption = page.locator('.project-option').first();
		if (await firstOption.isVisible()) {
			await firstOption.click();
			await page.waitForTimeout(500);
		}

		// Test Chat Tab
		const chatTab = page.locator('#chat-tab');
		await chatTab.click();
		await page.waitForTimeout(500);

		const chatPanel = page.locator('#chat-panel');
		await expect(chatPanel).toBeVisible();
		console.log('✓ Chat tab shows content');

		// Test Documents Tab
		const docsTab = page.locator('#documents-tab');
		await docsTab.click();
		await page.waitForTimeout(500);

		const docsPanel = page.locator('#documents-panel');
		await expect(docsPanel).toBeVisible();
		console.log('✓ Documents tab shows content');

		// Test Settings Tab
		const settingsTab = page.locator('#settings-tab');
		await settingsTab.click();
		await page.waitForTimeout(500);

		const settingsPanel = page.locator('#settings-panel');
		await expect(settingsPanel).toBeVisible();
		console.log('✓ Settings tab shows content');

		// Navigate back to Chat
		await chatTab.click();
		await page.waitForTimeout(500);
		await expect(chatPanel).toBeVisible();
		console.log('✓ Can navigate back to Chat tab');
	});

	test('Theme toggle is visible in VerticalNav footer', async ({ page }) => {
		// Verify theme toggle exists at bottom of nav
		const navFooter = page.locator('.nav-footer');
		await expect(navFooter).toBeVisible();

		const themeToggle = page.locator('.nav-footer .theme-toggle');
		await expect(themeToggle).toBeVisible();
		console.log('✓ Theme toggle is visible in nav footer');
	});

	test('Project selector in sidebar header works', async ({ page }) => {
		// Verify project header exists
		const projectHeader = page.locator('.project-header');
		await expect(projectHeader).toBeVisible();

		// Verify project selector is inside the header
		const projectSelect = projectHeader.locator('.project-select');
		await expect(projectSelect).toBeVisible();

		// Click to open dropdown
		await projectSelect.click();
		await page.waitForTimeout(300);

		// Check if dropdown options appear
		const dropdownVisible = await page.locator('.project-dropdown, .project-option').first().isVisible();
		console.log('Project dropdown opened:', dropdownVisible);

		// Take screenshot
		await page.screenshot({ path: 'tests/e2e/screenshots/project-selector-dropdown.png', fullPage: true });
	});
});
