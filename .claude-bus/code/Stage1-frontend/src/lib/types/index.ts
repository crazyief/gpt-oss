/**
 * TypeScript type definitions for GPT-OSS frontend
 *
 * Purpose: Centralized type definitions matching backend API contracts
 *
 * Type organization:
 * - Data models (Project, Conversation, Message)
 * - API request/response types
 * - UI state types
 * - SSE event types
 *
 * Note: These types match the API contracts in:
 * - .claude-bus/contracts/Stage1-api-001.json (Projects)
 * - .claude-bus/contracts/Stage1-api-002.json (Conversations)
 * - .claude-bus/contracts/Stage1-api-003.json (Chat/Messages)
 */

/**
 * Project data model
 *
 * Represents a top-level organizational unit for conversations
 */
export interface Project {
	id: number;
	name: string;
	description: string | null;
	created_at: string; // ISO 8601 datetime
	updated_at: string;
	metadata?: Record<string, unknown>;
	conversation_count?: number; // Included in list endpoint
}

/**
 * Conversation data model
 *
 * Represents a chat session/thread
 */
export interface Conversation {
	id: number;
	project_id: number | null;
	title: string;
	created_at: string; // ISO 8601 datetime
	updated_at: string;
	last_message_at: string | null;
	message_count: number;
	metadata?: Record<string, unknown>;
}

/**
 * Message role enum
 *
 * Indicates whether message is from user or assistant
 */
export type MessageRole = 'user' | 'assistant';

/**
 * Message reaction enum
 *
 * User feedback on assistant messages (thumbs up/down)
 */
export type MessageReaction = 'thumbs_up' | 'thumbs_down' | null;

/**
 * Message data model
 *
 * Represents a single message in a conversation
 */
export interface Message {
	id: number;
	conversation_id: number;
	role: MessageRole;
	content: string; // Markdown text
	created_at: string; // ISO 8601 datetime
	reaction: MessageReaction;
	parent_message_id: number | null; // For regenerate feature
	token_count: number;
	model_name?: string; // Only for assistant messages
	completion_time_ms?: number; // Only for assistant messages
	metadata?: Record<string, unknown>;
}

/**
 * API request types
 *
 * Types for POST/PATCH request bodies
 */
export interface CreateProjectRequest {
	name: string;
	description?: string;
}

export interface CreateConversationRequest {
	project_id?: number;
	title?: string;
}

export interface UpdateConversationRequest {
	title?: string;
}

export interface ChatStreamRequest {
	conversation_id: number;
	message: string;
}

export interface MessageReactionRequest {
	reaction: MessageReaction;
}

/**
 * API response types
 *
 * Types for paginated list endpoints
 */
export interface ProjectListResponse {
	projects: Project[];
	total_count: number;
}

export interface ConversationListResponse {
	conversations: Conversation[];
	total_count: number;
}

export interface MessageListResponse {
	messages: Message[];
	total_count: number;
}

export interface HealthCheckResponse {
	status: string;
	llm_service: string;
	database: string;
}

/**
 * SSE event types
 *
 * Types for Server-Sent Events from /api/chat/stream
 */

/**
 * SSE token event
 *
 * Sent for each LLM token as it's generated
 */
export interface SSETokenEvent {
	token: string;
	message_id: number;
	session_id: string; // UUID for stream cancellation
}

/**
 * SSE complete event
 *
 * Sent when stream finishes successfully
 */
export interface SSECompleteEvent {
	message_id: number;
	token_count: number;
	completion_time_ms: number;
}

/**
 * SSE error event
 *
 * Sent when error occurs during streaming
 */
export interface SSEErrorEvent {
	error: string; // User-friendly error message
	error_type: string; // Error category (validation_error, service_error, etc.)
}

/**
 * SSE event type discriminator
 *
 * Union type for all possible SSE events
 */
export type SSEEvent =
	| { type: 'token'; data: SSETokenEvent }
	| { type: 'complete'; data: SSECompleteEvent }
	| { type: 'error'; data: SSEErrorEvent };

/**
 * UI state types
 *
 * Types for client-side state management
 */

/**
 * Sidebar state
 *
 * Tracks sidebar visibility and search state
 */
export interface SidebarState {
	isOpen: boolean;
	searchQuery: string;
}

/**
 * Chat state
 *
 * Tracks current conversation and streaming state
 */
export interface ChatState {
	currentConversationId: number | null;
	messages: Message[];
	isStreaming: boolean;
	streamingMessageId: number | null;
	streamingContent: string; // Accumulated tokens during streaming
	error: string | null;
}

/**
 * SSE connection state
 *
 * Tracks EventSource connection status
 */
export interface SSEConnectionState {
	eventSource: EventSource | null;
	sessionId: string | null; // UUID for cancellation
	retryCount: number;
	status: 'disconnected' | 'connecting' | 'connected' | 'error';
}

/**
 * API error response
 *
 * Standardized error format from backend
 */
export interface APIError {
	detail: string;
}
