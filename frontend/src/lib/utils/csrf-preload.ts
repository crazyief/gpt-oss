/**
 * Preload CSRF token on app startup.
 *
 * This ensures the token is ready before the first API call,
 * improving UX by eliminating the initial token fetch delay.
 *
 * Non-blocking: App continues loading even if preload fails.
 */

import { csrfClient } from '$lib/services/core/csrf';
import { toast } from '$lib/stores/toast';
import { logger } from '$lib/utils/logger';

export async function preloadCsrfToken(): Promise<void> {
	try {
		const token = await csrfClient.getToken();
		logger.info('CSRF token preloaded successfully');
	} catch (error) {
		logger.error('CSRF token preload failed', { error });

		// Show warning toast (non-blocking)
		toast.warning('Security initialization delayed. First action may be slower.', 4000);

		// Token will be fetched on demand, so app still works
	}
}
