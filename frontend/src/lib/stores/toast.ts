/**
 * Toast notification store
 *
 * Purpose: Provide user-facing error/success/warning messages
 *
 * Features:
 * - Success, error, warning, info toast types
 * - Auto-dismiss with configurable duration
 * - Rich text support (HTML content)
 * - Accessible (ARIA labels)
 * - Position control (top-right by default)
 *
 * Design decisions:
 * - Wraps @zerodevx/svelte-toast for consistent API
 * - Predefined themes for each toast type
 * - Default durations based on message urgency
 *
 * WHY wrap library instead of using directly:
 * - Consistent API: All components use same toast() function signature
 * - Easy migration: Can swap toast library without changing component code
 * - Customization: Apply project-specific theming in one place
 * - Type safety: TypeScript types for toast options
 */

import { toast as svelteToast } from '@zerodevx/svelte-toast';

/**
 * Toast type enumeration
 */
export type ToastType = 'success' | 'error' | 'warning' | 'info';

/**
 * Toast theme options type
 * (Library doesn't export this type, so we define it locally)
 */
interface ToastThemeOptions {
	theme?: Record<string, string>;
	duration?: number;
	initial?: number;
}

/**
 * Toast theme configuration
 *
 * WHY specific colors chosen:
 * - Success (green): Universal positive feedback color
 * - Error (red): Universal danger/error color
 * - Warning (amber): Standard warning color (not red = not critical)
 * - Info (blue): Neutral informational color
 *
 * Colors match TailwindCSS defaults for consistency
 */
const themes: Record<ToastType, ToastThemeOptions> = {
	success: {
		theme: {
			'--toastBackground': '#10b981', // green-500
			'--toastColor': '#ffffff',
			'--toastBarBackground': '#059669' // green-600
		}
	},
	error: {
		theme: {
			'--toastBackground': '#ef4444', // red-500
			'--toastColor': '#ffffff',
			'--toastBarBackground': '#dc2626' // red-600
		}
	},
	warning: {
		theme: {
			'--toastBackground': '#f59e0b', // amber-500
			'--toastColor': '#ffffff',
			'--toastBarBackground': '#d97706' // amber-600
		}
	},
	info: {
		theme: {
			'--toastBackground': '#3b82f6', // blue-500
			'--toastColor': '#ffffff',
			'--toastBarBackground': '#2563eb' // blue-600
		}
	}
};

/**
 * Default durations for each toast type
 *
 * WHY different durations:
 * - Success: 3s = Quick confirmation, user can read and move on
 * - Error: 5s = More time to read error message (often longer)
 * - Warning: 4s = Between success and error
 * - Info: 3s = Quick informational message
 */
const defaultDurations: Record<ToastType, number> = {
	success: 3000,
	error: 5000,
	warning: 4000,
	info: 3000
};

/**
 * Show success toast
 *
 * Use for:
 * - Successful CRUD operations (created, updated, deleted)
 * - Successful API calls
 * - Confirmation of user actions
 *
 * @param message - Toast message text
 * @param duration - Auto-dismiss duration in milliseconds (default: 3000)
 * @returns Toast ID (can be used to manually dismiss)
 */
export function success(message: string, duration?: number): number {
	const actualDuration = duration ?? defaultDurations.success;
	const id = svelteToast.push(message, {
		...themes.success,
		duration: actualDuration
	});
	// Manual auto-dismiss as fallback (library auto-dismiss may not work in all cases)
	setTimeout(() => {
		svelteToast.pop(id);
	}, actualDuration);
	return id;
}

/**
 * Show error toast
 *
 * Use for:
 * - API errors (4xx, 5xx)
 * - Validation errors
 * - Network errors
 * - Failed operations
 *
 * @param message - Error message text
 * @param duration - Auto-dismiss duration in milliseconds (default: 5000)
 * @returns Toast ID (can be used to manually dismiss)
 */
export function error(message: string, duration?: number): number {
	const actualDuration = duration ?? defaultDurations.error;
	const id = svelteToast.push(message, {
		...themes.error,
		duration: actualDuration
	});
	// Manual auto-dismiss as fallback
	setTimeout(() => {
		svelteToast.pop(id);
	}, actualDuration);
	return id;
}

/**
 * Show warning toast
 *
 * Use for:
 * - Non-critical issues
 * - Validation warnings
 * - Deprecated features
 * - Soft limits exceeded
 *
 * @param message - Warning message text
 * @param duration - Auto-dismiss duration in milliseconds (default: 4000)
 * @returns Toast ID (can be used to manually dismiss)
 */
export function warning(message: string, duration?: number): number {
	const actualDuration = duration ?? defaultDurations.warning;
	const id = svelteToast.push(message, {
		...themes.warning,
		duration: actualDuration
	});
	// Manual auto-dismiss as fallback
	setTimeout(() => {
		svelteToast.pop(id);
	}, actualDuration);
	return id;
}

/**
 * Show info toast
 *
 * Use for:
 * - Informational messages
 * - Tips and hints
 * - Non-critical notifications
 *
 * @param message - Info message text
 * @param duration - Auto-dismiss duration in milliseconds (default: 3000)
 * @returns Toast ID (can be used to manually dismiss)
 */
export function info(message: string, duration?: number): number {
	const actualDuration = duration ?? defaultDurations.info;
	const id = svelteToast.push(message, {
		...themes.info,
		duration: actualDuration
	});
	// Manual auto-dismiss as fallback
	setTimeout(() => {
		svelteToast.pop(id);
	}, actualDuration);
	return id;
}

/**
 * Dismiss toast by ID
 *
 * Use for:
 * - Manually dismissing long-lived toasts
 * - Dismissing all toasts on navigation
 *
 * @param id - Toast ID returned from success/error/warning/info
 */
export function dismiss(id: number): void {
	svelteToast.pop(id);
}

/**
 * Dismiss all active toasts
 *
 * Use for:
 * - Page navigation (clear old toasts)
 * - Modal close (clear context-specific toasts)
 * - Logout (clear all notifications)
 */
export function dismissAll(): void {
	svelteToast.pop(0); // 0 = dismiss all
}

/**
 * Toast store object
 *
 * Provides convenient import pattern:
 * import { toast } from '$lib/stores/toast';
 * toast.success('Project created!');
 * toast.error('Failed to save');
 */
export const toast = {
	success,
	error,
	warning,
	info,
	dismiss,
	dismissAll
};

/**
 * Helper: Get user-friendly error message from API error
 *
 * Translates HTTP status codes and error objects into user-friendly messages
 *
 * WHY centralize error message formatting:
 * - Consistency: All error messages follow same format
 * - Localization: Single place to add i18n in future
 * - User-friendly: Technical errors → readable messages
 *
 * @param error - Error object or status code
 * @returns User-friendly error message
 */
export function getErrorMessage(error: any): string {
	// HTTP status code error messages
	if (typeof error === 'number') {
		switch (error) {
			case 400:
				return 'Invalid request. Please check your input.';
			case 401:
				return 'Authentication required. Please log in.';
			case 403:
				return 'Access denied. You do not have permission.';
			case 404:
				return 'Resource not found.';
			case 409:
				return 'Conflict. Resource already exists.';
			case 413:
				return 'Request too large. Please reduce file size.';
			case 422:
				return 'Validation failed. Please check your input.';
			case 429:
				return 'Too many requests. Please slow down.';
			case 500:
				return 'Server error. Please try again later.';
			case 502:
				return 'Bad gateway. Server is temporarily unavailable.';
			case 503:
				return 'Service unavailable. Please try again later.';
			case 504:
				return 'Gateway timeout. Request took too long.';
			default:
				return error >= 500
					? 'Server error. Please try again later.'
					: 'An error occurred. Please try again.';
		}
	}

	// Error object with status property
	if (error?.status) {
		return getErrorMessage(error.status);
	}

	// Error object with detail property (FastAPI format)
	if (error?.detail) {
		return typeof error.detail === 'string' ? error.detail : 'An error occurred.';
	}

	// Error object with message property
	if (error?.message) {
		return error.message;
	}

	// String error
	if (typeof error === 'string') {
		return error;
	}

	// Unknown error format
	return 'An unexpected error occurred.';
}
