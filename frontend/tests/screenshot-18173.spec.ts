import { test, expect } from '@playwright/test';

test.use({ baseURL: 'http://localhost:18173' });

test('Screenshot from port 18173', async ({ page }) => {
  await page.goto('http://localhost:18173');
  await page.waitForTimeout(3000);
  
  // Take screenshot
  await page.screenshot({ path: 'screenshot-18173.png', fullPage: false });
  
  console.log('Screenshot saved to screenshot-18173.png');
  
  // Check elements
  const projectHeader = await page.$('.project-header');
  const projectSelect = await page.$('.project-select');
  console.log('ProjectHeader div:', !!projectHeader);
  console.log('ProjectSelect element:', !!projectSelect);
});
