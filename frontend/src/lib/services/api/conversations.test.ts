/**
 * Unit tests for conversations API client
 *
 * Tests all conversation CRUD operations with mocked apiRequest.
 * Follows AAA pattern (Arrange, Act, Assert) for clarity.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { Conversation, ConversationListResponse } from '$lib/types';
import { toast } from '$lib/stores/toast';

// Mock the dependencies
vi.mock('./base', () => ({
	apiRequest: vi.fn()
}));

vi.mock('$lib/stores/toast', () => ({
	toast: {
		success: vi.fn(),
		error: vi.fn()
	}
}));

// Import after mocking
import { apiRequest } from './base';
import {
	getConversations,
	getConversation,
	createConversation,
	updateConversation,
	deleteConversation,
	getConversationMessages
} from './conversations';

describe('conversations.ts - getConversations', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('sends GET request to /api/projects/{projectId}/conversations', async () => {
		// Arrange
		const projectId = 123;
		const mockResponse: ConversationListResponse = {
			conversations: [],
			total_count: 0
		};
		(apiRequest as any).mockResolvedValue(mockResponse);

		// Act
		await getConversations(projectId);

		// Assert
		expect(apiRequest).toHaveBeenCalledWith('/api/projects/123/conversations');
	});

	it('returns array of conversations sorted by updated_at DESC', async () => {
		// Arrange
		const projectId = 123;
		const mockConversations: Conversation[] = [
			{
				id: 1,
				project_id: 123,
				title: 'Latest Chat',
				created_at: '2025-11-24T10:00:00Z',
				updated_at: '2025-11-24T12:00:00Z',
				last_message_at: '2025-11-24T12:00:00Z',
				message_count: 5
			},
			{
				id: 2,
				project_id: 123,
				title: 'Older Chat',
				created_at: '2025-11-23T10:00:00Z',
				updated_at: '2025-11-23T11:00:00Z',
				last_message_at: '2025-11-23T11:00:00Z',
				message_count: 3
			}
		];
		const mockResponse: ConversationListResponse = {
			conversations: mockConversations,
			total_count: 2
		};
		(apiRequest as any).mockResolvedValue(mockResponse);

		// Act
		const result = await getConversations(projectId);

		// Assert
		expect(result).toEqual(mockConversations);
		expect(result).toHaveLength(2);
		expect(result[0].title).toBe('Latest Chat');
	});

	it('returns empty array when no conversations exist', async () => {
		// Arrange
		const projectId = 123;
		const mockResponse: ConversationListResponse = {
			conversations: [],
			total_count: 0
		};
		(apiRequest as any).mockResolvedValue(mockResponse);

		// Act
		const result = await getConversations(projectId);

		// Assert
		expect(result).toEqual([]);
		expect(result).toHaveLength(0);
	});

	it('throws error on API failure', async () => {
		// Arrange
		const projectId = 123;
		const error = new Error('API Error: Project not found');
		(apiRequest as any).mockRejectedValue(error);

		// Act & Assert
		await expect(getConversations(projectId)).rejects.toThrow('API Error: Project not found');
	});
});

describe('conversations.ts - getConversation', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('sends GET request to /api/conversations/{id}', async () => {
		// Arrange
		const conversationId = 42;
		const mockConversation: Conversation = {
			id: 42,
			project_id: 123,
			title: 'Test Conversation',
			created_at: '2025-11-24T10:00:00Z',
			updated_at: '2025-11-24T12:00:00Z',
			last_message_at: '2025-11-24T12:00:00Z',
			message_count: 5
		};
		(apiRequest as any).mockResolvedValue(mockConversation);

		// Act
		await getConversation(conversationId);

		// Assert
		expect(apiRequest).toHaveBeenCalledWith('/api/conversations/42');
	});

	it('returns single conversation with all fields', async () => {
		// Arrange
		const conversationId = 42;
		const mockConversation: Conversation = {
			id: 42,
			project_id: 123,
			title: 'Test Conversation',
			created_at: '2025-11-24T10:00:00Z',
			updated_at: '2025-11-24T12:00:00Z',
			last_message_at: '2025-11-24T12:00:00Z',
			message_count: 5,
			metadata: { key: 'value' }
		};
		(apiRequest as any).mockResolvedValue(mockConversation);

		// Act
		const result = await getConversation(conversationId);

		// Assert
		expect(result).toEqual(mockConversation);
		expect(result.id).toBe(42);
		expect(result.title).toBe('Test Conversation');
		expect(result.metadata).toEqual({ key: 'value' });
	});

	it('throws error on 404 Not Found', async () => {
		// Arrange
		const conversationId = 999;
		const error = new Error('API Error: Conversation not found');
		(apiRequest as any).mockRejectedValue(error);

		// Act & Assert
		await expect(getConversation(conversationId)).rejects.toThrow(
			'API Error: Conversation not found'
		);
	});

	it('throws error on API failure', async () => {
		// Arrange
		const conversationId = 42;
		const error = new Error('API Error: Internal Server Error');
		(apiRequest as any).mockRejectedValue(error);

		// Act & Assert
		await expect(getConversation(conversationId)).rejects.toThrow(
			'API Error: Internal Server Error'
		);
	});
});

describe('conversations.ts - createConversation', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('sends POST request to /api/conversations/create', async () => {
		// Arrange
		const projectId = 123;
		const title = 'New Conversation';
		const mockConversation: Conversation = {
			id: 1,
			project_id: 123,
			title: 'New Conversation',
			created_at: '2025-11-24T10:00:00Z',
			updated_at: '2025-11-24T10:00:00Z',
			last_message_at: null,
			message_count: 0
		};
		(apiRequest as any).mockResolvedValue(mockConversation);

		// Act
		await createConversation(projectId, title);

		// Assert
		expect(apiRequest).toHaveBeenCalledWith('/api/conversations/create', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				project_id: projectId,
				title: title
			})
		});
	});

	it('includes projectId in request body', async () => {
		// Arrange
		const projectId = 456;
		const mockConversation: Conversation = {
			id: 1,
			project_id: 456,
			title: 'New Chat',
			created_at: '2025-11-24T10:00:00Z',
			updated_at: '2025-11-24T10:00:00Z',
			last_message_at: null,
			message_count: 0
		};
		(apiRequest as any).mockResolvedValue(mockConversation);

		// Act
		await createConversation(projectId);

		// Assert
		const callArgs = (apiRequest as any).mock.calls[0];
		const requestBody = JSON.parse(callArgs[1].body);
		expect(requestBody.project_id).toBe(456);
	});

	it('includes optional title in request body', async () => {
		// Arrange
		const projectId = 123;
		const title = 'Custom Title';
		const mockConversation: Conversation = {
			id: 1,
			project_id: 123,
			title: 'Custom Title',
			created_at: '2025-11-24T10:00:00Z',
			updated_at: '2025-11-24T10:00:00Z',
			last_message_at: null,
			message_count: 0
		};
		(apiRequest as any).mockResolvedValue(mockConversation);

		// Act
		await createConversation(projectId, title);

		// Assert
		const callArgs = (apiRequest as any).mock.calls[0];
		const requestBody = JSON.parse(callArgs[1].body);
		expect(requestBody.title).toBe('Custom Title');
	});

	it('returns created conversation with default title "New Chat"', async () => {
		// Arrange
		const projectId = 123;
		const mockConversation: Conversation = {
			id: 1,
			project_id: 123,
			title: 'New Chat',
			created_at: '2025-11-24T10:00:00Z',
			updated_at: '2025-11-24T10:00:00Z',
			last_message_at: null,
			message_count: 0
		};
		(apiRequest as any).mockResolvedValue(mockConversation);

		// Act
		const result = await createConversation(projectId);

		// Assert
		expect(result).toEqual(mockConversation);
		expect(result.title).toBe('New Chat');
		expect(toast.success).toHaveBeenCalledWith('Conversation created successfully');
	});

	it('throws error on API failure', async () => {
		// Arrange
		const projectId = 123;
		const error = new Error('API Error: Failed to create conversation');
		(apiRequest as any).mockRejectedValue(error);

		// Act & Assert
		await expect(createConversation(projectId)).rejects.toThrow(
			'API Error: Failed to create conversation'
		);
	});
});

describe('conversations.ts - updateConversation', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('sends PUT request to /api/conversations/{id}', async () => {
		// Arrange
		const conversationId = 42;
		const updateData = { title: 'Updated Title' };
		const mockConversation: Conversation = {
			id: 42,
			project_id: 123,
			title: 'Updated Title',
			created_at: '2025-11-24T10:00:00Z',
			updated_at: '2025-11-24T12:00:00Z',
			last_message_at: null,
			message_count: 0
		};
		(apiRequest as any).mockResolvedValue(mockConversation);

		// Act
		await updateConversation(conversationId, updateData);

		// Assert
		expect(apiRequest).toHaveBeenCalledWith('/api/conversations/42', {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(updateData)
		});
	});

	it('includes updated title in request body', async () => {
		// Arrange
		const conversationId = 42;
		const updateData = { title: 'Security Analysis 2024' };
		const mockConversation: Conversation = {
			id: 42,
			project_id: 123,
			title: 'Security Analysis 2024',
			created_at: '2025-11-24T10:00:00Z',
			updated_at: '2025-11-24T12:00:00Z',
			last_message_at: null,
			message_count: 0
		};
		(apiRequest as any).mockResolvedValue(mockConversation);

		// Act
		await updateConversation(conversationId, updateData);

		// Assert
		const callArgs = (apiRequest as any).mock.calls[0];
		const requestBody = JSON.parse(callArgs[1].body);
		expect(requestBody.title).toBe('Security Analysis 2024');
	});

	it('returns updated conversation data', async () => {
		// Arrange
		const conversationId = 42;
		const updateData = { title: 'Updated Title' };
		const mockConversation: Conversation = {
			id: 42,
			project_id: 123,
			title: 'Updated Title',
			created_at: '2025-11-24T10:00:00Z',
			updated_at: '2025-11-24T13:00:00Z',
			last_message_at: null,
			message_count: 0
		};
		(apiRequest as any).mockResolvedValue(mockConversation);

		// Act
		const result = await updateConversation(conversationId, updateData);

		// Assert
		expect(result).toEqual(mockConversation);
		expect(result.title).toBe('Updated Title');
		// No toast for updates - too noisy for frequent operations
	});

	it('throws error on API failure', async () => {
		// Arrange
		const conversationId = 42;
		const updateData = { title: 'Updated Title' };
		const error = new Error('API Error: Conversation not found');
		(apiRequest as any).mockRejectedValue(error);

		// Act & Assert
		await expect(updateConversation(conversationId, updateData)).rejects.toThrow(
			'API Error: Conversation not found'
		);
	});
});

describe('conversations.ts - deleteConversation', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('sends DELETE request to /api/conversations/{id}', async () => {
		// Arrange
		const conversationId = 42;
		(apiRequest as any).mockResolvedValue(undefined);

		// Act
		await deleteConversation(conversationId);

		// Assert
		expect(apiRequest).toHaveBeenCalledWith('/api/conversations/42', {
			method: 'DELETE'
		});
	});

	it('returns success response', async () => {
		// Arrange
		const conversationId = 42;
		(apiRequest as any).mockResolvedValue(undefined);

		// Act
		const result = await deleteConversation(conversationId);

		// Assert
		expect(result).toBeUndefined();
		expect(toast.success).toHaveBeenCalledWith('Conversation deleted successfully');
	});

	it('throws error on API failure', async () => {
		// Arrange
		const conversationId = 42;
		const error = new Error('API Error: Failed to delete conversation');
		(apiRequest as any).mockRejectedValue(error);

		// Act & Assert
		await expect(deleteConversation(conversationId)).rejects.toThrow(
			'API Error: Failed to delete conversation'
		);
	});
});

describe('conversations.ts - getConversationMessages', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('sends GET request to /api/messages/{conversationId}', async () => {
		// Arrange
		const conversationId = 42;
		const mockResponse: any = {
			messages: [],
			total_count: 0
		};
		(apiRequest as any).mockResolvedValue(mockResponse);

		// Act
		await getConversationMessages(conversationId);

		// Assert
		expect(apiRequest).toHaveBeenCalledWith('/api/messages/42');
	});

	it('returns array of messages sorted by created_at ASC', async () => {
		// Arrange
		const conversationId = 42;
		const mockMessages: any[] = [
			{
				id: 1,
				conversation_id: 42,
				role: 'user',
				content: 'First message',
				created_at: '2025-11-24T10:00:00Z',
				reaction: null,
				parent_message_id: null,
				token_count: 2
			},
			{
				id: 2,
				conversation_id: 42,
				role: 'assistant',
				content: 'Second message',
				created_at: '2025-11-24T10:01:00Z',
				reaction: null,
				parent_message_id: null,
				token_count: 2
			}
		];
		const mockResponse: any = {
			messages: mockMessages,
			total_count: 2
		};
		(apiRequest as any).mockResolvedValue(mockResponse);

		// Act
		const result = await getConversationMessages(conversationId);

		// Assert
		expect(result).toEqual(mockMessages);
		expect(result).toHaveLength(2);
		expect(result[0].content).toBe('First message');
		expect(result[1].content).toBe('Second message');
	});

	it('returns empty array when no messages exist', async () => {
		// Arrange
		const conversationId = 42;
		const mockResponse: any = {
			messages: [],
			total_count: 0
		};
		(apiRequest as any).mockResolvedValue(mockResponse);

		// Act
		const result = await getConversationMessages(conversationId);

		// Assert
		expect(result).toEqual([]);
		expect(result).toHaveLength(0);
	});

	it('throws error on API failure', async () => {
		// Arrange
		const conversationId = 999;
		const error = new Error('API Error: Conversation not found');
		(apiRequest as any).mockRejectedValue(error);

		// Act & Assert
		await expect(getConversationMessages(conversationId)).rejects.toThrow(
			'API Error: Conversation not found'
		);
	});
});
