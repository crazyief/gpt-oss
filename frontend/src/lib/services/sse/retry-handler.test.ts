/**
 * Unit tests for SSE retry handler
 *
 * Tests: Exponential backoff, retry limits, cleanup race condition prevention
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { RetryHandler } from './retry-handler';

// Mock dependencies
vi.mock('$lib/config', () => ({
	APP_CONFIG: {
		sse: {
			maxRetries: 5,
			retryDelays: [1000, 2000, 4000, 8000, 16000]
		}
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

vi.mock('$lib/stores/toast', () => ({
	toast: {
		warning: vi.fn(),
		error: vi.fn(),
		success: vi.fn(),
		info: vi.fn()
	}
}));

describe('RetryHandler', () => {
	let retryHandler: RetryHandler;

	beforeEach(() => {
		vi.useFakeTimers();
		retryHandler = new RetryHandler();
	});

	afterEach(() => {
		vi.useRealTimers();
		vi.clearAllMocks();
	});

	describe('initial state', () => {
		it('should start with retry count of 0', () => {
			expect(retryHandler.getRetryCount()).toBe(0);
		});

		it('should not be cleaned up initially', () => {
			expect(retryHandler.isCleanedUpState()).toBe(false);
		});

		it('should not have exceeded max retries initially', () => {
			expect(retryHandler.isMaxRetriesExceeded()).toBe(false);
		});
	});

	describe('custom config', () => {
		it('should accept custom retry configuration', () => {
			const customHandler = new RetryHandler({
				maxRetries: 3,
				retryDelays: [500, 1000, 2000]
			});

			// Increment to 4 (exceeds max of 3)
			customHandler.incrementRetry();
			customHandler.incrementRetry();
			customHandler.incrementRetry();
			customHandler.incrementRetry();

			expect(customHandler.isMaxRetriesExceeded()).toBe(true);
		});
	});

	describe('getRetryCount', () => {
		it('should return current retry count', () => {
			expect(retryHandler.getRetryCount()).toBe(0);

			retryHandler.incrementRetry();
			expect(retryHandler.getRetryCount()).toBe(1);

			retryHandler.incrementRetry();
			expect(retryHandler.getRetryCount()).toBe(2);
		});
	});

	describe('isMaxRetriesExceeded', () => {
		it('should return false when under max retries', () => {
			retryHandler.incrementRetry(); // 1
			expect(retryHandler.isMaxRetriesExceeded()).toBe(false);

			retryHandler.incrementRetry(); // 2
			expect(retryHandler.isMaxRetriesExceeded()).toBe(false);
		});

		it('should return false when at max retries', () => {
			for (let i = 0; i < 5; i++) {
				retryHandler.incrementRetry();
			}
			// At 5, which equals maxRetries (5), so not exceeded
			expect(retryHandler.isMaxRetriesExceeded()).toBe(false);
		});

		it('should return true when exceeding max retries', () => {
			for (let i = 0; i <= 5; i++) {
				retryHandler.incrementRetry();
			}
			// At 6, which exceeds maxRetries (5)
			expect(retryHandler.isMaxRetriesExceeded()).toBe(true);
		});
	});

	describe('reset', () => {
		it('should reset retry count to 0', () => {
			retryHandler.incrementRetry();
			retryHandler.incrementRetry();
			expect(retryHandler.getRetryCount()).toBe(2);

			retryHandler.reset();
			expect(retryHandler.getRetryCount()).toBe(0);
		});

		it('should reset cleaned up state', () => {
			retryHandler.cleanup();
			expect(retryHandler.isCleanedUpState()).toBe(true);

			retryHandler.reset();
			expect(retryHandler.isCleanedUpState()).toBe(false);
		});
	});

	describe('cleanup', () => {
		it('should mark handler as cleaned up', () => {
			expect(retryHandler.isCleanedUpState()).toBe(false);

			retryHandler.cleanup();
			expect(retryHandler.isCleanedUpState()).toBe(true);
		});
	});

	describe('incrementRetry', () => {
		it('should increment retry count by 1', () => {
			expect(retryHandler.getRetryCount()).toBe(0);

			retryHandler.incrementRetry();
			expect(retryHandler.getRetryCount()).toBe(1);

			retryHandler.incrementRetry();
			expect(retryHandler.getRetryCount()).toBe(2);
		});
	});

	describe('getRetryDelay', () => {
		it('should return correct delay for first retry', () => {
			retryHandler.incrementRetry(); // retryCount = 1
			expect(retryHandler.getRetryDelay()).toBe(1000);
		});

		it('should return correct delay for second retry', () => {
			retryHandler.incrementRetry(); // 1
			retryHandler.incrementRetry(); // 2
			expect(retryHandler.getRetryDelay()).toBe(2000);
		});

		it('should return correct delay for third retry', () => {
			retryHandler.incrementRetry(); // 1
			retryHandler.incrementRetry(); // 2
			retryHandler.incrementRetry(); // 3
			expect(retryHandler.getRetryDelay()).toBe(4000);
		});

		it('should return correct delay for fourth retry', () => {
			for (let i = 0; i < 4; i++) {
				retryHandler.incrementRetry();
			}
			expect(retryHandler.getRetryDelay()).toBe(8000);
		});

		it('should return correct delay for fifth retry', () => {
			for (let i = 0; i < 5; i++) {
				retryHandler.incrementRetry();
			}
			expect(retryHandler.getRetryDelay()).toBe(16000);
		});
	});

	describe('scheduleRetry', () => {
		it('should schedule retry and return true', () => {
			const retryFn = vi.fn();

			const result = retryHandler.scheduleRetry(retryFn);

			expect(result).toBe(true);
			expect(retryHandler.getRetryCount()).toBe(1);
		});

		it('should call retry function after delay', () => {
			const retryFn = vi.fn();

			retryHandler.scheduleRetry(retryFn);

			// Not called immediately
			expect(retryFn).not.toHaveBeenCalled();

			// Called after delay (1000ms for first retry)
			vi.advanceTimersByTime(1000);
			expect(retryFn).toHaveBeenCalledTimes(1);
		});

		it('should use exponential backoff delays', async () => {
			const retryFn = vi.fn();

			// First retry - 1000ms
			retryHandler.scheduleRetry(retryFn);
			vi.advanceTimersByTime(1000);
			expect(retryFn).toHaveBeenCalledTimes(1);

			// Second retry - 2000ms
			retryHandler.scheduleRetry(retryFn);
			vi.advanceTimersByTime(2000);
			expect(retryFn).toHaveBeenCalledTimes(2);

			// Third retry - 4000ms
			retryHandler.scheduleRetry(retryFn);
			vi.advanceTimersByTime(4000);
			expect(retryFn).toHaveBeenCalledTimes(3);
		});

		it('should return false when max retries exceeded', () => {
			const retryFn = vi.fn();

			// Schedule 5 retries (max)
			for (let i = 0; i < 5; i++) {
				const result = retryHandler.scheduleRetry(retryFn);
				expect(result).toBe(true);
			}

			// 6th retry should fail
			const result = retryHandler.scheduleRetry(retryFn);
			expect(result).toBe(false);
		});

		it('should not call retry function if cleaned up during delay', () => {
			const retryFn = vi.fn();

			retryHandler.scheduleRetry(retryFn);

			// Cleanup before timeout fires
			vi.advanceTimersByTime(500);
			retryHandler.cleanup();

			// Advance past delay
			vi.advanceTimersByTime(1000);

			// Should not have been called
			expect(retryFn).not.toHaveBeenCalled();
		});

		it('should show toast warning with retry count', async () => {
			const { toast } = await import('$lib/stores/toast');
			const retryFn = vi.fn();

			retryHandler.scheduleRetry(retryFn);

			expect(toast.warning).toHaveBeenCalledWith('Reconnecting... (1/5)');
		});

		it('should log retry attempt', async () => {
			const { logger } = await import('$lib/utils/logger');
			const retryFn = vi.fn();

			retryHandler.scheduleRetry(retryFn);

			expect(logger.info).toHaveBeenCalledWith(
				'SSE connection failed, retrying',
				expect.objectContaining({
					attempt: 1,
					maxRetries: 5,
					delayMs: 1000
				})
			);
		});
	});

	describe('race condition prevention', () => {
		it('should prevent retry after cleanup', () => {
			const retryFn = vi.fn();

			// Schedule retry
			retryHandler.scheduleRetry(retryFn);

			// Immediately cleanup
			retryHandler.cleanup();

			// Advance past delay
			vi.advanceTimersByTime(2000);

			// Retry function should not be called
			expect(retryFn).not.toHaveBeenCalled();
		});

		it('should allow retry after reset', () => {
			const retryFn = vi.fn();

			// Cleanup
			retryHandler.cleanup();
			expect(retryHandler.isCleanedUpState()).toBe(true);

			// Reset
			retryHandler.reset();
			expect(retryHandler.isCleanedUpState()).toBe(false);

			// Schedule retry should work
			const result = retryHandler.scheduleRetry(retryFn);
			expect(result).toBe(true);

			vi.advanceTimersByTime(1000);
			expect(retryFn).toHaveBeenCalledTimes(1);
		});
	});

	describe('edge cases', () => {
		it('should handle multiple cleanup calls', () => {
			retryHandler.cleanup();
			retryHandler.cleanup();
			retryHandler.cleanup();

			expect(retryHandler.isCleanedUpState()).toBe(true);
		});

		it('should handle multiple reset calls', () => {
			retryHandler.incrementRetry();
			retryHandler.incrementRetry();

			retryHandler.reset();
			retryHandler.reset();
			retryHandler.reset();

			expect(retryHandler.getRetryCount()).toBe(0);
		});

		it('should handle rapid schedule/cleanup cycles', () => {
			const retryFn = vi.fn();

			// First cycle: schedule then cleanup before timer fires
			retryHandler.scheduleRetry(retryFn);
			retryHandler.cleanup(); // Mark as cleaned up - prevents callback

			// Advance past first delay (1000ms) - callback should NOT fire due to cleanup
			vi.advanceTimersByTime(1500);

			// First callback should not have been called due to cleanup
			expect(retryFn).not.toHaveBeenCalled();

			// Reset for second cycle
			retryHandler.reset();

			// Second cycle: schedule then cleanup before timer fires
			retryHandler.scheduleRetry(retryFn);
			retryHandler.cleanup(); // Mark as cleaned up again

			// Advance past second delay (2000ms) - callback should NOT fire
			vi.advanceTimersByTime(3000);

			// Still no calls because we cleaned up before timers fired
			expect(retryFn).not.toHaveBeenCalled();
		});
	});
});
