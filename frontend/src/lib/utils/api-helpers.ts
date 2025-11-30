/**
 * API helper utilities
 *
 * Shared patterns and constants for API client functions.
 * Reduces code duplication across API service files.
 */

import { toast } from '$lib/stores/toast';

/**
 * Standard success messages for CRUD operations
 *
 * WHY centralize messages:
 * - Consistency: All success messages follow same format
 * - Maintainability: Change message format in one place
 * - Localization ready: Single place to add i18n
 */
export const API_SUCCESS_MESSAGES = {
	// Projects
	projectCreated: 'Project created successfully',
	projectUpdated: 'Project updated successfully',
	projectDeleted: 'Project deleted successfully',

	// Conversations
	conversationCreated: 'Conversation created successfully',
	conversationUpdated: 'Conversation updated successfully',
	conversationDeleted: 'Conversation deleted successfully',

	// Messages
	messageCreated: 'Message sent successfully',
	messageUpdated: 'Message updated successfully',

	// Documents
	documentsUploaded: (count: number): string => `${count} file(s) uploaded successfully`,
	documentsFailed: (count: number): string => `${count} file(s) failed to upload`,
	documentDeleted: 'Document deleted successfully',
	downloadStarted: 'Download started'
} as const;

/**
 * Show success toast with optional custom message
 *
 * @param message - Success message (from API_SUCCESS_MESSAGES or custom)
 * @param duration - Optional custom duration (default: 3000ms)
 * @returns Toast ID
 *
 * @example
 * showSuccessToast(API_SUCCESS_MESSAGES.projectCreated);
 * showSuccessToast('Custom success message', 5000);
 */
export function showSuccessToast(message: string, duration?: number): number {
	return toast.success(message, duration);
}

/**
 * Show error toast with optional custom message
 *
 * @param message - Error message
 * @param duration - Optional custom duration (default: 5000ms)
 * @returns Toast ID
 *
 * @example
 * showErrorToast('Failed to save project');
 */
export function showErrorToast(message: string, duration?: number): number {
	return toast.error(message, duration);
}

/**
 * Extract error message from Error object or unknown error
 *
 * @param error - Error object, string, or unknown type
 * @returns User-friendly error message
 *
 * @example
 * try { ... } catch (err) {
 *   showErrorToast(extractErrorMessage(err));
 * }
 */
export function extractErrorMessage(error: unknown): string {
	if (error instanceof Error) {
		return error.message;
	}
	if (typeof error === 'string') {
		return error;
	}
	return 'An unexpected error occurred';
}
