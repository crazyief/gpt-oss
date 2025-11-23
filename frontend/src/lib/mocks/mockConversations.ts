/**
 * Mock data for development and testing
 *
 * Purpose: Provide realistic sample data for UI development while backend is being implemented
 *
 * Usage strategy:
 * - Use during Task-005 implementation (sidebar components)
 * - Replace with real API calls once Backend-Agent completes CRUD endpoints
 * - Keep file for future testing (unit tests, Storybook stories)
 *
 * Data design:
 * - Realistic timestamps (recent dates, proper chronological order)
 * - Variety of conversation states (empty, active, old)
 * - Edge cases (long titles, null descriptions, zero message counts)
 *
 * WHY mock data instead of waiting for backend:
 * - Parallel development: Frontend and backend teams work independently
 * - Faster iteration: No need to run backend services during UI development
 * - Consistent test data: Same data across all dev environments
 * - Saves 2-3 hours: Can implement UI immediately without backend dependency
 */

import type { Conversation, Project } from '$lib/types';

/**
 * Mock projects
 *
 * Represents different project categories a user might create
 */
export const mockProjects: Project[] = [
	{
		id: 1,
		name: 'Cybersecurity Analysis',
		description: 'IEC 62443 industrial security standards research',
		created_at: '2025-11-01T09:00:00Z',
		updated_at: '2025-11-17T14:30:00Z',
		conversation_count: 12
	},
	{
		id: 2,
		name: 'IoT Security Review',
		description: 'ETSI EN 303 645 consumer IoT device analysis',
		created_at: '2025-11-05T10:15:00Z',
		updated_at: '2025-11-16T18:20:00Z',
		conversation_count: 8
	},
	{
		id: 3,
		name: 'Product Testing',
		description: 'EN 18031 privacy assessment and compliance verification',
		created_at: '2025-11-10T11:30:00Z',
		updated_at: '2025-11-17T09:45:00Z',
		conversation_count: 5
	},
	{
		id: 4,
		name: 'General Research',
		description: null, // Test null description handling
		created_at: '2025-11-15T13:00:00Z',
		updated_at: '2025-11-15T13:00:00Z',
		conversation_count: 1
	}
];

/**
 * Mock conversations
 *
 * Variety of conversation states for comprehensive UI testing:
 * - Active conversations (recent messages)
 * - Empty conversations (no messages yet)
 * - Old conversations (last activity weeks ago)
 * - Long titles (test truncation)
 * - Different projects (test filtering)
 */
export const mockConversations: Conversation[] = [
	// Project 1: Cybersecurity Analysis
	{
		id: 1,
		project_id: 1,
		title: 'IEC 62443-4-2 CR 2.11 Authentication Requirements',
		created_at: '2025-11-17T10:00:00Z',
		updated_at: '2025-11-17T14:30:00Z',
		last_message_at: '2025-11-17T14:30:00Z',
		message_count: 15
	},
	{
		id: 2,
		project_id: 1,
		title: 'Security Level Comparison: SL 1 vs SL 2',
		created_at: '2025-11-16T09:00:00Z',
		updated_at: '2025-11-17T11:20:00Z',
		last_message_at: '2025-11-17T11:20:00Z',
		message_count: 8
	},
	{
		id: 3,
		project_id: 1,
		title: 'Zone and Conduit Architecture Design',
		created_at: '2025-11-15T14:00:00Z',
		updated_at: '2025-11-16T16:45:00Z',
		last_message_at: '2025-11-16T16:45:00Z',
		message_count: 22
	},
	{
		id: 4,
		project_id: 1,
		title: 'Risk Assessment Methodology',
		created_at: '2025-11-14T10:30:00Z',
		updated_at: '2025-11-15T13:15:00Z',
		last_message_at: '2025-11-15T13:15:00Z',
		message_count: 12
	},
	{
		id: 5,
		project_id: 1,
		title: 'Empty conversation test', // Test empty conversation (no messages)
		created_at: '2025-11-17T15:00:00Z',
		updated_at: '2025-11-17T15:00:00Z',
		last_message_at: null,
		message_count: 0
	},

	// Project 2: IoT Security Review
	{
		id: 6,
		project_id: 2,
		title: 'ETSI EN 303 645 Provision 5.1 - Default Passwords',
		created_at: '2025-11-16T11:00:00Z',
		updated_at: '2025-11-16T18:20:00Z',
		last_message_at: '2025-11-16T18:20:00Z',
		message_count: 10
	},
	{
		id: 7,
		project_id: 2,
		title: 'Software Update Mechanisms (Provision 5.3)',
		created_at: '2025-11-15T13:30:00Z',
		updated_at: '2025-11-16T10:00:00Z',
		last_message_at: '2025-11-16T10:00:00Z',
		message_count: 7
	},
	{
		id: 8,
		project_id: 2,
		title: 'Network Security Assessment - Smart Camera',
		created_at: '2025-11-14T09:00:00Z',
		updated_at: '2025-11-15T17:30:00Z',
		last_message_at: '2025-11-15T17:30:00Z',
		message_count: 18
	},

	// Project 3: Product Testing
	{
		id: 9,
		project_id: 3,
		title: 'Privacy Impact Assessment Template',
		created_at: '2025-11-17T09:00:00Z',
		updated_at: '2025-11-17T09:45:00Z',
		last_message_at: '2025-11-17T09:45:00Z',
		message_count: 5
	},
	{
		id: 10,
		project_id: 3,
		title: 'GDPR Compliance Checklist',
		created_at: '2025-11-16T14:00:00Z',
		updated_at: '2025-11-16T15:20:00Z',
		last_message_at: '2025-11-16T15:20:00Z',
		message_count: 9
	},

	// Project 4: General Research
	{
		id: 11,
		project_id: 4,
		title: 'Test conversation with extremely long title that should be truncated in the sidebar to prevent layout issues and overflow',
		created_at: '2025-11-15T13:00:00Z',
		updated_at: '2025-11-15T14:00:00Z',
		last_message_at: '2025-11-15T14:00:00Z',
		message_count: 3
	},

	// Orphaned conversation (no project)
	{
		id: 12,
		project_id: null,
		title: 'Orphaned conversation test',
		created_at: '2025-11-01T10:00:00Z',
		updated_at: '2025-11-01T10:30:00Z',
		last_message_at: '2025-11-01T10:30:00Z',
		message_count: 2
	},

	// Old conversation (inactive for weeks)
	{
		id: 13,
		project_id: 1,
		title: 'Old archived conversation',
		created_at: '2025-10-01T08:00:00Z',
		updated_at: '2025-10-05T12:00:00Z',
		last_message_at: '2025-10-05T12:00:00Z',
		message_count: 25
	}
];

/**
 * Generate additional mock conversations for virtual scroll testing
 *
 * Creates 1000+ conversations to test performance of virtual scrolling
 *
 * WHY generate programmatically instead of hardcoding:
 * - Realistic volume: Users with hundreds of conversations need performant UI
 * - Virtual scroll testing: Validates svelte-virtual-list integration works correctly
 * - Memory testing: Ensures app doesn't crash with large datasets
 * - Performance benchmarking: Can measure render time for large lists
 *
 * @param count - Number of mock conversations to generate (default 1000)
 * @returns Array of generated conversations
 */
export function generateMockConversations(count: number = 1000): Conversation[] {
	const generated: Conversation[] = [];
	const titles = [
		'Security vulnerability analysis',
		'Compliance audit findings',
		'Risk assessment review',
		'Architecture design discussion',
		'Implementation questions',
		'Best practices research',
		'Standard interpretation',
		'Testing strategy planning'
	];

	for (let i = 0; i < count; i++) {
		const daysAgo = Math.floor(Math.random() * 90); // Random date within last 90 days
		const createdDate = new Date();
		createdDate.setDate(createdDate.getDate() - daysAgo);

		const messageCount = Math.floor(Math.random() * 50); // 0-50 messages
		const hasMessages = messageCount > 0;

		generated.push({
			id: 1000 + i,
			project_id: Math.floor(Math.random() * 4) + 1, // Random project 1-4
			title: `${titles[i % titles.length]} #${i + 1}`,
			created_at: createdDate.toISOString(),
			updated_at: createdDate.toISOString(),
			last_message_at: hasMessages ? createdDate.toISOString() : null,
			message_count: messageCount
		});
	}

	return generated;
}
