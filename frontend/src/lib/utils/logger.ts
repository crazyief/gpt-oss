/**
 * Frontend logging utility
 *
 * Purpose: Structured logging with levels and environment-aware behavior
 *
 * Features:
 * - Development: Logs to browser console with colors
 * - Production: Can send to remote logging service (Stage 2+)
 * - Type-safe: TypeScript interfaces for log context
 * - Performance: No-op in production for debug logs
 *
 * Usage:
 * import { logger } from '$lib/utils/logger';
 *
 * logger.debug('User clicked button', { buttonId: 'submit' });
 * logger.info('Message sent successfully', { conversationId: 123 });
 * logger.warn('Token count approaching limit', { tokenCount: 21000 });
 * logger.error('Failed to fetch messages', { error: err.message });
 *
 * WHY dedicated logger instead of console.log:
 * - Production control: Can disable debug logs in production
 * - Remote logging: Can send errors to monitoring service
 * - Structured data: Context objects easier to analyze than string interpolation
 * - Search/filter: Log levels enable filtering in browser DevTools
 * - Compliance: IEC 62443 requires audit logging (future: send to backend)
 */

/**
 * Log severity levels
 *
 * debug: Detailed diagnostic info (development only)
 * info: Important events (user actions, API calls)
 * warn: Warning conditions (approaching limits, deprecated usage)
 * error: Error conditions (API failures, exceptions)
 */
type LogLevel = 'debug' | 'info' | 'warn' | 'error';

/**
 * Structured log entry
 *
 * WHY timestamp:
 * - Chronological ordering: Essential for debugging race conditions
 * - Performance analysis: Measure time between events
 * - ISO 8601 format: Standard, sortable, timezone-aware
 *
 * WHY optional context:
 * - Rich data: Include IDs, counts, states without string interpolation
 * - JSON serialization: Easy to send to remote logging service
 * - Type-safe: TypeScript validates context shape
 */
interface LogEntry {
	timestamp: string;
	level: LogLevel;
	message: string;
	context?: Record<string, any>;
}

/**
 * Logger class
 *
 * WHY class instead of plain functions:
 * - Encapsulation: isDevelopment check in one place
 * - Extensibility: Easy to add features (filtering, batching, remote sending)
 * - State: Can track log history for debugging
 * - Testability: Can mock logger instance in tests
 */
class Logger {
	private isDevelopment = import.meta.env.DEV;

	/**
	 * Log debug message (development only)
	 *
	 * Use for: Detailed diagnostic info, state dumps, tracing
	 *
	 * WHY no-op in production:
	 * - Performance: Reduce logging overhead
	 * - Security: Don't expose sensitive data in production console
	 * - Cleanliness: Production console stays clean
	 *
	 * @param message - Human-readable description
	 * @param context - Optional structured data (IDs, states, etc.)
	 */
	debug(message: string, context?: Record<string, any>) {
		// Skip debug logs in production (performance optimization)
		if (!this.isDevelopment) return;

		this.log('debug', message, context);
	}

	/**
	 * Log info message
	 *
	 * Use for: Important events, user actions, successful operations
	 * Examples: "User sent message", "Conversation created", "SSE connected"
	 *
	 * @param message - Human-readable description
	 * @param context - Optional structured data
	 */
	info(message: string, context?: Record<string, any>) {
		this.log('info', message, context);
	}

	/**
	 * Log warning message
	 *
	 * Use for: Warning conditions, approaching limits, deprecated usage
	 * Examples: "Token count at 90%", "Retry attempt 3/5", "Feature deprecated"
	 *
	 * @param message - Human-readable description
	 * @param context - Optional structured data
	 */
	warn(message: string, context?: Record<string, any>) {
		this.log('warn', message, context);
	}

	/**
	 * Log error message
	 *
	 * Use for: Error conditions, exceptions, failures
	 * Examples: "API request failed", "SSE connection error", "Parse error"
	 *
	 * @param message - Human-readable description
	 * @param context - Optional structured data (include error details)
	 */
	error(message: string, context?: Record<string, any>) {
		this.log('error', message, context);
	}

	/**
	 * Internal log implementation
	 *
	 * WHY private:
	 * - Encapsulation: Enforce using debug/info/warn/error methods
	 * - Consistency: All logs go through same pipeline
	 *
	 * WHY console[level]:
	 * - Browser DevTools: Automatic color coding and filtering
	 * - Stack traces: console.error shows stack automatically
	 * - Network tab: console.log doesn't trigger network requests
	 *
	 * @param level - Log severity level
	 * @param message - Human-readable description
	 * @param context - Optional structured data
	 */
	private log(level: LogLevel, message: string, context?: Record<string, any>) {
		const entry: LogEntry = {
			timestamp: new Date().toISOString(),
			level,
			message,
			context
		};

		// In development: log to console with colors
		if (this.isDevelopment) {
			// Map level to console method (debug → log, others match exactly)
			const consoleMethod = level === 'debug' ? 'log' : level;

			// Format: [LEVEL] Message {context}
			const prefix = `[${level.toUpperCase()}]`;

			// Log with context if provided
			if (context && Object.keys(context).length > 0) {
				console[consoleMethod](prefix, message, context);
			} else {
				console[consoleMethod](prefix, message);
			}
		}

		// In production: could send to remote logging service
		// FUTURE (Stage 2+): Implement remote logging
		// - Batch logs to reduce network requests
		// - Send errors to Sentry/LogRocket/etc.
		// - Include session ID, user ID for debugging
		// - Respect privacy: don't send sensitive data
		//
		// Example implementation:
		// if (!this.isDevelopment && level === 'error') {
		//   this.sendToRemote(entry);
		// }
	}

	/**
	 * FUTURE: Send log entry to remote logging service
	 *
	 * WHY remote logging:
	 * - Production debugging: See errors from real users
	 * - Monitoring: Track error rates, performance
	 * - Compliance: IEC 62443 requires audit logging
	 *
	 * Implementation considerations:
	 * - Batching: Send logs in batches to reduce requests
	 * - Retry: Handle network failures gracefully
	 * - Privacy: Filter sensitive data (passwords, tokens)
	 * - Rate limiting: Don't overwhelm server with logs
	 *
	 * @param entry - Structured log entry
	 */
	// private async sendToRemote(entry: LogEntry): Promise<void> {
	//   // TODO (Stage 2+): Implement remote logging
	//   // POST to /api/logs/frontend with entry
	// }
}

/**
 * Singleton logger instance
 *
 * WHY singleton:
 * - Convenience: Import once, use everywhere
 * - Consistency: All code uses same logger configuration
 * - State sharing: Could track log history globally
 *
 * Usage:
 * import { logger } from '$lib/utils/logger';
 * logger.info('User logged in', { userId: 123 });
 */
export const logger = new Logger();
