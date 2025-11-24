/**
 * Conversations API client
 *
 * Handles all conversation-related API operations (CRUD + message retrieval).
 * All functions use shared apiRequest wrapper with automatic error handling.
 */

import { apiRequest } from './base';
import { API_ENDPOINTS } from '$lib/config';
import { toast } from '$lib/stores/toast';
import type { Conversation, ConversationListResponse, Message, MessageListResponse } from '$lib/types';

/**
 * Fetch all conversations for a project.
 *
 * @param projectId - Project ID to fetch conversations for
 * @returns Promise<Conversation[]> - List of conversations (ordered by updated_at DESC)
 * @throws Error if project not found or API call fails
 *
 * @example
 * const conversations = await getConversations(123);
 * console.log(`Found ${conversations.length} conversations`);
 */
export async function getConversations(projectId: number): Promise<Conversation[]> {
	const response = await apiRequest<ConversationListResponse>(
		`/api/projects/${projectId}/conversations`
	);
	return response.conversations;
}

/**
 * Fetch single conversation by ID.
 *
 * @param id - Conversation ID
 * @returns Promise<Conversation> - The conversation data
 * @throws Error if conversation not found or API call fails
 *
 * @example
 * const conversation = await getConversation(42);
 * console.log(conversation.title);
 */
export async function getConversation(id: number): Promise<Conversation> {
	return apiRequest<Conversation>(API_ENDPOINTS.conversations.get(id));
}

/**
 * Create new conversation.
 *
 * @param projectId - Project ID to create conversation in
 * @param title - Optional conversation title (defaults to "New Chat")
 * @returns Promise<Conversation> - The created conversation
 * @throws Error if project not found or API call fails
 *
 * @example
 * const conversation = await createConversation(123, 'Security Analysis');
 */
export async function createConversation(
	projectId: number,
	title?: string
): Promise<Conversation> {
	const conversation = await apiRequest<Conversation>(API_ENDPOINTS.conversations.create, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			project_id: projectId,
			title: title || 'New Chat'
		})
	});

	// Show success toast
	toast.success('Conversation created successfully');

	return conversation;
}

/**
 * Update existing conversation.
 *
 * @param id - Conversation ID
 * @param data - Partial conversation data to update (typically just title)
 * @returns Promise<Conversation> - The updated conversation
 * @throws Error if conversation not found or API call fails
 *
 * @example
 * const conversation = await updateConversation(42, { title: 'New Title' });
 */
export async function updateConversation(
	id: number,
	data: Partial<Pick<Conversation, 'title'>>
): Promise<Conversation> {
	const conversation = await apiRequest<Conversation>(API_ENDPOINTS.conversations.update(id), {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});

	// Show success toast
	toast.success('Conversation updated successfully');

	return conversation;
}

/**
 * Delete conversation by ID.
 *
 * Note: This will cascade delete all messages in the conversation
 *
 * @param id - Conversation ID to delete
 * @returns Promise<void> - Resolves when deletion completes
 * @throws Error if conversation not found or API call fails
 *
 * @example
 * await deleteConversation(42);
 */
export async function deleteConversation(id: number): Promise<void> {
	await apiRequest<void>(API_ENDPOINTS.conversations.delete(id), {
		method: 'DELETE'
	});

	// Show success toast
	toast.success('Conversation deleted successfully');
}

/**
 * Fetch all messages in a conversation.
 *
 * @param conversationId - Conversation ID to fetch messages for
 * @returns Promise<Message[]> - List of messages (ordered by created_at ASC)
 * @throws Error if conversation not found or API call fails
 *
 * @example
 * const messages = await getConversationMessages(42);
 * console.log(`Found ${messages.length} messages`);
 */
export async function getConversationMessages(conversationId: number): Promise<Message[]> {
	const response = await apiRequest<MessageListResponse>(
		API_ENDPOINTS.messages.get(conversationId)
	);
	return response.messages;
}
