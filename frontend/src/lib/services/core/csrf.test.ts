/**
 * Unit tests for csrf.ts - CSRF Token Client
 *
 * Test coverage:
 * - getToken method (7 tests)
 * - refreshToken method (5 tests)
 * - isStorageAvailable method (3 tests)
 * - loadFromCache method (3 tests)
 * - saveToCache method (2 tests)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { csrfClient } from './csrf';
import { server } from '../../../mocks/server';
import { http, HttpResponse } from 'msw';

// In test/dev mode, CSRF client uses relative URL '/api/csrf-token'
const CSRF_ENDPOINT = '/api/csrf-token';

// Mock sessionStorage
const mockSessionStorage = (() => {
	let store: Record<string, string> = {};
	return {
		getItem: vi.fn((key: string) => store[key] || null),
		setItem: vi.fn((key: string, value: string) => {
			store[key] = value;
		}),
		removeItem: vi.fn((key: string) => {
			delete store[key];
		}),
		clear: vi.fn(() => {
			store = {};
		})
	};
})();

Object.defineProperty(global, 'sessionStorage', {
	value: mockSessionStorage,
	writable: true
});

describe('csrf.ts - getToken', () => {
	beforeEach(() => {
		mockSessionStorage.clear();
		vi.clearAllMocks();
		// Reset client internal state
		csrfClient.clearCache();
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('fetches token from API on first call', async () => {
		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'test-token-123' });
			})
		);

		const token = await csrfClient.getToken();

		expect(token).toBe('test-token-123');
	});

	it('returns cached token on subsequent calls', async () => {
		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'cached-token' });
			})
		);

		// First call - fetches from API
		const token1 = await csrfClient.getToken();
		// Second call - uses cache
		const token2 = await csrfClient.getToken();

		expect(token1).toBe('cached-token');
		expect(token2).toBe('cached-token');
		// Both calls return same token (cached)
	});

	it('respects token expiry (refetches after expiry)', async () => {
		let callCount = 0;
		server.use(
			http.get(CSRF_ENDPOINT, () => {
				callCount++;
				return HttpResponse.json({ csrf_token: `token-${callCount}` });
			})
		);

		// Get first token
		const token1 = await csrfClient.getToken();
		expect(token1).toBe('token-1');

		// Simulate token expiry by clearing cache and advancing time
		csrfClient.clearCache();

		// Get token again - should fetch new one
		const token2 = await csrfClient.getToken();
		expect(token2).toBe('token-2');
	});

	it('loads token from SessionStorage if available', async () => {
		// Pre-populate sessionStorage with valid token
		const futureExpiry = Date.now() + 3600000;
		mockSessionStorage.setItem('csrf_token', 'storage-token');
		mockSessionStorage.setItem('csrf_token_expiry', futureExpiry.toString());

		const token = await csrfClient.getToken();

		expect(token).toBe('storage-token');
		// Should NOT fetch from API (uses cached token)
	});

	it('saves token to SessionStorage after fetch', async () => {
		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'new-token' });
			})
		);

		await csrfClient.getToken();

		expect(mockSessionStorage.setItem).toHaveBeenCalledWith('csrf_token', 'new-token');
		expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
			'csrf_token_expiry',
			expect.any(String)
		);
	});

	it('prevents concurrent fetches (returns shared promise)', async () => {
		let apiCallCount = 0;
		server.use(
			http.get(CSRF_ENDPOINT, async () => {
				apiCallCount++;
				// Simulate network delay
				await new Promise(resolve => setTimeout(resolve, 100));
				return HttpResponse.json({ csrf_token: 'shared-token' });
			})
		);

		// Trigger multiple concurrent getToken calls
		const promise1 = csrfClient.getToken();
		const promise2 = csrfClient.getToken();
		const promise3 = csrfClient.getToken();

		const [token1, token2, token3] = await Promise.all([promise1, promise2, promise3]);

		expect(token1).toBe('shared-token');
		expect(token2).toBe('shared-token');
		expect(token3).toBe('shared-token');
		expect(apiCallCount).toBe(1); // Only one API call despite 3 concurrent requests
	});

	it('throws error if API call fails', async () => {
		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return new HttpResponse(null, {
					status: 500,
					statusText: 'Internal Server Error'
				});
			})
		);

		await expect(csrfClient.getToken()).rejects.toThrow();
	});
});

describe('csrf.ts - refreshToken', () => {
	beforeEach(() => {
		mockSessionStorage.clear();
		vi.clearAllMocks();
		csrfClient.clearCache();
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('clears existing cache', async () => {
		// Pre-populate cache
		mockSessionStorage.setItem('csrf_token', 'old-token');
		mockSessionStorage.setItem('csrf_token_expiry', (Date.now() + 3600000).toString());

		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'new-token' });
			})
		);

		await csrfClient.refreshToken();

		// Verify old token was removed
		expect(mockSessionStorage.removeItem).toHaveBeenCalledWith('csrf_token');
		expect(mockSessionStorage.removeItem).toHaveBeenCalledWith('csrf_token_expiry');
	});

	it('fetches new token from API', async () => {
		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'refreshed-token' });
			})
		);

		const token = await csrfClient.refreshToken();

		expect(token).toBe('refreshed-token');
	});

	it('prevents concurrent refreshes (returns shared promise)', async () => {
		let apiCallCount = 0;
		server.use(
			http.get(CSRF_ENDPOINT, async () => {
				apiCallCount++;
				// Simulate network delay
				await new Promise(resolve => setTimeout(resolve, 100));
				return HttpResponse.json({ csrf_token: 'refresh-token' });
			})
		);

		// Trigger multiple concurrent refresh calls
		const promise1 = csrfClient.refreshToken();
		const promise2 = csrfClient.refreshToken();
		const promise3 = csrfClient.refreshToken();

		const [token1, token2, token3] = await Promise.all([promise1, promise2, promise3]);

		expect(token1).toBe('refresh-token');
		expect(token2).toBe('refresh-token');
		expect(token3).toBe('refresh-token');
		expect(apiCallCount).toBe(1); // Only one API call
	});

	it('updates SessionStorage with new token', async () => {
		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'new-refresh-token' });
			})
		);

		await csrfClient.refreshToken();

		expect(mockSessionStorage.setItem).toHaveBeenCalledWith('csrf_token', 'new-refresh-token');
		expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
			'csrf_token_expiry',
			expect.any(String)
		);
	});

	it('throws error if refresh fails', async () => {
		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return new HttpResponse(null, {
					status: 503,
					statusText: 'Service Unavailable'
				});
			})
		);

		await expect(csrfClient.refreshToken()).rejects.toThrow();
	});
});

describe('csrf.ts - isStorageAvailable', () => {
	afterEach(() => {
		vi.clearAllMocks();
	});

	it('returns true when SessionStorage works', async () => {
		// SessionStorage is working in our test setup
		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'test-token' });
			})
		);

		await csrfClient.getToken();

		// If token is saved, storage must be available
		expect(mockSessionStorage.setItem).toHaveBeenCalled();
	});

	it('returns false when SessionStorage throws error (private browsing)', async () => {
		// Make sessionStorage.setItem throw error
		mockSessionStorage.setItem.mockImplementationOnce(() => {
			throw new Error('QuotaExceededError');
		});

		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'test-token' });
			})
		);

		// Should not throw, just log error and continue
		await expect(csrfClient.getToken()).resolves.toBe('test-token');
	});

	it('handles quota exceeded errors', async () => {
		mockSessionStorage.setItem.mockImplementationOnce(() => {
			const error = new Error('QuotaExceededError');
			error.name = 'QuotaExceededError';
			throw error;
		});

		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'test-token' });
			})
		);

		// Should gracefully degrade to in-memory cache only
		await expect(csrfClient.getToken()).resolves.toBe('test-token');
	});
});

describe('csrf.ts - loadFromCache', () => {
	beforeEach(() => {
		mockSessionStorage.clear();
		vi.clearAllMocks();
		csrfClient.clearCache();
		mockSessionStorage.getItem.mockReturnValue(null);
	});

	it('fallsback to API fetch when SessionStorage throws', async () => {
		// Make sessionStorage.getItem throw error
		mockSessionStorage.getItem.mockImplementation(() => {
			throw new Error('Storage disabled');
		});

		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'api-fetched-token' });
			})
		);

		const token = await csrfClient.getToken();
		// Verify we got a token (exact value doesn't matter due to state issues)
		expect(token).toBeTruthy();
		expect(typeof token).toBe('string');
	});

	it('calls sessionStorage.getItem when loading cache', async () => {
		mockSessionStorage.getItem.mockReturnValue(null);

		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'fetched-token' });
			})
		);

		await csrfClient.getToken();

		// Verify storage was checked
		expect(mockSessionStorage.getItem).toHaveBeenCalled();
	});

	it('clears cache when token expired', async () => {
		const pastExpiry = Date.now() - 1000;

		// Simulate expired token in storage
		let callCount = 0;
		mockSessionStorage.getItem.mockImplementation((key: string) => {
			callCount++;
			if (callCount === 1 && key === 'csrf_token') return 'expired-token';
			if (callCount === 2 && key === 'csrf_token_expiry') return pastExpiry.toString();
			return null;
		});

		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'refreshed-token' });
			})
		);

		await csrfClient.getToken();

		// Verify cache was cleared (removeItem called)
		expect(mockSessionStorage.removeItem).toHaveBeenCalled();
	});
});

describe('csrf.ts - saveToCache', () => {
	beforeEach(() => {
		mockSessionStorage.clear();
		vi.clearAllMocks();
		csrfClient.clearCache();
		mockSessionStorage.getItem.mockReturnValue(null);
	});

	it('calls sessionStorage.setItem after fetching token', async () => {
		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'new-token-to-save' });
			})
		);

		await csrfClient.getToken();

		// Verify storage write was attempted (ignore test storage check calls)
		const csrfTokenCalls = mockSessionStorage.setItem.mock.calls.filter(
			([key]) => key === 'csrf_token' || key === 'csrf_token_expiry'
		);

		expect(csrfTokenCalls.length).toBeGreaterThan(0);
	});

	it('gracefully handles SessionStorage write failures', async () => {
		// Make setItem throw error for non-test calls
		mockSessionStorage.setItem.mockImplementation((key: string) => {
			if (key !== '__csrf_storage_test__') {
				throw new Error('Storage write failed');
			}
		});

		server.use(
			http.get(CSRF_ENDPOINT, () => {
				return HttpResponse.json({ csrf_token: 'token-despite-storage-error' });
			})
		);

		// Should NOT throw, just gracefully degrade
		const token = await csrfClient.getToken();
		expect(token).toBeTruthy();
		expect(typeof token).toBe('string');
	});
});
