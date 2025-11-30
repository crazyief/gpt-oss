import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration
 *
 * Purpose: Browser-based end-to-end testing for GPT-OSS frontend
 *
 * Why Playwright over Cypress:
 * - Multi-browser support (Chrome, Firefox, Safari)
 * - Better TypeScript integration
 * - Faster execution
 * - Built-in auto-waiting (reduces flaky tests)
 *
 * Test Structure:
 * - tests/e2e/ - End-to-end user workflows
 * - tests/ssr/ - SSR rendering smoke tests
 * - tests/visual/ - Visual regression tests (Stage 2+)
 *
 * Usage:
 * - Default (local dev server): npm run test:e2e
 * - With Docker backend: USE_DOCKER=true npm run test:e2e
 */

// Determine if we should use Docker-deployed services
const useDocker = process.env.USE_DOCKER === 'true';
// Use 127.0.0.1 instead of localhost to avoid IPv6 issues on Windows with Docker
const baseURL = useDocker ? 'http://127.0.0.1:18173' : 'http://localhost:5173';

export default defineConfig({
	// Test directory (updated to include component tests)
	testDir: './tests',

	// Timeout for each test
	timeout: 30 * 1000, // 30 seconds

	// Expect timeout for assertions
	expect: {
		timeout: 5000 // 5 seconds
	},

	// Run tests in files in parallel
	fullyParallel: true,

	// Fail the build on CI if you accidentally left test.only in the source code
	forbidOnly: !!process.env.CI,

	// Retry on CI only
	retries: process.env.CI ? 2 : 0,

	// Opt out of parallel tests on CI
	workers: process.env.CI ? 1 : undefined,

	// Reporter to use
	reporter: [
		['html', { outputFolder: 'playwright-report' }],
		['json', { outputFile: 'test-results/e2e-results.json' }],
		['list']
	],

	// Shared settings for all the projects below
	use: {
		// Base URL to use in actions like `await page.goto('/')`
		baseURL,

		// Collect trace when retrying the failed test
		trace: 'on-first-retry',

		// Screenshot on failure
		screenshot: 'only-on-failure',

		// Video on failure
		video: 'retain-on-failure',

		// Maximum time each action such as `click()` can take
		actionTimeout: 10000,

		// Navigation timeout
		navigationTimeout: 30000
	},

	// Configure projects for major browsers
	projects: [
		{
			name: 'chromium',
			use: { ...devices['Desktop Chrome'] }
		},

		{
			name: 'firefox',
			use: { ...devices['Desktop Firefox'] }
		},

		// Uncomment for Safari testing (macOS only)
		// {
		// 	name: 'webkit',
		// 	use: { ...devices['Desktop Safari'] }
		// },

		// Mobile viewports for responsive testing
		{
			name: 'Mobile Chrome',
			use: { ...devices['Pixel 5'] }
		},

		{
			name: 'Mobile Safari',
			use: { ...devices['iPhone 12'] }
		}
	],

	// Run your local dev server before starting the tests (skip if using Docker)
	webServer: useDocker
		? undefined
		: {
				command: 'npm run dev',
				url: 'http://localhost:5173',
				reuseExistingServer: !process.env.CI,
				timeout: 120 * 1000, // 2 minutes for server startup
				stdout: 'ignore',
				stderr: 'pipe'
			}
});
