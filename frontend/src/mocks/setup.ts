/**
 * MSW Test Setup
 *
 * Integrates MSW server with Vitest lifecycle hooks.
 * Ensures clean state for each test.
 */

import { beforeAll, afterEach, afterAll } from 'vitest';
import { server } from './server';
import { resetMockData } from './handlers';

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
