/**
 * Unit tests for messages store
 *
 * Tests: State mutations, streaming logic, error handling
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { messages } from './messages';
import type { Message } from '$lib/types';

describe('messages store', () => {
	beforeEach(() => {
		messages.reset();
	});

	describe('initial state', () => {
		it('should start with empty items', () => {
			const state = get(messages);
			expect(state.items).toEqual([]);
		});

		it('should have loading = false initially', () => {
			const state = get(messages);
			expect(state.isLoading).toBe(false);
		});

		it('should have no error initially', () => {
			const state = get(messages);
			expect(state.error).toBeNull();
		});

		it('should not be streaming initially', () => {
			const state = get(messages);
			expect(state.isStreaming).toBe(false);
			expect(state.streamingMessageId).toBeNull();
			expect(state.streamingContent).toBe('');
		});
	});

	describe('setLoading', () => {
		it('should set loading to true', () => {
			messages.setLoading(true);
			const state = get(messages);
			expect(state.isLoading).toBe(true);
		});

		it('should set loading to false', () => {
			messages.setLoading(true);
			messages.setLoading(false);
			const state = get(messages);
			expect(state.isLoading).toBe(false);
		});
	});

	describe('setMessages', () => {
		it('should set messages array', () => {
			const testMessages: Message[] = [
				{
					id: 1,
					conversation_id: 1,
					role: 'user',
					content: 'Hello',
					created_at: '2025-01-01T00:00:00Z',
					reaction: null,
					parent_message_id: null
				}
			];

			messages.setMessages(testMessages);
			const state = get(messages);
			expect(state.items).toEqual(testMessages);
		});

		it('should reset other state when setting messages', () => {
			messages.setLoading(true);
			messages.setError('Test error');

			const testMessages: Message[] = [];
			messages.setMessages(testMessages);

			const state = get(messages);
			expect(state.isLoading).toBe(false);
			expect(state.error).toBeNull();
		});
	});

	describe('addMessage', () => {
		it('should add message to items', () => {
			const message: Message = {
				id: 1,
				conversation_id: 1,
				role: 'user',
				content: 'Test message',
				created_at: '2025-01-01T00:00:00Z',
				reaction: null,
				parent_message_id: null
			};

			messages.addMessage(message);
			const state = get(messages);
			expect(state.items).toHaveLength(1);
			expect(state.items[0]).toEqual(message);
		});

		it('should append to existing messages', () => {
			const message1: Message = {
				id: 1,
				conversation_id: 1,
				role: 'user',
				content: 'First',
				created_at: '2025-01-01T00:00:00Z',
				reaction: null,
				parent_message_id: null
			};

			const message2: Message = {
				id: 2,
				conversation_id: 1,
				role: 'assistant',
				content: 'Second',
				created_at: '2025-01-01T00:01:00Z',
				reaction: null,
				parent_message_id: null
			};

			messages.addMessage(message1);
			messages.addMessage(message2);

			const state = get(messages);
			expect(state.items).toHaveLength(2);
			expect(state.items[1]).toEqual(message2);
		});
	});

	describe('updateMessage', () => {
		it('should update message by id', () => {
			const message: Message = {
				id: 1,
				conversation_id: 1,
				role: 'assistant',
				content: 'Original',
				created_at: '2025-01-01T00:00:00Z',
				reaction: null,
				parent_message_id: null
			};

			messages.addMessage(message);
			messages.updateMessage(1, { reaction: 'thumbs_up' });

			const state = get(messages);
			expect(state.items[0].reaction).toBe('thumbs_up');
			expect(state.items[0].content).toBe('Original'); // Other fields unchanged
		});

		it('should not update messages with different id', () => {
			const message: Message = {
				id: 1,
				conversation_id: 1,
				role: 'assistant',
				content: 'Test',
				created_at: '2025-01-01T00:00:00Z',
				reaction: null,
				parent_message_id: null
			};

			messages.addMessage(message);
			messages.updateMessage(999, { reaction: 'thumbs_up' });

			const state = get(messages);
			expect(state.items[0].reaction).toBeNull();
		});
	});

	describe('streaming', () => {
		it('should start streaming with message id', () => {
			messages.startStreaming(42);

			const state = get(messages);
			expect(state.isStreaming).toBe(true);
			expect(state.streamingMessageId).toBe(42);
			expect(state.streamingContent).toBe('');
		});

		it('should append tokens during streaming', () => {
			messages.startStreaming(1);
			messages.appendStreamingToken('Hello');
			messages.appendStreamingToken(' ');
			messages.appendStreamingToken('world');

			const state = get(messages);
			expect(state.streamingContent).toBe('Hello world');
		});

		it('should finish streaming and add message', () => {
			messages.startStreaming(1);
			messages.appendStreamingToken('Streamed content');

			const completeMessage: Message = {
				id: 1,
				conversation_id: 1,
				role: 'assistant',
				content: '', // Backend sends empty, will use streamingContent
				created_at: '2025-01-01T00:00:00Z',
				reaction: null,
				parent_message_id: null,
				token_count: 10,
				model_name: 'gpt-oss-20b',
				completion_time_ms: 1500
			};

			messages.finishStreaming(completeMessage);

			const state = get(messages);
			expect(state.isStreaming).toBe(false);
			expect(state.streamingMessageId).toBeNull();
			expect(state.streamingContent).toBe('');
			expect(state.items).toHaveLength(1);
			expect(state.items[0].content).toBe('Streamed content');
		});

		it('should use messageData.content when provided', () => {
			messages.startStreaming(1);
			messages.appendStreamingToken('Streamed content');

			const completeMessage: Message = {
				id: 1,
				conversation_id: 1,
				role: 'assistant',
				content: 'Backend content', // Backend provides content
				created_at: '2025-01-01T00:00:00Z',
				reaction: null,
				parent_message_id: null
			};

			messages.finishStreaming(completeMessage);

			const state = get(messages);
			expect(state.items[0].content).toBe('Backend content');
		});

		it('should cancel streaming', () => {
			messages.startStreaming(1);
			messages.appendStreamingToken('Partial');
			messages.cancelStreaming();

			const state = get(messages);
			expect(state.isStreaming).toBe(false);
			expect(state.streamingMessageId).toBeNull();
			expect(state.streamingContent).toBe('');
			expect(state.items).toHaveLength(0); // No message added
		});
	});

	describe('error handling', () => {
		it('should set error message', () => {
			messages.setError('Test error');

			const state = get(messages);
			expect(state.error).toBe('Test error');
			expect(state.isLoading).toBe(false);
			expect(state.isStreaming).toBe(false);
		});

		it('should clear error message', () => {
			messages.setError('Test error');
			messages.clearError();

			const state = get(messages);
			expect(state.error).toBeNull();
		});
	});

	describe('reset', () => {
		it('should reset to initial state', () => {
			const message: Message = {
				id: 1,
				conversation_id: 1,
				role: 'user',
				content: 'Test',
				created_at: '2025-01-01T00:00:00Z',
				reaction: null,
				parent_message_id: null
			};

			messages.addMessage(message);
			messages.setLoading(true);
			messages.setError('Error');
			messages.startStreaming(1);

			messages.reset();

			const state = get(messages);
			expect(state.items).toEqual([]);
			expect(state.isLoading).toBe(false);
			expect(state.error).toBeNull();
			expect(state.isStreaming).toBe(false);
			expect(state.streamingMessageId).toBeNull();
			expect(state.streamingContent).toBe('');
		});
	});
});
