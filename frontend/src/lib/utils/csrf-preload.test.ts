/**
 * Unit tests for CSRF token preload utility
 *
 * Tests: Preload success, failure handling, toast notifications
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { preloadCsrfToken } from './csrf-preload';

// Mock dependencies
vi.mock('$lib/services/core/csrf', () => ({
	csrfClient: {
		getToken: vi.fn()
	}
}));

vi.mock('$lib/stores/toast', () => ({
	toast: {
		warning: vi.fn(),
		error: vi.fn(),
		success: vi.fn(),
		info: vi.fn()
	}
}));

vi.mock('$lib/utils/logger', () => ({
	logger: {
		info: vi.fn(),
		error: vi.fn(),
		warn: vi.fn(),
		debug: vi.fn()
	}
}));

describe('preloadCsrfToken', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe('successful preload', () => {
		it('should call csrfClient.getToken', async () => {
			const { csrfClient } = await import('$lib/services/core/csrf');
			(csrfClient.getToken as ReturnType<typeof vi.fn>).mockResolvedValue('test-token');

			await preloadCsrfToken();

			expect(csrfClient.getToken).toHaveBeenCalledTimes(1);
		});

		it('should log success message', async () => {
			const { csrfClient } = await import('$lib/services/core/csrf');
			const { logger } = await import('$lib/utils/logger');

			(csrfClient.getToken as ReturnType<typeof vi.fn>).mockResolvedValue('test-token');

			await preloadCsrfToken();

			expect(logger.info).toHaveBeenCalledWith('CSRF token preloaded successfully');
		});

		it('should not show toast on success', async () => {
			const { csrfClient } = await import('$lib/services/core/csrf');
			const { toast } = await import('$lib/stores/toast');

			(csrfClient.getToken as ReturnType<typeof vi.fn>).mockResolvedValue('test-token');

			await preloadCsrfToken();

			expect(toast.warning).not.toHaveBeenCalled();
			expect(toast.error).not.toHaveBeenCalled();
		});

		it('should not throw on success', async () => {
			const { csrfClient } = await import('$lib/services/core/csrf');
			(csrfClient.getToken as ReturnType<typeof vi.fn>).mockResolvedValue('test-token');

			await expect(preloadCsrfToken()).resolves.toBeUndefined();
		});
	});

	describe('failed preload', () => {
		it('should catch and handle errors gracefully', async () => {
			const { csrfClient } = await import('$lib/services/core/csrf');
			(csrfClient.getToken as ReturnType<typeof vi.fn>).mockRejectedValue(
				new Error('Network error')
			);

			// Should not throw
			await expect(preloadCsrfToken()).resolves.toBeUndefined();
		});

		it('should log error on failure', async () => {
			const { csrfClient } = await import('$lib/services/core/csrf');
			const { logger } = await import('$lib/utils/logger');

			const error = new Error('Network error');
			(csrfClient.getToken as ReturnType<typeof vi.fn>).mockRejectedValue(error);

			await preloadCsrfToken();

			expect(logger.error).toHaveBeenCalledWith('CSRF token preload failed', { error });
		});

		it('should show warning toast on failure', async () => {
			const { csrfClient } = await import('$lib/services/core/csrf');
			const { toast } = await import('$lib/stores/toast');

			(csrfClient.getToken as ReturnType<typeof vi.fn>).mockRejectedValue(
				new Error('Network error')
			);

			await preloadCsrfToken();

			expect(toast.warning).toHaveBeenCalledWith(
				'Security initialization delayed. First action may be slower.',
				4000
			);
		});

		it('should handle non-Error rejections', async () => {
			const { csrfClient } = await import('$lib/services/core/csrf');
			const { logger } = await import('$lib/utils/logger');

			(csrfClient.getToken as ReturnType<typeof vi.fn>).mockRejectedValue('string error');

			await preloadCsrfToken();

			expect(logger.error).toHaveBeenCalledWith('CSRF token preload failed', {
				error: 'string error'
			});
		});

		it('should handle timeout errors', async () => {
			const { csrfClient } = await import('$lib/services/core/csrf');
			const { toast } = await import('$lib/stores/toast');

			const timeoutError = new Error('Request timeout');
			timeoutError.name = 'TimeoutError';
			(csrfClient.getToken as ReturnType<typeof vi.fn>).mockRejectedValue(timeoutError);

			await preloadCsrfToken();

			expect(toast.warning).toHaveBeenCalled();
		});
	});

	describe('return value', () => {
		it('should return Promise<void> on success', async () => {
			const { csrfClient } = await import('$lib/services/core/csrf');
			(csrfClient.getToken as ReturnType<typeof vi.fn>).mockResolvedValue('token');

			const result = preloadCsrfToken();
			expect(result).toBeInstanceOf(Promise);

			const resolved = await result;
			expect(resolved).toBeUndefined();
		});

		it('should return Promise<void> on failure', async () => {
			const { csrfClient } = await import('$lib/services/core/csrf');
			(csrfClient.getToken as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('fail'));

			const result = preloadCsrfToken();
			expect(result).toBeInstanceOf(Promise);

			const resolved = await result;
			expect(resolved).toBeUndefined();
		});
	});

	describe('non-blocking behavior', () => {
		it('should not block on slow token fetch', async () => {
			const { csrfClient } = await import('$lib/services/core/csrf');

			// Simulate slow API
			(csrfClient.getToken as ReturnType<typeof vi.fn>).mockImplementation(
				() => new Promise((resolve) => setTimeout(() => resolve('token'), 100))
			);

			const start = Date.now();
			const promise = preloadCsrfToken();

			// Promise should be returned immediately (non-blocking)
			expect(promise).toBeInstanceOf(Promise);

			await promise;
			const elapsed = Date.now() - start;

			// Should take at least 100ms (the timeout)
			expect(elapsed).toBeGreaterThanOrEqual(90); // Allow some timing variance
		});
	});
});
