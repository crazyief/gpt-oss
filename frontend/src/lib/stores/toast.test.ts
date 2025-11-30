/**
 * Unit tests for toast store
 *
 * Tests: Toast functions (success, error, warning, info), error message formatting
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock @zerodevx/svelte-toast BEFORE imports
vi.mock('@zerodevx/svelte-toast', () => ({
	toast: {
		push: vi.fn(() => 1),
		pop: vi.fn()
	}
}));

import { toast as svelteToast } from '@zerodevx/svelte-toast';
import { toast, getErrorMessage } from './toast';

const mockPush = svelteToast.push as ReturnType<typeof vi.fn>;
const mockPop = svelteToast.pop as ReturnType<typeof vi.fn>;

// Mock setTimeout to test auto-dismiss
vi.useFakeTimers();

describe('toast store', () => {
	beforeEach(() => {
		mockPush.mockClear();
		mockPop.mockClear();
		vi.clearAllTimers();
	});

	afterEach(() => {
		vi.clearAllTimers();
	});

	describe('success', () => {
		it('should call toast.push with success theme', () => {
			toast.success('Success message');

			expect(mockPush).toHaveBeenCalledWith(
				'Success message',
				expect.objectContaining({
					theme: expect.objectContaining({
						'--toastBackground': '#10b981',
						'--toastColor': '#ffffff',
						'--toastBarBackground': '#059669'
					})
				})
			);
		});

		it('should use default duration of 3000ms', () => {
			toast.success('Success message');

			expect(mockPush).toHaveBeenCalledWith(
				'Success message',
				expect.objectContaining({
					duration: 3000
				})
			);
		});

		it('should support custom duration', () => {
			toast.success('Success message', 5000);

			expect(mockPush).toHaveBeenCalledWith(
				'Success message',
				expect.objectContaining({
					duration: 5000
				})
			);
		});

		it('should auto-dismiss after duration', () => {
			const toastId = toast.success('Success message', 3000);

			expect(mockPop).not.toHaveBeenCalled();

			vi.advanceTimersByTime(3000);

			expect(mockPop).toHaveBeenCalledWith(toastId);
		});

		it('should return toast ID', () => {
			const id = toast.success('Success message');
			expect(id).toBe(1);
		});
	});

	describe('error', () => {
		it('should call toast.push with error theme', () => {
			toast.error('Error message');

			expect(mockPush).toHaveBeenCalledWith(
				'Error message',
				expect.objectContaining({
					theme: expect.objectContaining({
						'--toastBackground': '#ef4444',
						'--toastColor': '#ffffff',
						'--toastBarBackground': '#dc2626'
					})
				})
			);
		});

		it('should use default duration of 5000ms', () => {
			toast.error('Error message');

			expect(mockPush).toHaveBeenCalledWith(
				'Error message',
				expect.objectContaining({
					duration: 5000
				})
			);
		});

		it('should support custom duration', () => {
			toast.error('Error message', 8000);

			expect(mockPush).toHaveBeenCalledWith(
				'Error message',
				expect.objectContaining({
					duration: 8000
				})
			);
		});

		it('should auto-dismiss after duration', () => {
			const toastId = toast.error('Error message', 5000);

			vi.advanceTimersByTime(5000);

			expect(mockPop).toHaveBeenCalledWith(toastId);
		});
	});

	describe('warning', () => {
		it('should call toast.push with warning theme', () => {
			toast.warning('Warning message');

			expect(mockPush).toHaveBeenCalledWith(
				'Warning message',
				expect.objectContaining({
					theme: expect.objectContaining({
						'--toastBackground': '#f59e0b',
						'--toastColor': '#ffffff',
						'--toastBarBackground': '#d97706'
					})
				})
			);
		});

		it('should use default duration of 4000ms', () => {
			toast.warning('Warning message');

			expect(mockPush).toHaveBeenCalledWith(
				'Warning message',
				expect.objectContaining({
					duration: 4000
				})
			);
		});

		it('should auto-dismiss after duration', () => {
			const toastId = toast.warning('Warning message', 4000);

			vi.advanceTimersByTime(4000);

			expect(mockPop).toHaveBeenCalledWith(toastId);
		});
	});

	describe('info', () => {
		it('should call toast.push with info theme', () => {
			toast.info('Info message');

			expect(mockPush).toHaveBeenCalledWith(
				'Info message',
				expect.objectContaining({
					theme: expect.objectContaining({
						'--toastBackground': '#3b82f6',
						'--toastColor': '#ffffff',
						'--toastBarBackground': '#2563eb'
					})
				})
			);
		});

		it('should use default duration of 3000ms', () => {
			toast.info('Info message');

			expect(mockPush).toHaveBeenCalledWith(
				'Info message',
				expect.objectContaining({
					duration: 3000
				})
			);
		});

		it('should auto-dismiss after duration', () => {
			const toastId = toast.info('Info message', 3000);

			vi.advanceTimersByTime(3000);

			expect(mockPop).toHaveBeenCalledWith(toastId);
		});
	});

	describe('dismiss', () => {
		it('should call toast.pop with toast ID', () => {
			toast.dismiss(42);

			expect(mockPop).toHaveBeenCalledWith(42);
		});
	});

	describe('dismissAll', () => {
		it('should call toast.pop with ID 0', () => {
			toast.dismissAll();

			expect(mockPop).toHaveBeenCalledWith(0);
		});
	});

	describe('getErrorMessage', () => {
		describe('HTTP status codes', () => {
			it('should handle 400 Bad Request', () => {
				const message = getErrorMessage(400);
				expect(message).toBe('Invalid request. Please check your input.');
			});

			it('should handle 401 Unauthorized', () => {
				const message = getErrorMessage(401);
				expect(message).toBe('Authentication required. Please log in.');
			});

			it('should handle 403 Forbidden', () => {
				const message = getErrorMessage(403);
				expect(message).toBe('Access denied. You do not have permission.');
			});

			it('should handle 404 Not Found', () => {
				const message = getErrorMessage(404);
				expect(message).toBe('Resource not found.');
			});

			it('should handle 409 Conflict', () => {
				const message = getErrorMessage(409);
				expect(message).toBe('Conflict. Resource already exists.');
			});

			it('should handle 413 Payload Too Large', () => {
				const message = getErrorMessage(413);
				expect(message).toBe('Request too large. Please reduce file size.');
			});

			it('should handle 422 Unprocessable Entity', () => {
				const message = getErrorMessage(422);
				expect(message).toBe('Validation failed. Please check your input.');
			});

			it('should handle 429 Too Many Requests', () => {
				const message = getErrorMessage(429);
				expect(message).toBe('Too many requests. Please slow down.');
			});

			it('should handle 500 Internal Server Error', () => {
				const message = getErrorMessage(500);
				expect(message).toBe('Server error. Please try again later.');
			});

			it('should handle 502 Bad Gateway', () => {
				const message = getErrorMessage(502);
				expect(message).toBe('Bad gateway. Server is temporarily unavailable.');
			});

			it('should handle 503 Service Unavailable', () => {
				const message = getErrorMessage(503);
				expect(message).toBe('Service unavailable. Please try again later.');
			});

			it('should handle 504 Gateway Timeout', () => {
				const message = getErrorMessage(504);
				expect(message).toBe('Gateway timeout. Request took too long.');
			});

			it('should handle unknown 5xx error', () => {
				const message = getErrorMessage(599);
				expect(message).toBe('Server error. Please try again later.');
			});

			it('should handle unknown 4xx error', () => {
				const message = getErrorMessage(418);
				expect(message).toBe('An error occurred. Please try again.');
			});
		});

		describe('error objects', () => {
			it('should extract status from error object', () => {
				const error = { status: 404 };
				const message = getErrorMessage(error);
				expect(message).toBe('Resource not found.');
			});

			it('should extract detail from FastAPI error', () => {
				const error = { detail: 'Custom error message' };
				const message = getErrorMessage(error);
				expect(message).toBe('Custom error message');
			});

			it('should handle non-string detail', () => {
				const error = { detail: { code: 'ERROR', message: 'Complex error' } };
				const message = getErrorMessage(error);
				expect(message).toBe('An error occurred.');
			});

			it('should extract message from error object', () => {
				const error = { message: 'Error message from exception' };
				const message = getErrorMessage(error);
				expect(message).toBe('Error message from exception');
			});

			it('should prioritize detail over message', () => {
				const error = {
					detail: 'Detail message',
					message: 'Generic message'
				};
				const message = getErrorMessage(error);
				expect(message).toBe('Detail message');
			});

			it('should prioritize status over detail', () => {
				const error = {
					status: 404,
					detail: 'Some detail'
				};
				const message = getErrorMessage(error);
				expect(message).toBe('Resource not found.');
			});
		});

		describe('string errors', () => {
			it('should return string error directly', () => {
				const message = getErrorMessage('Custom error string');
				expect(message).toBe('Custom error string');
			});
		});

		describe('unknown errors', () => {
			it('should handle null error', () => {
				const message = getErrorMessage(null);
				expect(message).toBe('An unexpected error occurred.');
			});

			it('should handle undefined error', () => {
				const message = getErrorMessage(undefined);
				expect(message).toBe('An unexpected error occurred.');
			});

			it('should handle empty object error', () => {
				const message = getErrorMessage({});
				expect(message).toBe('An unexpected error occurred.');
			});

			it('should handle boolean error', () => {
				const message = getErrorMessage(true);
				expect(message).toBe('An unexpected error occurred.');
			});

			it('should handle array error', () => {
				const message = getErrorMessage([]);
				expect(message).toBe('An unexpected error occurred.');
			});
		});
	});

	describe('toast object', () => {
		it('should have success method', () => {
			expect(toast.success).toBeDefined();
			expect(typeof toast.success).toBe('function');
		});

		it('should have error method', () => {
			expect(toast.error).toBeDefined();
			expect(typeof toast.error).toBe('function');
		});

		it('should have warning method', () => {
			expect(toast.warning).toBeDefined();
			expect(typeof toast.warning).toBe('function');
		});

		it('should have info method', () => {
			expect(toast.info).toBeDefined();
			expect(typeof toast.info).toBe('function');
		});

		it('should have dismiss method', () => {
			expect(toast.dismiss).toBeDefined();
			expect(typeof toast.dismiss).toBe('function');
		});

		it('should have dismissAll method', () => {
			expect(toast.dismissAll).toBeDefined();
			expect(typeof toast.dismissAll).toBe('function');
		});
	});
});
