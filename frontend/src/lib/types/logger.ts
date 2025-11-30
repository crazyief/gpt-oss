/**
 * Logger type definitions
 *
 * Improved type safety for logging operations.
 */

/**
 * Log context data type
 *
 * Restricts context to serializable primitive types only.
 * Prevents logging functions, DOM nodes, or other non-serializable data.
 *
 * WHY restrict types:
 * - JSON serializable: Can send to remote logging service
 * - Type safety: Catch attempts to log non-primitive data at compile time
 * - Performance: Primitive types are fast to serialize
 *
 * Allowed types:
 * - string: IDs, names, descriptions
 * - number: Counts, IDs, metrics
 * - boolean: Flags, states
 * - null/undefined: Optional fields
 * - Error: Error objects (special handling for serialization)
 *
 * @example
 * const context: LogContext = {
 *   userId: 123,              // number ✅
 *   conversationId: '456',    // string ✅
 *   isStreaming: true,        // boolean ✅
 *   error: new Error('Oops'), // Error ✅
 *   timestamp: null           // null ✅
 * };
 */
export type LogContext = Record<
	string,
	string | number | boolean | null | undefined | Error
>;

/**
 * Log severity levels
 *
 * - debug: Detailed diagnostic info (development only)
 * - info: Important events (user actions, API calls)
 * - warn: Warning conditions (approaching limits, deprecated usage)
 * - error: Error conditions (API failures, exceptions)
 */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

/**
 * Structured log entry
 *
 * Used for both console logging and remote logging service.
 */
export interface LogEntry {
	/** ISO 8601 timestamp */
	timestamp: string;
	/** Log severity level */
	level: LogLevel;
	/** Human-readable message */
	message: string;
	/** Optional structured context data */
	context?: LogContext;
}
