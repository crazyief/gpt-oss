/**
 * API client service
 *
 * Purpose: Centralized API communication layer with mock data fallback
 *
 * Development strategy:
 * - TEMPORARY: Uses mock data for development (backend not ready yet)
 * - TODO: Replace mock implementations with real fetch() calls to backend
 * - Keeps consistent interface: Components don't change when switching to real API
 *
 * Design decisions:
 * - Async functions: Simulate network delay, prepare for real async API calls
 * - Error handling: Return consistent error format matching backend API
 * - Type safety: All functions return typed Promise<T> matching API contracts
 *
 * WHY separate API client from components:
 * - Single source of truth: All API calls go through one layer
 * - Easy testing: Mock entire API client in tests
 * - Easy migration: Change mock to real API in one file, components unchanged
 * - Consistent error handling: Centralized retry logic, error formatting
 *
 * Migration plan:
 * 1. Backend-Agent completes CRUD endpoints (Phase 2)
 * 2. Replace mock function bodies with fetch() calls
 * 3. Keep function signatures identical (no component changes needed)
 * 4. Move mock data to tests directory for unit testing
 */

import type {
	Project,
	Conversation,
	Message,
	ProjectListResponse,
	ConversationListResponse,
	MessageListResponse,
	CreateProjectRequest,
	CreateConversationRequest,
	UpdateConversationRequest,
	MessageReaction
} from '$lib/types';
import { mockProjects, mockConversations } from '$lib/mocks/mockConversations';
import { API_ENDPOINTS } from '$lib/config';

/**
 * Simulate network delay for realistic development experience
 *
 * WHY simulate delay in mock API:
 * - Reveals loading states: Forces UI to show loading spinners (tests UX)
 * - Realistic timing: Real API calls take 50-500ms, mock should too
 * - Race condition testing: Helps catch async bugs (e.g., user clicking twice)
 * - Prevents false confidence: Instant responses hide performance issues
 *
 * @param ms - Delay duration in milliseconds (default 300ms = typical API latency)
 */
function simulateDelay(ms: number = 300): Promise<void> {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Projects API
 *
 * CRUD operations for project management
 */

/**
 * Fetch all projects
 *
 * TEMPORARY: Returns mock data
 * TODO: Replace with fetch(API_ENDPOINTS.projects.list)
 *
 * @returns Promise resolving to project list with total count
 */
export async function fetchProjects(): Promise<ProjectListResponse> {
	await simulateDelay();

	// MOCK IMPLEMENTATION - Replace with real API call:
	// const response = await fetch(API_ENDPOINTS.projects.list);
	// if (!response.ok) throw new Error('Failed to fetch projects');
	// return await response.json();

	return {
		projects: mockProjects,
		total_count: mockProjects.length
	};
}

/**
 * Fetch single project by ID
 *
 * TEMPORARY: Returns mock data
 * TODO: Replace with fetch(API_ENDPOINTS.projects.get(id))
 *
 * @param projectId - Project ID
 * @returns Promise resolving to project object
 */
export async function fetchProject(projectId: number): Promise<Project> {
	await simulateDelay();

	// MOCK IMPLEMENTATION
	const project = mockProjects.find((p) => p.id === projectId);
	if (!project) {
		throw new Error(`Project ${projectId} not found`);
	}

	return project;
}

/**
 * Create new project
 *
 * TEMPORARY: Simulates creation, returns mock object
 * TODO: Replace with POST fetch(API_ENDPOINTS.projects.create, { body: JSON.stringify(data) })
 *
 * @param data - Project creation request
 * @returns Promise resolving to created project
 */
export async function createProject(data: CreateProjectRequest): Promise<Project> {
	await simulateDelay();

	// MOCK IMPLEMENTATION
	const newProject: Project = {
		id: Math.max(...mockProjects.map((p) => p.id)) + 1, // Auto-increment ID
		name: data.name,
		description: data.description || null,
		created_at: new Date().toISOString(),
		updated_at: new Date().toISOString(),
		conversation_count: 0
	};

	return newProject;
}

/**
 * Delete project by ID
 *
 * TEMPORARY: Simulates deletion
 * TODO: Replace with DELETE fetch(API_ENDPOINTS.projects.delete(id))
 *
 * @param projectId - Project ID to delete
 */
export async function deleteProject(projectId: number): Promise<void> {
	await simulateDelay();

	// MOCK IMPLEMENTATION
	const index = mockProjects.findIndex((p) => p.id === projectId);
	if (index === -1) {
		throw new Error(`Project ${projectId} not found`);
	}

	// In real implementation, just call DELETE endpoint
	// Backend handles cascade deletion of conversations
}

/**
 * Conversations API
 *
 * CRUD operations for conversation management
 */

/**
 * Fetch conversations, optionally filtered by project
 *
 * TEMPORARY: Returns mock data
 * TODO: Replace with fetch(API_ENDPOINTS.conversations.list + query params)
 *
 * WHY optional projectId parameter:
 * - Flexibility: Can fetch all conversations or filter by project
 * - Query params: Mirrors backend API design (?project_id=123)
 * - Component reuse: Same function works for sidebar (all) and project view (filtered)
 *
 * @param projectId - Optional project ID to filter conversations
 * @param limit - Max number of conversations to return (pagination)
 * @param offset - Offset for pagination
 * @returns Promise resolving to conversation list
 */
export async function fetchConversations(
	projectId?: number,
	limit: number = 50,
	offset: number = 0
): Promise<ConversationListResponse> {
	await simulateDelay();

	// MOCK IMPLEMENTATION
	let filtered = mockConversations;

	// Filter by project if specified
	if (projectId !== undefined) {
		filtered = filtered.filter((c) => c.project_id === projectId);
	}

	// Simulate pagination
	const paginated = filtered.slice(offset, offset + limit);

	return {
		conversations: paginated,
		total_count: filtered.length
	};
}

/**
 * Fetch single conversation by ID
 *
 * TEMPORARY: Returns mock data
 * TODO: Replace with fetch(API_ENDPOINTS.conversations.get(id))
 *
 * @param conversationId - Conversation ID
 * @returns Promise resolving to conversation object
 */
export async function fetchConversation(conversationId: number): Promise<Conversation> {
	await simulateDelay();

	// MOCK IMPLEMENTATION
	const conversation = mockConversations.find((c) => c.id === conversationId);
	if (!conversation) {
		throw new Error(`Conversation ${conversationId} not found`);
	}

	return conversation;
}

/**
 * Create new conversation
 *
 * TEMPORARY: Simulates creation
 * TODO: Replace with POST fetch(API_ENDPOINTS.conversations.create)
 *
 * WHY auto-generate title if not provided:
 * - Better UX: User doesn't have to think of title upfront
 * - Backend handles: Real API generates title from first message
 * - Consistent: Mock behavior matches backend behavior
 *
 * @param data - Conversation creation request
 * @returns Promise resolving to created conversation
 */
export async function createConversation(
	data: CreateConversationRequest
): Promise<Conversation> {
	await simulateDelay();

	// MOCK IMPLEMENTATION
	const newConversation: Conversation = {
		id: Math.max(...mockConversations.map((c) => c.id)) + 1,
		project_id: data.project_id || null,
		title: data.title || 'New Conversation',
		created_at: new Date().toISOString(),
		updated_at: new Date().toISOString(),
		last_message_at: null,
		message_count: 0
	};

	return newConversation;
}

/**
 * Update conversation (e.g., rename)
 *
 * TEMPORARY: Simulates update
 * TODO: Replace with PATCH fetch(API_ENDPOINTS.conversations.update(id))
 *
 * @param conversationId - Conversation ID to update
 * @param data - Partial conversation data
 * @returns Promise resolving to updated conversation
 */
export async function updateConversation(
	conversationId: number,
	data: UpdateConversationRequest
): Promise<Conversation> {
	await simulateDelay();

	// MOCK IMPLEMENTATION
	const conversation = mockConversations.find((c) => c.id === conversationId);
	if (!conversation) {
		throw new Error(`Conversation ${conversationId} not found`);
	}

	return {
		...conversation,
		...data,
		updated_at: new Date().toISOString()
	};
}

/**
 * Delete conversation by ID
 *
 * TEMPORARY: Simulates deletion
 * TODO: Replace with DELETE fetch(API_ENDPOINTS.conversations.delete(id))
 *
 * @param conversationId - Conversation ID to delete
 */
export async function deleteConversation(conversationId: number): Promise<void> {
	await simulateDelay();

	// MOCK IMPLEMENTATION
	const index = mockConversations.findIndex((c) => c.id === conversationId);
	if (index === -1) {
		throw new Error(`Conversation ${conversationId} not found`);
	}

	// In real implementation, just call DELETE endpoint
	// Backend handles cascade deletion of messages
}

/**
 * Messages API
 *
 * Fetch message history (sending messages uses SSE endpoint)
 */

/**
 * Fetch messages for conversation
 *
 * TEMPORARY: Returns empty array (mock messages not implemented yet)
 * TODO: Replace with fetch(API_ENDPOINTS.messages.get(conversationId))
 *
 * WHY return empty array instead of mock messages:
 * - Simplicity: Message mock data is complex (markdown content, reactions)
 * - SSE focus: Task-006 focuses on streaming, not history loading
 * - Future work: Add mock messages when implementing message history UI
 *
 * @param conversationId - Conversation ID
 * @param limit - Max number of messages (pagination)
 * @param offset - Offset for pagination
 * @returns Promise resolving to message list
 */
export async function fetchMessages(
	conversationId: number,
	limit: number = 50,
	offset: number = 0
): Promise<MessageListResponse> {
	await simulateDelay();

	// MOCK IMPLEMENTATION - Return empty for now
	// TODO: Add mock message data when implementing message history
	return {
		messages: [],
		total_count: 0
	};
}

/**
 * Add or update message reaction
 *
 * TEMPORARY: Simulates reaction update
 * TODO: Replace with POST fetch(API_ENDPOINTS.messages.reaction(messageId))
 *
 * @param messageId - Message ID
 * @param reaction - Reaction type (thumbs_up, thumbs_down, null)
 */
export async function updateMessageReaction(
	messageId: number,
	reaction: MessageReaction
): Promise<void> {
	await simulateDelay();

	// MOCK IMPLEMENTATION
	// In real implementation, backend persists reaction to database
	console.log(`[MOCK] Updated message ${messageId} reaction to ${reaction}`);
}
