/**
 * Unit tests for date utility functions
 *
 * CRITICAL: Tests timezone handling for GMT+8 users
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { parseUTCTimestamp, formatRelativeTime, formatTime, formatDateTime } from './date';

describe('parseUTCTimestamp', () => {
	it('should parse timezone-aware timestamps correctly', () => {
		const utcTimestamp = '2025-11-23T03:10:00Z';
		const date = parseUTCTimestamp(utcTimestamp);

		// Should parse as UTC (3:10 AM UTC)
		expect(date.getUTCHours()).toBe(3);
		expect(date.getUTCMinutes()).toBe(10);
	});

	it('should parse naive timestamps as UTC (append Z)', () => {
		const naiveTimestamp = '2025-11-23T03:10:00'; // No timezone info
		const date = parseUTCTimestamp(naiveTimestamp);

		// Should be treated as UTC (3:10 AM UTC)
		expect(date.getUTCHours()).toBe(3);
		expect(date.getUTCMinutes()).toBe(10);
	});

	it('should parse timestamps with offset correctly', () => {
		const offsetTimestamp = '2025-11-23T11:10:00+08:00'; // GMT+8
		const date = parseUTCTimestamp(offsetTimestamp);

		// 11:10 AM GMT+8 = 3:10 AM UTC
		expect(date.getUTCHours()).toBe(3);
		expect(date.getUTCMinutes()).toBe(10);
	});

	it('should handle negative offsets', () => {
		const negativeOffset = '2025-11-23T01:10:00-02:00'; // GMT-2
		const date = parseUTCTimestamp(negativeOffset);

		// 1:10 AM GMT-2 = 3:10 AM UTC
		expect(date.getUTCHours()).toBe(3);
		expect(date.getUTCMinutes()).toBe(10);
	});
});

describe('formatRelativeTime', () => {
	let originalDate: typeof Date;
	const mockCurrentTime = new Date('2025-11-23T03:15:00Z');

	beforeEach(() => {
		// Mock Date constructor to return fixed timestamp when called without arguments
		originalDate = global.Date;
		global.Date = class extends Date {
			constructor(...args: any[]) {
				if (args.length === 0) {
					// new Date() returns mocked current time
					super(mockCurrentTime.getTime());
				} else {
					// new Date(timestamp) works normally
					super(...args as []);
				}
			}

			static now() {
				return mockCurrentTime.getTime();
			}
		} as any;
	});

	afterEach(() => {
		global.Date = originalDate;
	});

	it('should return "Just now" for very recent timestamps', () => {
		// 30 seconds ago (current time - 30s)
		const timestamp = '2025-11-23T03:14:30Z';
		expect(formatRelativeTime(timestamp)).toBe('Just now');
	});

	it('should return "5m ago" for 5 minutes', () => {
		// 5 minutes ago
		const timestamp = '2025-11-23T03:10:00Z';
		expect(formatRelativeTime(timestamp)).toBe('5m ago');
	});

	it('should return "2h ago" for 2 hours', () => {
		// 2 hours ago
		const timestamp = '2025-11-23T01:15:00Z';
		expect(formatRelativeTime(timestamp)).toBe('2h ago');
	});

	it('should return "3d ago" for 3 days', () => {
		// 3 days ago
		const timestamp = '2025-11-20T03:15:00Z';
		expect(formatRelativeTime(timestamp)).toBe('3d ago');
	});

	it('should return "2w ago" for 2 weeks', () => {
		// 14 days ago
		const timestamp = '2025-11-09T03:15:00Z';
		expect(formatRelativeTime(timestamp)).toBe('2w ago');
	});

	it('should return "2mo ago" for 2 months', () => {
		// 60 days ago
		const timestamp = '2025-09-24T03:15:00Z';
		expect(formatRelativeTime(timestamp)).toBe('2mo ago');
	});

	it('should handle naive timestamps correctly (BUG FIX)', () => {
		// This is the critical test for the timezone bug
		// Backend sends: "2025-11-23T03:10:00" (no Z)
		// This should be interpreted as UTC, not local time
		const naiveTimestamp = '2025-11-23T03:10:00'; // 5 minutes ago (UTC)

		// WITHOUT FIX: GMT+8 user would see "8h ago" (wrong!)
		// WITH FIX: Should see "5m ago" (correct!)
		expect(formatRelativeTime(naiveTimestamp)).toBe('5m ago');
	});

	it('should return "No messages" for null', () => {
		expect(formatRelativeTime(null)).toBe('No messages');
	});

	it('should handle future timestamps gracefully', () => {
		// Future timestamp (clock skew or timezone bug)
		const futureTimestamp = '2025-11-23T04:00:00Z';
		expect(formatRelativeTime(futureTimestamp)).toBe('Just now');
	});
});

describe('formatTime', () => {
	it('should format time as HH:MM in local timezone', () => {
		// 3:10 AM UTC
		const timestamp = '2025-11-23T03:10:00Z';
		const formatted = formatTime(timestamp);

		// Result depends on local timezone (test runner's timezone)
		// Format should be HH:MM (e.g., "11:10" for GMT+8, "03:10" for GMT+0)
		expect(formatted).toMatch(/^\d{2}:\d{2}$/);
	});

	it('should handle naive timestamps correctly', () => {
		const naiveTimestamp = '2025-11-23T03:10:00';
		const formatted = formatTime(naiveTimestamp);

		// Should treat as UTC and convert to local time
		expect(formatted).toMatch(/^\d{2}:\d{2}$/);
	});
});

describe('formatDateTime', () => {
	it('should format as YYYY-MM-DD HH:MM in local timezone', () => {
		const timestamp = '2025-11-23T03:10:00Z';
		const formatted = formatDateTime(timestamp);

		// Format: YYYY-MM-DD HH:MM
		expect(formatted).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);
	});

	it('should handle naive timestamps correctly', () => {
		const naiveTimestamp = '2025-11-23T03:10:00';
		const formatted = formatDateTime(naiveTimestamp);

		// Should treat as UTC
		expect(formatted).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);
	});
});
