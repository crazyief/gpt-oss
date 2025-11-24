/**
 * Messages API client
 *
 * Handles all message-related API operations (CRUD + reactions).
 * All functions use shared apiRequest wrapper with automatic error handling.
 */

import { apiRequest } from './base';
import { toast } from '$lib/stores/toast';
import type { Message, MessageRole, MessageReaction } from '$lib/types';

/**
 * Fetch single message by ID.
 *
 * @param id - Message ID
 * @returns Promise<Message> - The message data
 * @throws Error if message not found or API call fails
 *
 * @example
 * const message = await getMessage(42);
 * console.log(message.content);
 */
export async function getMessage(id: number): Promise<Message> {
	return apiRequest<Message>(`/api/messages/${id}`);
}

/**
 * Create new message in a conversation.
 *
 * Note: This is typically used for creating user messages.
 * Assistant messages are created automatically via the chat streaming endpoint.
 *
 * @param conversationId - Conversation ID to add message to
 * @param content - Message content (markdown text)
 * @param role - Message role (defaults to 'user')
 * @returns Promise<Message> - The created message
 * @throws Error if conversation not found or API call fails
 *
 * @example
 * const message = await createMessage(123, 'Hello, how are you?', 'user');
 * console.log(message.id);
 */
export async function createMessage(
	conversationId: number,
	content: string,
	role: MessageRole = 'user'
): Promise<Message> {
	const message = await apiRequest<Message>('/api/messages/create', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			conversation_id: conversationId,
			content,
			role
		})
	});

	return message;
}

/**
 * Update existing message.
 *
 * Note: Typically used for updating message content or metadata.
 * Use updateMessageReaction() for updating reactions.
 *
 * @param id - Message ID
 * @param data - Partial message data to update
 * @returns Promise<Message> - The updated message
 * @throws Error if message not found or API call fails
 *
 * @example
 * const message = await updateMessage(42, { content: 'Updated content' });
 */
export async function updateMessage(
	id: number,
	data: Partial<Pick<Message, 'content' | 'metadata'>>
): Promise<Message> {
	const message = await apiRequest<Message>(`/api/messages/${id}/update`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});

	// Show success toast
	toast.success('Message updated successfully');

	return message;
}

/**
 * Update message reaction (thumbs up/down).
 *
 * @param messageId - Message ID to react to
 * @param reaction - Reaction type ('thumbs_up', 'thumbs_down', or null to remove)
 * @returns Promise<Message> - The updated message with new reaction
 * @throws Error if message not found or API call fails
 *
 * @example
 * const message = await updateMessageReaction(42, 'thumbs_up');
 * // Remove reaction
 * const message2 = await updateMessageReaction(42, null);
 */
export async function updateMessageReaction(
	messageId: number,
	reaction: MessageReaction
): Promise<Message> {
	return apiRequest<Message>(`/api/messages/${messageId}/reaction`, {
		method: 'PATCH',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ reaction })
	});
}
