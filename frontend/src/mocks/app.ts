/**
 * Mock implementations for SvelteKit $app modules
 *
 * These mocks are loaded before tests run to provide fake implementations
 * of SvelteKit runtime modules that aren't available in the test environment.
 */

import { vi } from 'vitest';

// $app/environment mock
export const browser = true;
export const dev = true;
export const building = false;
export const version = '1.0.0';

// $app/navigation mock
export const goto = vi.fn();
export const invalidate = vi.fn();
export const invalidateAll = vi.fn();
export const prefetch = vi.fn();
export const prefetchRoutes = vi.fn();

// $app/stores mock
export const page = {
	subscribe: vi.fn()
};

export const navigating = {
	subscribe: vi.fn()
};

export const updated = {
	subscribe: vi.fn(),
	check: vi.fn()
};
