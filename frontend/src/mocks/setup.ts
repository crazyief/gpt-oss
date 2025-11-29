/**
 * MSW Test Setup
 *
 * Integrates MSW server with Vitest lifecycle hooks.
 * Ensures clean state for each test.
 */

import { beforeAll, afterEach, afterAll, vi } from 'vitest';
import { server } from './server';
import { resetMockData } from './handlers';

// Mock SvelteKit $app modules
vi.mock('$app/environment', () => ({
	browser: true,
	dev: true,
	building: false,
	version: '1.0.0'
}));

vi.mock('$app/navigation', () => ({
	goto: vi.fn(),
	invalidate: vi.fn(),
	invalidateAll: vi.fn(),
	prefetch: vi.fn(),
	prefetchRoutes: vi.fn()
}));

vi.mock('$app/stores', () => ({
	page: {
		subscribe: vi.fn()
	},
	navigating: {
		subscribe: vi.fn()
	},
	updated: {
		subscribe: vi.fn(),
		check: vi.fn()
	}
}));

// Start MSW server before all tests
beforeAll(() => {
	server.listen({
		onUnhandledRequest: 'warn' // Warn on unhandled requests (helps catch missing handlers)
	});
});

// Reset handlers and mock data after each test (test isolation)
afterEach(() => {
	server.resetHandlers();
	resetMockData();
});

// Clean up after all tests
afterAll(() => {
	server.close();
});
