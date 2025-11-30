/**
 * Unit tests for date utility functions
 *
 * CRITICAL: Tests timezone handling for GMT+8 users
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { parseUTCTimestamp, formatRelativeTime, formatTime, formatDateTime, formatDate } from './date';

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

describe('formatDate', () => {
	let originalDate: typeof Date;
	const mockCurrentTime = new Date('2025-11-23T12:00:00Z');

	beforeEach(() => {
		originalDate = global.Date;
		global.Date = class extends Date {
			constructor(...args: any[]) {
				if (args.length === 0) {
					super(mockCurrentTime.getTime());
				} else {
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

	it('should return "Today" for same day timestamps', () => {
		// Same day as mock (2025-11-23)
		const today = '2025-11-23T10:00:00Z';
		expect(formatDate(today)).toBe('Today');
	});

	it('should return "Yesterday" for previous day', () => {
		// One day before mock (2025-11-22)
		const yesterday = '2025-11-22T10:00:00Z';
		expect(formatDate(yesterday)).toBe('Yesterday');
	});

	it('should return month and day for same year', () => {
		// Earlier in same year
		const sameYear = '2025-03-15T10:00:00Z';
		expect(formatDate(sameYear)).toBe('Mar 15');
	});

	it('should return month, day, and year for different year', () => {
		// Different year
		const differentYear = '2024-03-15T10:00:00Z';
		expect(formatDate(differentYear)).toBe('Mar 15, 2024');
	});

	it('should handle naive timestamps correctly', () => {
		// Naive timestamp (no Z)
		const naiveToday = '2025-11-23T10:00:00';
		expect(formatDate(naiveToday)).toBe('Today');
	});

	it('should handle timestamps with offset', () => {
		// Timestamp with offset
		const offsetTimestamp = '2025-11-23T20:00:00+08:00'; // Still Nov 23 in UTC
		expect(formatDate(offsetTimestamp)).toBe('Today');
	});

	it('should handle January dates', () => {
		const january = '2025-01-05T10:00:00Z';
		expect(formatDate(january)).toBe('Jan 5');
	});

	it('should handle December dates', () => {
		const december = '2025-12-25T10:00:00Z';
		expect(formatDate(december)).toBe('Dec 25');
	});

	it('should handle all months correctly', () => {
		const months = [
			{ date: '2025-01-15T10:00:00Z', expected: 'Jan 15' },
			{ date: '2025-02-15T10:00:00Z', expected: 'Feb 15' },
			{ date: '2025-03-15T10:00:00Z', expected: 'Mar 15' },
			{ date: '2025-04-15T10:00:00Z', expected: 'Apr 15' },
			{ date: '2025-05-15T10:00:00Z', expected: 'May 15' },
			{ date: '2025-06-15T10:00:00Z', expected: 'Jun 15' },
			{ date: '2025-07-15T10:00:00Z', expected: 'Jul 15' },
			{ date: '2025-08-15T10:00:00Z', expected: 'Aug 15' },
			{ date: '2025-09-15T10:00:00Z', expected: 'Sep 15' },
			{ date: '2025-10-15T10:00:00Z', expected: 'Oct 15' }
		];

		for (const { date, expected } of months) {
			expect(formatDate(date)).toBe(expected);
		}
	});

	it('should handle single-digit days', () => {
		const singleDigit = '2025-03-05T10:00:00Z';
		expect(formatDate(singleDigit)).toBe('Mar 5');
	});

	it('should handle double-digit days', () => {
		const doubleDigit = '2025-03-25T10:00:00Z';
		expect(formatDate(doubleDigit)).toBe('Mar 25');
	});

	it('should handle end of month', () => {
		const endOfMonth = '2025-03-31T10:00:00Z';
		expect(formatDate(endOfMonth)).toBe('Mar 31');
	});

	it('should handle beginning of year', () => {
		const newYearsDay = '2025-01-01T10:00:00Z';
		expect(formatDate(newYearsDay)).toBe('Jan 1');
	});

	it('should handle previous year December', () => {
		const previousYearDec = '2024-12-31T10:00:00Z';
		expect(formatDate(previousYearDec)).toBe('Dec 31, 2024');
	});
});

describe('formatRelativeTime - edge cases', () => {
	let originalDate: typeof Date;
	const mockCurrentTime = new Date('2025-11-23T03:15:00Z');

	beforeEach(() => {
		originalDate = global.Date;
		global.Date = class extends Date {
			constructor(...args: any[]) {
				if (args.length === 0) {
					super(mockCurrentTime.getTime());
				} else {
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

	it('should return "1m ago" for exactly 1 minute', () => {
		const oneMinuteAgo = '2025-11-23T03:14:00Z';
		expect(formatRelativeTime(oneMinuteAgo)).toBe('1m ago');
	});

	it('should return "1h ago" for exactly 1 hour', () => {
		const oneHourAgo = '2025-11-23T02:15:00Z';
		expect(formatRelativeTime(oneHourAgo)).toBe('1h ago');
	});

	it('should return "1d ago" for exactly 1 day', () => {
		const oneDayAgo = '2025-11-22T03:15:00Z';
		expect(formatRelativeTime(oneDayAgo)).toBe('1d ago');
	});

	it('should return "1w ago" for exactly 1 week', () => {
		const oneWeekAgo = '2025-11-16T03:15:00Z';
		expect(formatRelativeTime(oneWeekAgo)).toBe('1w ago');
	});

	it('should return "1mo ago" for exactly 1 month (30 days)', () => {
		const oneMonthAgo = '2025-10-24T03:15:00Z';
		expect(formatRelativeTime(oneMonthAgo)).toBe('1mo ago');
	});

	it('should handle 59 minutes correctly', () => {
		const fiftyNineMinutes = '2025-11-23T02:16:00Z';
		expect(formatRelativeTime(fiftyNineMinutes)).toBe('59m ago');
	});

	it('should handle 23 hours correctly', () => {
		const twentyThreeHours = '2025-11-22T04:15:00Z';
		expect(formatRelativeTime(twentyThreeHours)).toBe('23h ago');
	});

	it('should handle 6 days correctly', () => {
		const sixDays = '2025-11-17T03:15:00Z';
		expect(formatRelativeTime(sixDays)).toBe('6d ago');
	});

	it('should handle 3 weeks correctly', () => {
		const threeWeeks = '2025-11-02T03:15:00Z';
		expect(formatRelativeTime(threeWeeks)).toBe('3w ago');
	});

	it('should handle 6 months correctly', () => {
		const sixMonths = '2025-05-23T03:15:00Z';
		expect(formatRelativeTime(sixMonths)).toBe('6mo ago');
	});

	it('should handle 12 months correctly', () => {
		const twelveMonths = '2024-11-23T03:15:00Z';
		expect(formatRelativeTime(twelveMonths)).toBe('12mo ago');
	});
});

describe('parseUTCTimestamp - edge cases', () => {
	it('should handle midnight UTC', () => {
		const midnight = '2025-11-23T00:00:00Z';
		const date = parseUTCTimestamp(midnight);
		expect(date.getUTCHours()).toBe(0);
		expect(date.getUTCMinutes()).toBe(0);
	});

	it('should handle end of day UTC', () => {
		const endOfDay = '2025-11-23T23:59:59Z';
		const date = parseUTCTimestamp(endOfDay);
		expect(date.getUTCHours()).toBe(23);
		expect(date.getUTCMinutes()).toBe(59);
	});

	it('should handle leap year February 29', () => {
		const leapYear = '2024-02-29T12:00:00Z';
		const date = parseUTCTimestamp(leapYear);
		expect(date.getUTCMonth()).toBe(1); // 0-indexed
		expect(date.getUTCDate()).toBe(29);
	});

	it('should handle year boundary', () => {
		const newYear = '2025-01-01T00:00:00Z';
		const date = parseUTCTimestamp(newYear);
		expect(date.getUTCFullYear()).toBe(2025);
		expect(date.getUTCMonth()).toBe(0);
		expect(date.getUTCDate()).toBe(1);
	});

	it('should handle timestamps with milliseconds', () => {
		const withMs = '2025-11-23T12:34:56.789Z';
		const date = parseUTCTimestamp(withMs);
		expect(date.getUTCHours()).toBe(12);
		expect(date.getUTCMinutes()).toBe(34);
		expect(date.getUTCSeconds()).toBe(56);
	});

	it('should handle +00:00 offset (same as Z)', () => {
		const zeroOffset = '2025-11-23T12:00:00+00:00';
		const date = parseUTCTimestamp(zeroOffset);
		expect(date.getUTCHours()).toBe(12);
	});

	it('should handle maximum positive offset +14:00', () => {
		const maxPositive = '2025-11-24T02:00:00+14:00'; // Line Islands
		const date = parseUTCTimestamp(maxPositive);
		expect(date.getUTCHours()).toBe(12); // 02:00 + 14 = 12:00 previous day
	});

	it('should handle maximum negative offset -12:00', () => {
		const maxNegative = '2025-11-22T00:00:00-12:00'; // Baker Island
		const date = parseUTCTimestamp(maxNegative);
		expect(date.getUTCHours()).toBe(12);
	});
});
