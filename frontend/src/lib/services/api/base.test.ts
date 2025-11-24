/**
 * Unit tests for base.ts - API request handler
 *
 * Test coverage:
 * - buildUrl function (5 tests)
 * - injectCsrfToken function (8 tests)
 * - handleCsrfError function (6 tests)
 * - apiRequest function (9 tests)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiRequest } from './base';
import { csrfClient } from '../core/csrf';
import { API_BASE_URL } from '$lib/config';
import * as toastStore from '$lib/stores/toast';

// Mock dependencies
vi.mock('../core/csrf');
vi.mock('$lib/stores/toast', () => ({
	toast: {
		error: vi.fn(),
		success: vi.fn(),
		info: vi.fn()
	}
}));

// Mock global fetch
global.fetch = vi.fn();

describe('base.ts - buildUrl', () => {
	afterEach(() => {
		vi.clearAllMocks();
	});

	it('returns absolute URL unchanged', async () => {
		const absoluteUrl = 'https://example.com/api/test';
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest(absoluteUrl, { skipCsrf: true });

		expect(fetch).toHaveBeenCalledWith(absoluteUrl, expect.any(Object));
	});

	it('prepends base URL to relative endpoint', async () => {
		const relativeEndpoint = '/api/projects';
		const expectedUrl = `${API_BASE_URL}${relativeEndpoint}`;

		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest(relativeEndpoint, { skipCsrf: true });

		expect(fetch).toHaveBeenCalledWith(expectedUrl, expect.any(Object));
	});

	it('handles endpoints starting with /', async () => {
		const endpoint = '/api/test';
		const expectedUrl = `${API_BASE_URL}${endpoint}`;

		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest(endpoint, { skipCsrf: true });

		expect(fetch).toHaveBeenCalledWith(expectedUrl, expect.any(Object));
	});

	it('handles endpoints without leading /', async () => {
		const endpoint = 'api/test';
		const expectedUrl = `${API_BASE_URL}${endpoint}`;

		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest(endpoint, { skipCsrf: true });

		expect(fetch).toHaveBeenCalledWith(expectedUrl, expect.any(Object));
	});

	it('uses configured base URL from config', async () => {
		const endpoint = '/api/test';

		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest(endpoint, { skipCsrf: true });

		const callUrl = vi.mocked(fetch).mock.calls[0][0] as string;
		expect(callUrl).toContain(API_BASE_URL);
	});
});

describe('base.ts - injectCsrfToken', () => {
	beforeEach(() => {
		vi.mocked(csrfClient.getToken).mockResolvedValue('mock-csrf-token');
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('adds CSRF token for POST requests', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest('/api/test', { method: 'POST', body: JSON.stringify({ test: true }) });

		expect(csrfClient.getToken).toHaveBeenCalled();
		expect(fetch).toHaveBeenCalledWith(
			expect.any(String),
			expect.objectContaining({
				headers: expect.objectContaining({
					'X-CSRF-Token': 'mock-csrf-token'
				})
			})
		);
	});

	it('adds CSRF token for PUT requests', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest('/api/test', { method: 'PUT', body: JSON.stringify({ test: true }) });

		expect(csrfClient.getToken).toHaveBeenCalled();
		expect(fetch).toHaveBeenCalledWith(
			expect.any(String),
			expect.objectContaining({
				headers: expect.objectContaining({
					'X-CSRF-Token': 'mock-csrf-token'
				})
			})
		);
	});

	it('adds CSRF token for DELETE requests', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest('/api/test', { method: 'DELETE' });

		expect(csrfClient.getToken).toHaveBeenCalled();
		expect(fetch).toHaveBeenCalledWith(
			expect.any(String),
			expect.objectContaining({
				headers: expect.objectContaining({
					'X-CSRF-Token': 'mock-csrf-token'
				})
			})
		);
	});

	it('adds CSRF token for PATCH requests', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest('/api/test', { method: 'PATCH', body: JSON.stringify({ test: true }) });

		expect(csrfClient.getToken).toHaveBeenCalled();
		expect(fetch).toHaveBeenCalledWith(
			expect.any(String),
			expect.objectContaining({
				headers: expect.objectContaining({
					'X-CSRF-Token': 'mock-csrf-token'
				})
			})
		);
	});

	it('does NOT add CSRF for GET requests', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest('/api/test', { method: 'GET' });

		expect(csrfClient.getToken).not.toHaveBeenCalled();
	});

	it('does NOT add CSRF for HEAD requests', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest('/api/test', { method: 'HEAD' });

		expect(csrfClient.getToken).not.toHaveBeenCalled();
	});

	it('skips CSRF when skipCsrf=true', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest('/api/test', { method: 'POST', skipCsrf: true });

		expect(csrfClient.getToken).not.toHaveBeenCalled();
	});

	it('preserves existing headers when adding CSRF', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest('/api/test', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Custom-Header': 'custom-value'
			}
		});

		expect(fetch).toHaveBeenCalledWith(
			expect.any(String),
			expect.objectContaining({
				headers: expect.objectContaining({
					'Content-Type': 'application/json',
					'X-Custom-Header': 'custom-value',
					'X-CSRF-Token': 'mock-csrf-token'
				})
			})
		);
	});
});

describe('base.ts - handleCsrfError', () => {
	beforeEach(() => {
		vi.mocked(csrfClient.getToken).mockResolvedValue('initial-token');
		vi.mocked(csrfClient.refreshToken).mockResolvedValue('new-token');
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('returns null for non-CSRF errors', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: false,
			status: 403,
			json: async () => ({ detail: 'Access denied' })
		} as Response);

		await expect(apiRequest('/api/test', { method: 'POST' })).rejects.toThrow();
		expect(csrfClient.refreshToken).not.toHaveBeenCalled();
	});

	it('refreshes token on 403 CSRF error', async () => {
		vi.mocked(fetch)
			.mockResolvedValueOnce({
				ok: false,
				status: 403,
				json: async () => ({ detail: 'CSRF token invalid' })
			} as Response)
			.mockResolvedValueOnce({
				ok: true,
				json: async () => ({ success: true })
			} as Response);

		const result = await apiRequest('/api/test', { method: 'POST' });

		expect(csrfClient.refreshToken).toHaveBeenCalled();
		expect(result).toEqual({ success: true });
	});

	it('retries request with new token', async () => {
		vi.mocked(fetch)
			.mockResolvedValueOnce({
				ok: false,
				status: 403,
				json: async () => ({ detail: 'CSRF token expired' })
			} as Response)
			.mockResolvedValueOnce({
				ok: true,
				json: async () => ({ data: 'retry-success' })
			} as Response);

		const result = await apiRequest('/api/test', { method: 'POST' });

		expect(fetch).toHaveBeenCalledTimes(2);
		expect(result).toEqual({ data: 'retry-success' });
	});

	it('returns retry response data on success', async () => {
		const expectedData = { message: 'Success after retry' };

		vi.mocked(fetch)
			.mockResolvedValueOnce({
				ok: false,
				status: 403,
				json: async () => ({ detail: 'CSRF token invalid' })
			} as Response)
			.mockResolvedValueOnce({
				ok: true,
				json: async () => expectedData
			} as Response);

		const result = await apiRequest('/api/test', { method: 'POST' });

		expect(result).toEqual(expectedData);
	});

	it('returns null if retry also fails', async () => {
		vi.mocked(fetch)
			.mockResolvedValueOnce({
				ok: false,
				status: 403,
				json: async () => ({ detail: 'CSRF token invalid' })
			} as Response)
			.mockResolvedValueOnce({
				ok: false,
				status: 403,
				json: async () => ({ detail: 'Still invalid' })
			} as Response);

		await expect(apiRequest('/api/test', { method: 'POST' })).rejects.toThrow();
	});

	it('only triggers for requests that need CSRF', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: false,
			status: 403,
			json: async () => ({ detail: 'CSRF token invalid' })
		} as Response);

		// GET request doesn't need CSRF, so no retry
		await expect(apiRequest('/api/test', { method: 'GET' })).rejects.toThrow();
		expect(csrfClient.refreshToken).not.toHaveBeenCalled();
	});
});

describe('base.ts - apiRequest', () => {
	beforeEach(() => {
		vi.mocked(csrfClient.getToken).mockResolvedValue('mock-csrf-token');
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it('successful GET request returns data', async () => {
		const mockData = { id: 1, name: 'Test Project' };

		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => mockData
		} as Response);

		const result = await apiRequest('/api/test', { method: 'GET' });

		expect(result).toEqual(mockData);
	});

	it('successful POST request returns data', async () => {
		const mockData = { id: 1, created: true };

		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => mockData
		} as Response);

		const result = await apiRequest('/api/test', { method: 'POST' });

		expect(result).toEqual(mockData);
	});

	it('throws error on 400 Bad Request', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: false,
			status: 400,
			statusText: 'Bad Request',
			json: async () => ({ detail: 'Invalid input' })
		} as Response);

		await expect(apiRequest('/api/test', { method: 'POST' })).rejects.toThrow('Invalid input');
		expect(toastStore.toast.error).toHaveBeenCalled();
	});

	it('throws error on 401 Unauthorized', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: false,
			status: 401,
			statusText: 'Unauthorized',
			json: async () => ({ detail: 'Authentication required' })
		} as Response);

		await expect(apiRequest('/api/test')).rejects.toThrow();
		expect(toastStore.toast.error).toHaveBeenCalledWith(
			expect.stringContaining('Authentication')
		);
	});

	it('retries on 403 CSRF error', async () => {
		vi.mocked(fetch)
			.mockResolvedValueOnce({
				ok: false,
				status: 403,
				json: async () => ({ detail: 'CSRF token invalid' })
			} as Response)
			.mockResolvedValueOnce({
				ok: true,
				json: async () => ({ success: true })
			} as Response);

		const result = await apiRequest('/api/test', { method: 'POST' });

		expect(result).toEqual({ success: true });
	});

	it('throws error on 404 Not Found', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: false,
			status: 404,
			statusText: 'Not Found',
			json: async () => ({ detail: 'Resource not found' })
		} as Response);

		await expect(apiRequest('/api/test')).rejects.toThrow('Resource not found');
		expect(toastStore.toast.error).toHaveBeenCalledWith(expect.stringContaining('not found'));
	});

	it('throws error on 500 Server Error', async () => {
		vi.mocked(fetch).mockResolvedValueOnce({
			ok: false,
			status: 500,
			statusText: 'Internal Server Error',
			json: async () => ({ detail: 'Server error occurred' })
		} as Response);

		await expect(apiRequest('/api/test')).rejects.toThrow();
		expect(toastStore.toast.error).toHaveBeenCalledWith(expect.stringContaining('Server error'));
	});

	it('includes error details from API response', async () => {
		const errorDetail = 'Specific validation error message';

		vi.mocked(fetch).mockResolvedValueOnce({
			ok: false,
			status: 422,
			statusText: 'Unprocessable Entity',
			json: async () => ({ detail: errorDetail })
		} as Response);

		await expect(apiRequest('/api/test', { method: 'POST' })).rejects.toThrow(errorDetail);
	});

	it('passes custom headers correctly', async () => {
		const customHeaders = {
			'Content-Type': 'application/json',
			'X-Custom-Header': 'custom-value'
		};

		vi.mocked(fetch).mockResolvedValueOnce({
			ok: true,
			json: async () => ({ success: true })
		} as Response);

		await apiRequest('/api/test', { method: 'GET', headers: customHeaders });

		expect(fetch).toHaveBeenCalledWith(
			expect.any(String),
			expect.objectContaining({
				headers: expect.objectContaining(customHeaders)
			})
		);
	});
});
