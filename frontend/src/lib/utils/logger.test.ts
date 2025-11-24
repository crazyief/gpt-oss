/**
 * Unit tests for logger utility
 *
 * Tests logging functionality with environment-aware behavior.
 * Follows AAA pattern (Arrange, Act, Assert) for clarity.
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { logger } from './logger';

describe('logger.ts - Logger', () => {
	// Store original console methods
	const originalConsole = {
		log: console.log,
		info: console.info,
		warn: console.warn,
		error: console.error
	};

	beforeEach(() => {
		// Mock console methods
		console.log = vi.fn();
		console.info = vi.fn();
		console.warn = vi.fn();
		console.error = vi.fn();
	});

	afterEach(() => {
		// Restore original console methods
		console.log = originalConsole.log;
		console.info = originalConsole.info;
		console.warn = originalConsole.warn;
		console.error = originalConsole.error;
	});

	it('debug() logs in development mode', () => {
		// Arrange
		const message = 'Debug message';
		const context = { userId: 123 };

		// Act
		logger.debug(message, context);

		// Assert
		// In Vitest, import.meta.env.DEV is true by default
		expect(console.log).toHaveBeenCalledWith('[DEBUG]', message, context);
	});

	it('info() logs in all environments', () => {
		// Arrange
		const message = 'Info message';
		const context = { action: 'user_login' };

		// Act
		logger.info(message, context);

		// Assert
		expect(console.info).toHaveBeenCalledWith('[INFO]', message, context);
	});

	it('warn() logs warnings', () => {
		// Arrange
		const message = 'Warning message';
		const context = { tokenCount: 21000 };

		// Act
		logger.warn(message, context);

		// Assert
		expect(console.warn).toHaveBeenCalledWith('[WARN]', message, context);
	});

	it('error() logs errors', () => {
		// Arrange
		const message = 'Error message';
		const context = { errorCode: 500, endpoint: '/api/chat' };

		// Act
		logger.error(message, context);

		// Assert
		expect(console.error).toHaveBeenCalledWith('[ERROR]', message, context);
	});

	it('logs without context when not provided', () => {
		// Arrange
		const message = 'Simple log message';

		// Act
		logger.info(message);

		// Assert
		expect(console.info).toHaveBeenCalledWith('[INFO]', message);
	});
});
