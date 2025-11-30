/**
 * Unit tests for conversations store
 *
 * Tests: State mutations, CRUD operations, derived stores (filtering, sorting), error handling
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import {
	conversations,
	currentConversationId,
	filteredConversations,
	sortedFilteredConversations
} from './conversations';
import type { Conversation } from '$lib/types';

describe('conversations store', () => {
	beforeEach(() => {
		conversations.reset();
		currentConversationId.set(null);
	});

	describe('initial state', () => {
		it('should start with empty items', () => {
			const state = get(conversations);
			expect(state.items).toEqual([]);
		});

		it('should have loading = false initially', () => {
			const state = get(conversations);
			expect(state.isLoading).toBe(false);
		});

		it('should have no error initially', () => {
			const state = get(conversations);
			expect(state.error).toBeNull();
		});

		it('should have empty search query initially', () => {
			const state = get(conversations);
			expect(state.searchQuery).toBe('');
		});
	});

	describe('setLoading', () => {
		it('should set loading to true', () => {
			conversations.setLoading(true);
			const state = get(conversations);
			expect(state.isLoading).toBe(true);
		});

		it('should set loading to false', () => {
			conversations.setLoading(true);
			conversations.setLoading(false);
			const state = get(conversations);
			expect(state.isLoading).toBe(false);
		});
	});

	describe('setConversations', () => {
		it('should set conversations array', () => {
			const testConversations: Conversation[] = [
				{
					id: 1,
					project_id: 1,
					title: 'Test Conversation',
					created_at: '2025-01-01T00:00:00Z',
					updated_at: '2025-01-01T00:00:00Z',
					last_message_at: '2025-01-01T00:00:00Z'
				}
			];

			conversations.setConversations(testConversations);
			const state = get(conversations);
			expect(state.items).toEqual(testConversations);
		});

		it('should clear loading and error when setting conversations', () => {
			conversations.setLoading(true);
			conversations.setError('Test error');

			const testConversations: Conversation[] = [];
			conversations.setConversations(testConversations);

			const state = get(conversations);
			expect(state.isLoading).toBe(false);
			expect(state.error).toBeNull();
		});

		it('should clear search query when setting conversations', () => {
			conversations.setSearchQuery('test query');
			conversations.setConversations([]);

			const state = get(conversations);
			expect(state.searchQuery).toBe('');
		});
	});

	describe('addConversation', () => {
		it('should add conversation to items', () => {
			const conversation: Conversation = {
				id: 1,
				project_id: 1,
				title: 'New Conversation',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				last_message_at: null
			};

			conversations.addConversation(conversation);
			const state = get(conversations);
			expect(state.items).toHaveLength(1);
			expect(state.items[0]).toEqual(conversation);
		});

		it('should prepend new conversation (optimistic update pattern)', () => {
			const conv1: Conversation = {
				id: 1,
				project_id: 1,
				title: 'First',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				last_message_at: null
			};

			const conv2: Conversation = {
				id: 2,
				project_id: 1,
				title: 'Second',
				created_at: '2025-01-01T01:00:00Z',
				updated_at: '2025-01-01T01:00:00Z',
				last_message_at: null
			};

			conversations.addConversation(conv1);
			conversations.addConversation(conv2);

			const state = get(conversations);
			expect(state.items).toHaveLength(2);
			expect(state.items[0]).toEqual(conv2); // Latest first
		});
	});

	describe('updateConversation', () => {
		it('should update conversation by id', () => {
			const conversation: Conversation = {
				id: 1,
				project_id: 1,
				title: 'Original Title',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				last_message_at: null
			};

			conversations.addConversation(conversation);
			conversations.updateConversation(1, { title: 'Updated Title' });

			const state = get(conversations);
			expect(state.items[0].title).toBe('Updated Title');
		});

		it('should update last_message_at timestamp', () => {
			const conversation: Conversation = {
				id: 1,
				project_id: 1,
				title: 'Test',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				last_message_at: null
			};

			conversations.addConversation(conversation);
			conversations.updateConversation(1, { last_message_at: '2025-01-01T12:00:00Z' });

			const state = get(conversations);
			expect(state.items[0].last_message_at).toBe('2025-01-01T12:00:00Z');
		});

		it('should not update conversations with different id', () => {
			const conversation: Conversation = {
				id: 1,
				project_id: 1,
				title: 'Test Conversation',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				last_message_at: null
			};

			conversations.addConversation(conversation);
			conversations.updateConversation(999, { title: 'Should Not Update' });

			const state = get(conversations);
			expect(state.items[0].title).toBe('Test Conversation');
		});
	});

	describe('removeConversation', () => {
		it('should remove conversation by id', () => {
			const conversation: Conversation = {
				id: 1,
				project_id: 1,
				title: 'To Remove',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				last_message_at: null
			};

			conversations.addConversation(conversation);
			conversations.removeConversation(1);

			const state = get(conversations);
			expect(state.items).toHaveLength(0);
		});

		it('should not remove conversations with different id', () => {
			const conversation: Conversation = {
				id: 1,
				project_id: 1,
				title: 'Keep Me',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				last_message_at: null
			};

			conversations.addConversation(conversation);
			conversations.removeConversation(999);

			const state = get(conversations);
			expect(state.items).toHaveLength(1);
		});
	});

	describe('setSearchQuery', () => {
		it('should update search query', () => {
			conversations.setSearchQuery('test query');

			const state = get(conversations);
			expect(state.searchQuery).toBe('test query');
		});

		it('should support empty query', () => {
			conversations.setSearchQuery('test');
			conversations.setSearchQuery('');

			const state = get(conversations);
			expect(state.searchQuery).toBe('');
		});
	});

	describe('error handling', () => {
		it('should set error message', () => {
			conversations.setError('Test error');

			const state = get(conversations);
			expect(state.error).toBe('Test error');
			expect(state.isLoading).toBe(false);
		});

		it('should clear error message', () => {
			conversations.setError('Test error');
			conversations.clearError();

			const state = get(conversations);
			expect(state.error).toBeNull();
		});
	});

	describe('reset', () => {
		it('should reset to initial state', () => {
			const conversation: Conversation = {
				id: 1,
				project_id: 1,
				title: 'Test',
				created_at: '2025-01-01T00:00:00Z',
				updated_at: '2025-01-01T00:00:00Z',
				last_message_at: null
			};

			conversations.addConversation(conversation);
			conversations.setLoading(true);
			conversations.setError('Error');
			conversations.setSearchQuery('query');

			conversations.reset();

			const state = get(conversations);
			expect(state.items).toEqual([]);
			expect(state.isLoading).toBe(false);
			expect(state.error).toBeNull();
			expect(state.searchQuery).toBe('');
		});
	});

	describe('filteredConversations derived store', () => {
		beforeEach(() => {
			const testConversations: Conversation[] = [
				{
					id: 1,
					project_id: 1,
					title: 'API Integration Project',
					created_at: '2025-01-01T00:00:00Z',
					updated_at: '2025-01-01T00:00:00Z',
					last_message_at: '2025-01-01T12:00:00Z'
				},
				{
					id: 2,
					project_id: 1,
					title: 'UI Design Discussion',
					created_at: '2025-01-02T00:00:00Z',
					updated_at: '2025-01-02T00:00:00Z',
					last_message_at: '2025-01-02T14:00:00Z'
				},
				{
					id: 3,
					project_id: 1,
					title: 'Database Schema',
					created_at: '2025-01-03T00:00:00Z',
					updated_at: '2025-01-03T00:00:00Z',
					last_message_at: null
				}
			];

			conversations.setConversations(testConversations);
		});

		it('should return all conversations when search query is empty', () => {
			conversations.setSearchQuery('');

			const filtered = get(filteredConversations);
			expect(filtered).toHaveLength(3);
		});

		it('should filter by title (case-insensitive)', () => {
			conversations.setSearchQuery('api');

			const filtered = get(filteredConversations);
			expect(filtered).toHaveLength(1);
			expect(filtered[0].title).toBe('API Integration Project');
		});

		it('should support partial matches', () => {
			conversations.setSearchQuery('design');

			const filtered = get(filteredConversations);
			expect(filtered).toHaveLength(1);
			expect(filtered[0].title).toBe('UI Design Discussion');
		});

		it('should support uppercase search query', () => {
			conversations.setSearchQuery('DATABASE');

			const filtered = get(filteredConversations);
			expect(filtered).toHaveLength(1);
			expect(filtered[0].title).toBe('Database Schema');
		});

		it('should return empty array when no matches', () => {
			conversations.setSearchQuery('nonexistent');

			const filtered = get(filteredConversations);
			expect(filtered).toHaveLength(0);
		});

		it('should update reactively when search query changes', () => {
			conversations.setSearchQuery('api');
			let filtered = get(filteredConversations);
			expect(filtered).toHaveLength(1);

			conversations.setSearchQuery('');
			filtered = get(filteredConversations);
			expect(filtered).toHaveLength(3);
		});
	});

	describe('sortedFilteredConversations derived store', () => {
		it('should sort by last_message_at (newest first)', () => {
			const testConversations: Conversation[] = [
				{
					id: 1,
					project_id: 1,
					title: 'Oldest Activity',
					created_at: '2025-01-01T00:00:00Z',
					updated_at: '2025-01-01T00:00:00Z',
					last_message_at: '2025-01-01T10:00:00Z'
				},
				{
					id: 2,
					project_id: 1,
					title: 'Newest Activity',
					created_at: '2025-01-02T00:00:00Z',
					updated_at: '2025-01-02T00:00:00Z',
					last_message_at: '2025-01-03T12:00:00Z'
				},
				{
					id: 3,
					project_id: 1,
					title: 'Middle Activity',
					created_at: '2025-01-03T00:00:00Z',
					updated_at: '2025-01-03T00:00:00Z',
					last_message_at: '2025-01-02T11:00:00Z'
				}
			];

			conversations.setConversations(testConversations);

			const sorted = get(sortedFilteredConversations);
			expect(sorted).toHaveLength(3);
			expect(sorted[0].title).toBe('Newest Activity');
			expect(sorted[1].title).toBe('Middle Activity');
			expect(sorted[2].title).toBe('Oldest Activity');
		});

		it('should put conversations with no messages at bottom', () => {
			const testConversations: Conversation[] = [
				{
					id: 1,
					project_id: 1,
					title: 'Empty Conversation',
					created_at: '2025-01-01T00:00:00Z',
					updated_at: '2025-01-01T00:00:00Z',
					last_message_at: null
				},
				{
					id: 2,
					project_id: 1,
					title: 'Has Messages',
					created_at: '2025-01-02T00:00:00Z',
					updated_at: '2025-01-02T00:00:00Z',
					last_message_at: '2025-01-02T12:00:00Z'
				}
			];

			conversations.setConversations(testConversations);

			const sorted = get(sortedFilteredConversations);
			expect(sorted[0].title).toBe('Has Messages');
			expect(sorted[1].title).toBe('Empty Conversation');
		});

		it('should handle multiple empty conversations', () => {
			const testConversations: Conversation[] = [
				{
					id: 1,
					project_id: 1,
					title: 'Empty 1',
					created_at: '2025-01-01T00:00:00Z',
					updated_at: '2025-01-01T00:00:00Z',
					last_message_at: null
				},
				{
					id: 2,
					project_id: 1,
					title: 'Empty 2',
					created_at: '2025-01-02T00:00:00Z',
					updated_at: '2025-01-02T00:00:00Z',
					last_message_at: null
				}
			];

			conversations.setConversations(testConversations);

			const sorted = get(sortedFilteredConversations);
			expect(sorted).toHaveLength(2);
			// Both are empty, so order doesn't matter (they're equal)
		});

		it('should sort and filter combined', () => {
			const testConversations: Conversation[] = [
				{
					id: 1,
					project_id: 1,
					title: 'API Test Old',
					created_at: '2025-01-01T00:00:00Z',
					updated_at: '2025-01-01T00:00:00Z',
					last_message_at: '2025-01-01T10:00:00Z'
				},
				{
					id: 2,
					project_id: 1,
					title: 'API Test New',
					created_at: '2025-01-02T00:00:00Z',
					updated_at: '2025-01-02T00:00:00Z',
					last_message_at: '2025-01-02T12:00:00Z'
				},
				{
					id: 3,
					project_id: 1,
					title: 'UI Design',
					created_at: '2025-01-03T00:00:00Z',
					updated_at: '2025-01-03T00:00:00Z',
					last_message_at: '2025-01-03T14:00:00Z'
				}
			];

			conversations.setConversations(testConversations);
			conversations.setSearchQuery('api');

			const sorted = get(sortedFilteredConversations);
			expect(sorted).toHaveLength(2);
			expect(sorted[0].title).toBe('API Test New'); // Newest API first
			expect(sorted[1].title).toBe('API Test Old');
		});
	});

	describe('currentConversationId store', () => {
		it('should start as null', () => {
			const id = get(currentConversationId);
			expect(id).toBeNull();
		});

		it('should update when set', () => {
			currentConversationId.set(42);
			const id = get(currentConversationId);
			expect(id).toBe(42);
		});

		it('should support null (no active conversation)', () => {
			currentConversationId.set(5);
			currentConversationId.set(null);
			const id = get(currentConversationId);
			expect(id).toBeNull();
		});

		it('should be independent of conversations store', () => {
			// Setting current ID shouldn't affect conversations list
			currentConversationId.set(123);

			const state = get(conversations);
			expect(state.items).toEqual([]);
		});
	});
});
