/**
 * Message factory for SSE client
 *
 * Purpose: Create complete message objects from SSE events
 *
 * Refactored from sse-client.ts to comply with 400-line limit
 */

import type { Message } from '$lib/types';

/**
 * Fetch complete message from backend
 *
 * WHY fetch from backend instead of using streamed content:
 * - Authoritative: Backend is source of truth
 * - Metadata: Backend adds token_count, model_name, timestamps
 * - Validation: Ensures streamed content matches stored content
 *
 * @param messageId - Message ID to fetch
 * @param conversationId - Conversation ID
 * @param tokenCount - Number of tokens generated (from SSE complete event)
 * @param completionTimeMs - Time taken to generate response in milliseconds
 * @returns Complete message object
 */
export async function fetchCompleteMessage(
	messageId: number,
	conversationId: number,
	tokenCount: number,
	completionTimeMs: number
): Promise<Message> {
	// TODO: Implement GET /api/messages/{conversationId} endpoint
	// For now, construct message from streamed content with actual metadata

	// TEMPORARY: This would normally fetch from backend
	// Backend provides authoritative message with all metadata
	return {
		id: messageId,
		conversation_id: conversationId,
		role: 'assistant',
		content: '', // Will be populated by finishStreaming with streamingContent
		created_at: new Date().toISOString(),
		reaction: null,
		parent_message_id: null,
		token_count: tokenCount, // Use actual value from SSE event
		model_name: 'gpt-oss-20b',
		completion_time_ms: completionTimeMs // Use actual value from SSE event
	} as Message;
}
