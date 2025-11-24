/**
 * Date and time utility functions
 *
 * CRITICAL TIMEZONE HANDLING:
 * Backend sends naive UTC timestamps without "Z" suffix (e.g., "2025-11-23T03:10:00").
 * JavaScript's Date() constructor interprets these as LOCAL time, not UTC.
 * All functions in this file handle timezone conversion correctly.
 */

/**
 * Parse timestamp string and ensure it's interpreted as UTC
 *
 * PROBLEM:
 * - Backend: datetime.utcnow() creates naive datetime
 * - Pydantic: Serializes as "2025-11-23T03:10:00" (NO "Z" suffix)
 * - JavaScript: new Date("2025-11-23T03:10:00") assumes LOCAL timezone
 * - Result: GMT+8 user sees wrong time (8 hour difference)
 *
 * SOLUTION:
 * - If timestamp has timezone info ("Z" or "+HH:MM"), use as-is
 * - If timestamp is naive (no timezone), append "Z" to force UTC interpretation
 *
 * @param isoDate - ISO 8601 datetime string (with or without timezone)
 * @returns Date object representing the correct UTC time
 */
export function parseUTCTimestamp(isoDate: string): Date {
	// Check if timestamp already has timezone info
	// Valid timezone formats:
	// - "Z" suffix: 2025-11-23T03:10:00Z
	// - Positive offset: 2025-11-23T11:10:00+08:00
	// - Negative offset: 2025-11-23T01:10:00-02:00
	const hasTimezone = isoDate.endsWith('Z') ||
	                    /[+-]\d{2}:\d{2}$/.test(isoDate);

	if (hasTimezone) {
		// Already has timezone, parse directly
		return new Date(isoDate);
	} else {
		// Naive timestamp (no timezone info), assume UTC by appending "Z"
		return new Date(isoDate + 'Z');
	}
}

/**
 * Format relative timestamp
 *
 * Examples: "Just now", "2m ago", "5h ago", "3d ago", "2w ago", "6mo ago"
 *
 * WHY relative instead of absolute:
 * - Relevance: "2 hours ago" is more meaningful than "14:32"
 * - Scanning: User can quickly identify recent conversations
 * - Space-efficient: Shorter than full datetime
 *
 * @param isoDate - ISO 8601 datetime string (null for "No messages")
 * @returns Human-readable relative time string
 */
export function formatRelativeTime(isoDate: string | null): string {
	if (!isoDate) return 'No messages';

	const date = parseUTCTimestamp(isoDate);
	const now = new Date();
	const diffMs = now.getTime() - date.getTime();

	// Handle future timestamps (clock skew or timezone bugs)
	if (diffMs < 0) return 'Just now';

	const diffMins = Math.floor(diffMs / 60000);
	const diffHours = Math.floor(diffMs / 3600000);
	const diffDays = Math.floor(diffMs / 86400000);

	if (diffMins < 1) return 'Just now';
	if (diffMins === 1) return '1m ago';
	if (diffMins < 60) return `${diffMins}m ago`;

	if (diffHours === 1) return '1h ago';
	if (diffHours < 24) return `${diffHours}h ago`;

	if (diffDays === 1) return '1d ago';
	if (diffDays < 7) return `${diffDays}d ago`;

	const diffWeeks = Math.floor(diffDays / 7);
	if (diffWeeks === 1) return '1w ago';
	if (diffWeeks < 4) return `${diffWeeks}w ago`;

	const diffMonths = Math.floor(diffDays / 30);
	if (diffMonths === 1) return '1mo ago';
	return `${diffMonths}mo ago`;
}

/**
 * Format timestamp as HH:MM (24-hour format)
 *
 * Examples: "09:30", "14:45", "23:59"
 *
 * WHY 24-hour format:
 * - International standard: Works across timezones
 * - No ambiguity: No AM/PM confusion
 * - Compact: Shorter than "2:45 PM"
 *
 * @param isoDate - ISO 8601 datetime string
 * @returns Time string in HH:MM format
 */
export function formatTime(isoDate: string): string {
	const date = parseUTCTimestamp(isoDate);
	const hours = date.getHours().toString().padStart(2, '0');
	const minutes = date.getMinutes().toString().padStart(2, '0');
	return `${hours}:${minutes}`;
}

/**
 * Format timestamp as full date and time
 *
 * Examples: "2025-11-23 14:30", "2025-01-15 09:00"
 *
 * WHY this format:
 * - ISO 8601 compatible: Sortable and unambiguous
 * - Human-readable: Easy to scan
 * - Compact: Fits in UI tooltips
 *
 * @param isoDate - ISO 8601 datetime string
 * @returns Formatted datetime string
 */
export function formatDateTime(isoDate: string): string {
	const date = parseUTCTimestamp(isoDate);
	const year = date.getFullYear();
	const month = (date.getMonth() + 1).toString().padStart(2, '0');
	const day = date.getDate().toString().padStart(2, '0');
	const hours = date.getHours().toString().padStart(2, '0');
	const minutes = date.getMinutes().toString().padStart(2, '0');
	return `${year}-${month}-${day} ${hours}:${minutes}`;
}

/**
 * Format timestamp as human-readable date
 *
 * Examples: "Today", "Yesterday", "Nov 23", "Jan 15, 2025"
 *
 * WHY smart formatting:
 * - Context-aware: Shows relevant detail based on recency
 * - Natural language: "Today" is friendlier than "2025-11-23"
 * - Compact: Short labels for recent dates
 *
 * @param isoDate - ISO 8601 datetime string
 * @returns Human-readable date string
 */
export function formatDate(isoDate: string): string {
	const date = parseUTCTimestamp(isoDate);
	const now = new Date();

	// Check if same day
	const isToday = date.getDate() === now.getDate() &&
	                date.getMonth() === now.getMonth() &&
	                date.getFullYear() === now.getFullYear();

	if (isToday) return 'Today';

	// Check if yesterday
	const yesterday = new Date(now);
	yesterday.setDate(yesterday.getDate() - 1);
	const isYesterday = date.getDate() === yesterday.getDate() &&
	                    date.getMonth() === yesterday.getMonth() &&
	                    date.getFullYear() === yesterday.getFullYear();

	if (isYesterday) return 'Yesterday';

	// Format as "Nov 23" for current year, "Nov 23, 2024" for other years
	const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
	const month = months[date.getMonth()];
	const day = date.getDate();
	const year = date.getFullYear();

	if (year === now.getFullYear()) {
		return `${month} ${day}`;
	} else {
		return `${month} ${day}, ${year}`;
	}
}
