/**
 * Base API request handler
 *
 * Shared fetch wrapper with automatic error handling and toast integration.
 * Translates HTTP errors to user-friendly messages and shows error toasts.
 */

import { API_BASE_URL } from '$lib/config';
import { toast } from '$lib/stores/toast';
import { csrfClient } from '../core/csrf';

/**
 * API error response structure
 */
export interface ApiError {
	detail?: string;
	error_type?: string;
	[key: string]: unknown;
}

/**
 * API request options (extends RequestInit)
 */
export interface ApiRequestOptions extends RequestInit {
	/** Skip automatic error toast (default: false) */
	skipErrorToast?: boolean;
	/** Custom error message to override defaults */
	customErrorMessage?: string;
	/** Skip CSRF token injection (default: false) */
	skipCsrf?: boolean;
}

/**
 * Build full API URL from endpoint.
 */
function buildUrl(endpoint: string): string {
	return endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
}

/**
 * Inject CSRF token for state-changing requests.
 */
async function injectCsrfToken(
	method: string,
	headers: HeadersInit = {},
	skipCsrf: boolean = false
): Promise<HeadersInit> {
	const needsCsrf = ['POST', 'PUT', 'DELETE', 'PATCH'].includes(method.toUpperCase());

	if (needsCsrf && !skipCsrf) {
		try {
			const csrfToken = await csrfClient.getToken();
			return {
				...headers,
				'X-CSRF-Token': csrfToken
			};
		} catch (error) {
			console.error('Failed to get CSRF token:', error);
			throw new Error('CSRF token fetch failed');
		}
	}

	return headers;
}

/**
 * Handle 403 CSRF errors with token refresh and retry.
 */
async function handleCsrfError<T>(
	url: string,
	options: RequestInit,
	needsCsrf: boolean
): Promise<T | null> {
	if (!needsCsrf) return null;

	console.log('CSRF token expired, refreshing...');

	try {
		const newToken = await csrfClient.refreshToken();

		// Retry request with new token
		const retryOptions = {
			...options,
			headers: {
				...options.headers,
				'X-CSRF-Token': newToken
			}
		};

		const retryResponse = await fetch(url, retryOptions);

		if (retryResponse.ok) {
			return await retryResponse.json();
		}
	} catch (retryError) {
		console.error('CSRF token refresh failed:', retryError);
	}

	return null;
}

/**
 * Make an API request with automatic error handling.
 *
 * @param endpoint - API endpoint (relative or absolute URL)
 * @param options - Request options (extends fetch RequestInit)
 * @returns Promise resolving to typed response data
 */
export async function apiRequest<T>(
	endpoint: string,
	options: ApiRequestOptions = {}
): Promise<T> {
	const { skipErrorToast, customErrorMessage, skipCsrf, ...fetchOptions } = options;
	const url = buildUrl(endpoint);
	const method = (fetchOptions.method || 'GET').toUpperCase();
	const needsCsrf = ['POST', 'PUT', 'DELETE', 'PATCH'].includes(method);

	try {
		fetchOptions.headers = await injectCsrfToken(method, fetchOptions.headers, skipCsrf);
	} catch (error) {
		if (!skipErrorToast) toast.error('Security token unavailable. Please refresh the page.');
		throw error;
	}

	try {
		const response = await fetch(url, fetchOptions);

		if (!response.ok) {
			if (response.status === 403) {
				const errorData: ApiError = await response.json().catch(() => ({}));
				if (errorData.detail?.includes('CSRF')) {
					const retryResult = await handleCsrfError<T>(url, fetchOptions, needsCsrf);
					if (retryResult) return retryResult;
				}
			}

			const error: ApiError = await response.json().catch(() => ({
				detail: response.statusText
			}));
			const message = customErrorMessage || getErrorMessage(response.status, error);
			if (!skipErrorToast) toast.error(message);
			throw new Error(error.detail || message);
		}

		// Handle 204 No Content (no response body)
	if (response.status === 204) {
		return undefined as T;
	}

	return await response.json();
	} catch (err) {
		if (err instanceof TypeError) {
			const message = 'Network error. Please check your connection.';
			if (!skipErrorToast) toast.error(message);
			throw new Error(message);
		}
		throw err;
	}
}

/**
 * Get user-friendly error message for HTTP status code
 *
 * @param status - HTTP status code
 * @param error - Error object from API response
 * @returns User-friendly error message
 */
function getErrorMessage(status: number, error: ApiError): string {
	// If error.detail exists, prefer it over generic message
	const detail = error?.detail;

	// Map HTTP status codes to user-friendly messages
	const statusMessages: Record<number, string> = {
		400: 'Invalid request. Please check your input.',
		401: 'Authentication required. Please log in.',
		403: 'Access denied. You do not have permission.',
		404: 'Resource not found.',
		409: 'Conflict. Resource already exists.',
		413: 'Request too large. Please reduce file size.',
		422: 'Validation failed. Please check your input.',
		429: 'Too many requests. Please slow down.',
		500: 'Server error. Please try again later.',
		502: 'Bad gateway. Server is temporarily unavailable.',
		503: 'Service unavailable. Please try again later.',
		504: 'Gateway timeout. Request took too long.'
	};

	// Return detail if available, otherwise status message, otherwise generic message
	return detail || statusMessages[status] || 'An error occurred. Please try again.';
}
