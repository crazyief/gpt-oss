/**
 * SSE retry handler with exponential backoff
 *
 * Purpose: Encapsulate retry logic to reduce sse-client.ts file size
 *
 * Features:
 * - Exponential backoff retry logic
 * - Configurable max retries and delays
 * - Cleanup race condition prevention
 *
 * Refactored from sse-client.ts to comply with 400-line limit
 */

import { APP_CONFIG } from '$lib/config';
import { logger } from '$lib/utils/logger';
import { toast } from '$lib/stores/toast';

/**
 * Retry configuration
 */
export interface RetryConfig {
	maxRetries: number;
	retryDelays: readonly number[] | number[];
}

/**
 * Retry handler class
 *
 * Manages retry logic with exponential backoff
 */
export class RetryHandler {
	private retryCount: number = 0;
	private isCleanedUp: boolean = false;
	private config: RetryConfig;
	private retryTimerId: ReturnType<typeof setTimeout> | null = null;

	constructor(config: RetryConfig = APP_CONFIG.sse) {
		this.config = config;
	}

	/**
	 * Get current retry count
	 */
	getRetryCount(): number {
		return this.retryCount;
	}

	/**
	 * Check if max retries exceeded
	 */
	isMaxRetriesExceeded(): boolean {
		return this.retryCount > this.config.maxRetries;
	}

	/**
	 * Check if cleaned up (prevents retry race condition)
	 */
	isCleanedUpState(): boolean {
		return this.isCleanedUp;
	}

	/**
	 * Reset retry state for new connection
	 *
	 * Clears pending retry timer and resets all state.
	 */
	reset(): void {
		// Cancel pending retry timer
		if (this.retryTimerId !== null) {
			clearTimeout(this.retryTimerId);
			this.retryTimerId = null;
		}

		this.retryCount = 0;
		this.isCleanedUp = false;
	}

	/**
	 * Mark as cleaned up and cancel pending retry timer
	 *
	 * MEMORY LEAK FIX: Previously only set flag, but didn't cancel timer.
	 * Now properly clears the setTimeout to release closure references.
	 */
	cleanup(): void {
		this.isCleanedUp = true;

		// Cancel pending retry timer to prevent memory leak
		if (this.retryTimerId !== null) {
			clearTimeout(this.retryTimerId);
			this.retryTimerId = null;
		}
	}

	/**
	 * Increment retry count and show user feedback
	 */
	incrementRetry(): void {
		this.retryCount++;
	}

	/**
	 * Get delay for current retry attempt
	 */
	getRetryDelay(): number {
		return this.config.retryDelays[this.retryCount - 1];
	}

	/**
	 * Schedule retry with exponential backoff
	 *
	 * @param retryFn - Function to call for retry
	 * @returns true if retry scheduled, false if max retries exceeded
	 */
	scheduleRetry(retryFn: () => void): boolean {
		this.incrementRetry();

		if (this.isMaxRetriesExceeded()) {
			return false; // Max retries exceeded
		}

		const delay = this.getRetryDelay();

		// Show retry message to user
		logger.info('SSE connection failed, retrying', {
			attempt: this.retryCount,
			maxRetries: this.config.maxRetries,
			delayMs: delay
		});

		toast.warning(`Reconnecting... (${this.retryCount}/${this.config.maxRetries})`);

		// Schedule retry and store timer ID for cleanup
		this.retryTimerId = setTimeout(() => {
			this.retryTimerId = null; // Clear reference after timer fires

			// Check if cleaned up during retry delay
			if (this.isCleanedUp) {
				return; // Don't retry if already cleaned up
			}

			retryFn();
		}, delay);

		return true; // Retry scheduled
	}
}
