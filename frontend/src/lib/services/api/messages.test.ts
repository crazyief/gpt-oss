/**
 * Unit tests for messages API client
 *
 * Tests all message CRUD operations with mocked apiRequest.
 * Follows AAA pattern (Arrange, Act, Assert) for clarity.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { Message, MessageListResponse } from '$lib/types';
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
import { getMessage, createMessage, updateMessage, updateMessageReaction } from './messages';

// Note: getConversationMessages is tested in conversations.test.ts

describe('messages.ts - getMessage', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('sends GET request to /api/messages/{id}', async () => {
		// Arrange
		const messageId = 42;
		const mockMessage: Message = {
			id: 42,
			conversation_id: 123,
			role: 'user',
			content: 'Test message',
			created_at: '2025-11-24T10:00:00Z',
			reaction: null,
			parent_message_id: null,
			token_count: 3
		};
		(apiRequest as any).mockResolvedValue(mockMessage);

		// Act
		await getMessage(messageId);

		// Assert
		expect(apiRequest).toHaveBeenCalledWith('/api/messages/42');
	});

	it('returns single message with content and metadata', async () => {
		// Arrange
		const messageId = 42;
		const mockMessage: Message = {
			id: 42,
			conversation_id: 123,
			role: 'assistant',
			content: '# Analysis\n\nThis is a markdown response.',
			created_at: '2025-11-24T10:00:00Z',
			reaction: 'thumbs_up',
			parent_message_id: 41,
			token_count: 150,
			model_name: 'gpt-oss-20b',
			completion_time_ms: 1500,
			metadata: { sources: ['doc1.pdf'] }
		};
		(apiRequest as any).mockResolvedValue(mockMessage);

		// Act
		const result = await getMessage(messageId);

		// Assert
		expect(result).toEqual(mockMessage);
		expect(result.id).toBe(42);
		expect(result.content).toContain('Analysis');
		expect(result.model_name).toBe('gpt-oss-20b');
		expect(result.metadata).toEqual({ sources: ['doc1.pdf'] });
	});

	it('throws error on API failure', async () => {
		// Arrange
		const messageId = 999;
		const error = new Error('API Error: Message not found');
		(apiRequest as any).mockRejectedValue(error);

		// Act & Assert
		await expect(getMessage(messageId)).rejects.toThrow('API Error: Message not found');
	});
});

describe('messages.ts - createMessage', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('sends POST request to /api/messages/create', async () => {
		// Arrange
		const conversationId = 123;
		const content = 'Hello, how are you?';
		const role = 'user';
		const mockMessage: Message = {
			id: 1,
			conversation_id: 123,
			role: 'user',
			content: 'Hello, how are you?',
			created_at: '2025-11-24T10:00:00Z',
			reaction: null,
			parent_message_id: null,
			token_count: 5
		};
		(apiRequest as any).mockResolvedValue(mockMessage);

		// Act
		await createMessage(conversationId, content, role);

		// Assert
		expect(apiRequest).toHaveBeenCalledWith('/api/messages/create', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				conversation_id: conversationId,
				content: content,
				role: role
			})
		});
	});

	it('includes conversationId, role, and content in request body', async () => {
		// Arrange
		const conversationId = 456;
		const content = 'Test message content';
		const role = 'user';
		const mockMessage: Message = {
			id: 1,
			conversation_id: 456,
			role: 'user',
			content: 'Test message content',
			created_at: '2025-11-24T10:00:00Z',
			reaction: null,
			parent_message_id: null,
			token_count: 4
		};
		(apiRequest as any).mockResolvedValue(mockMessage);

		// Act
		await createMessage(conversationId, content, role);

		// Assert
		const callArgs = (apiRequest as any).mock.calls[0];
		const requestBody = JSON.parse(callArgs[1].body);
		expect(requestBody.conversation_id).toBe(456);
		expect(requestBody.content).toBe('Test message content');
		expect(requestBody.role).toBe('user');
	});

	it('returns created message with timestamp', async () => {
		// Arrange
		const conversationId = 123;
		const content = 'New message';
		const mockMessage: Message = {
			id: 10,
			conversation_id: 123,
			role: 'user',
			content: 'New message',
			created_at: '2025-11-24T14:30:00Z',
			reaction: null,
			parent_message_id: null,
			token_count: 2
		};
		(apiRequest as any).mockResolvedValue(mockMessage);

		// Act
		const result = await createMessage(conversationId, content);

		// Assert
		expect(result).toEqual(mockMessage);
		expect(result.id).toBe(10);
		expect(result.created_at).toBe('2025-11-24T14:30:00Z');
	});

	it('throws error on API failure', async () => {
		// Arrange
		const conversationId = 123;
		const content = 'Test message';
		const error = new Error('API Error: Failed to create message');
		(apiRequest as any).mockRejectedValue(error);

		// Act & Assert
		await expect(createMessage(conversationId, content)).rejects.toThrow(
			'API Error: Failed to create message'
		);
	});
});

describe('messages.ts - updateMessage', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('sends PUT request to /api/messages/{id}/update', async () => {
		// Arrange
		const messageId = 42;
		const updateData = { content: 'Updated content' };
		const mockMessage: Message = {
			id: 42,
			conversation_id: 123,
			role: 'user',
			content: 'Updated content',
			created_at: '2025-11-24T10:00:00Z',
			reaction: null,
			parent_message_id: null,
			token_count: 3
		};
		(apiRequest as any).mockResolvedValue(mockMessage);

		// Act
		await updateMessage(messageId, updateData);

		// Assert
		expect(apiRequest).toHaveBeenCalledWith('/api/messages/42/update', {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(updateData)
		});
	});

	it('includes updated content in request body', async () => {
		// Arrange
		const messageId = 42;
		const updateData = { content: 'This is the updated message content' };
		const mockMessage: Message = {
			id: 42,
			conversation_id: 123,
			role: 'user',
			content: 'This is the updated message content',
			created_at: '2025-11-24T10:00:00Z',
			reaction: null,
			parent_message_id: null,
			token_count: 7
		};
		(apiRequest as any).mockResolvedValue(mockMessage);

		// Act
		await updateMessage(messageId, updateData);

		// Assert
		const callArgs = (apiRequest as any).mock.calls[0];
		const requestBody = JSON.parse(callArgs[1].body);
		expect(requestBody.content).toBe('This is the updated message content');
		expect(toast.success).toHaveBeenCalledWith('Message updated successfully');
	});
});

describe('messages.ts - updateMessageReaction', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('sends PUT request to /api/messages/{id}/reaction', async () => {
		// Arrange
		const messageId = 42;
		const reaction = 'thumbs_up';
		const mockMessage: Message = {
			id: 42,
			conversation_id: 123,
			role: 'assistant',
			content: 'Test response',
			created_at: '2025-11-24T10:00:00Z',
			reaction: 'thumbs_up',
			parent_message_id: null,
			token_count: 2
		};
		(apiRequest as any).mockResolvedValue(mockMessage);

		// Act
		await updateMessageReaction(messageId, reaction);

		// Assert
		expect(apiRequest).toHaveBeenCalledWith('/api/messages/42/reaction', {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ reaction: reaction })
		});
	});

	it('includes reaction type (like/dislike) in request body', async () => {
		// Arrange
		const messageId = 42;
		const reaction = 'thumbs_down';
		const mockMessage: Message = {
			id: 42,
			conversation_id: 123,
			role: 'assistant',
			content: 'Test response',
			created_at: '2025-11-24T10:00:00Z',
			reaction: 'thumbs_down',
			parent_message_id: null,
			token_count: 2
		};
		(apiRequest as any).mockResolvedValue(mockMessage);

		// Act
		const result = await updateMessageReaction(messageId, reaction);

		// Assert
		const callArgs = (apiRequest as any).mock.calls[0];
		const requestBody = JSON.parse(callArgs[1].body);
		expect(requestBody.reaction).toBe('thumbs_down');
		expect(result.reaction).toBe('thumbs_down');
	});
});
