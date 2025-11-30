import { test, expect } from '@playwright/test';

test('Verify UI Layout', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await page.waitForTimeout(2000);
  
  // Take screenshot
  await page.screenshot({ path: 'verify-ui-screenshot.png', fullPage: false });
  
  // Check for TopBar (should NOT exist after fix)
  const topbar = await page.$('header.top-bar');
  console.log('TopBar exists:', !!topbar);
  
  // Check for VerticalNav
  const verticalNav = await page.$('.vertical-nav');
  console.log('VerticalNav exists:', !!verticalNav);
  
  // Check for ThemeToggle in VerticalNav footer
  const themeInNav = await page.$('.nav-footer .theme-toggle');
  console.log('ThemeToggle in nav-footer:', !!themeInNav);
  
  // Check for Sidebar with project selector
  const projectInSidebar = await page.$('.sidebar-header .project-select');
  console.log('ProjectSelector in sidebar:', !!projectInSidebar);
  
  // Verify expected layout
  expect(verticalNav).toBeTruthy();
});
