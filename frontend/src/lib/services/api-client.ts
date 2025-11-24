/**
 * API client service
 *
 * Purpose: Centralized API communication layer for backend integration
 *
 * Design decisions:
 * - Async functions: All API calls use fetch() with real backend endpoints
 * - Error handling: Consistent error format from backend API responses
 * - Type safety: All functions return typed Promise<T> matching API contracts
 * - Proxy routing: Vite dev server proxies /api/* requests to backend
 *
 * WHY separate API client from components:
 * - Single source of truth: All API calls go through one layer
 * - Easy testing: Mock entire API client in tests
 * - Consistent error handling: Centralized error formatting
 * - Clear separation: Components call api-client, never fetch() directly
 *
 * Migration status:
 * ✅ All functions now use REAL backend APIs (no more mock data)
 * ✅ Mock data removed from production code (moved to tests directory)
 * ✅ E2E tests verify real backend integration
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
import { API_ENDPOINTS } from '$lib/config';
import { toast, getErrorMessage } from '$lib/stores/toast';

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
	try {
	// REAL API IMPLEMENTATION
	const response = await fetch(API_ENDPOINTS.projects.list);

	if (!response.ok) {
			const error = await response.json();
			const message = getErrorMessage(error);
			toast.error(`Failed to loadProjects: ${message}`);
			throw new Error(error.detail || 'Failed to fetch projects');
	}

	return await response.json();
	} catch (err) {
		if (err instanceof TypeError) {
			toast.error('Network error. Please check your connection.');
		}
		throw err;
	}
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
	try {
	// REAL API IMPLEMENTATION
	const response = await fetch(API_ENDPOINTS.projects.get(projectId));

	if (!response.ok) {
			const error = await response.json();
			const message = getErrorMessage(error);
			toast.error(`Failed to loadProject: ${message}`);
			throw new Error(error.detail || `Project ${projectId} not found`);
	}

	return await response.json();
	} catch (err) {
		if (err instanceof TypeError) {
			toast.error('Network error. Please check your connection.');
		}
		throw err;
	}
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
	try {
	// REAL API IMPLEMENTATION
	const response = await fetch(API_ENDPOINTS.projects.create, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			name: data.name,
			description: data.description || null
		})
	});

	if (!response.ok) {
			const error = await response.json();
			const message = getErrorMessage(error);
			toast.error(`Failed to createProject: ${message}`);
			throw new Error(error.detail || 'Failed to create project');
	}

	const result = await response.json();
		toast.success('Project created successfully');
		return result;
	} catch (err) {
		if (err instanceof TypeError) {
			toast.error('Network error. Please check your connection.');
		}
		throw err;
	}
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
	try {
	// REAL API IMPLEMENTATION
	const response = await fetch(API_ENDPOINTS.projects.delete(projectId), {
		method: 'DELETE'
	});

	if (!response.ok) {
			const error = await response.json();
			const message = getErrorMessage(error);
			toast.error(`Failed to deleteProject: ${message}`);
			throw new Error(error.detail || `Failed to delete project ${projectId}`);
	}

	// Backend handles cascade deletion of conversations
	} catch (err) {
		if (err instanceof TypeError) {
			toast.error('Network error. Please check your connection.');
		}
		throw err;
	}
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
	try {
	// REAL API IMPLEMENTATION
	const params = new URLSearchParams({
		limit: limit.toString(),
		offset: offset.toString()
	});

	// Add project_id filter if specified
	if (projectId !== undefined) {
		params.append('project_id', projectId.toString());
	}

	const response = await fetch(`${API_ENDPOINTS.conversations.list}?${params.toString()}`);

	if (!response.ok) {
			const error = await response.json();
			const message = getErrorMessage(error);
			toast.error(`Failed to loadConversations: ${message}`);
			throw new Error(error.detail || 'Failed to fetch conversations');
	}

	return await response.json();
	} catch (err) {
		if (err instanceof TypeError) {
			toast.error('Network error. Please check your connection.');
		}
		throw err;
	}
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
	try {
	// REAL API IMPLEMENTATION
	const response = await fetch(API_ENDPOINTS.conversations.get(conversationId));

	if (!response.ok) {
			const error = await response.json();
			const message = getErrorMessage(error);
			toast.error(`Failed to loadConversation: ${message}`);
			throw new Error(error.detail || `Conversation ${conversationId} not found`);
	}

	return await response.json();
	} catch (err) {
		if (err instanceof TypeError) {
			toast.error('Network error. Please check your connection.');
		}
		throw err;
	}
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
	try {
	// REAL API IMPLEMENTATION
	const response = await fetch(API_ENDPOINTS.conversations.create, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			project_id: data.project_id || 1, // Default to project 1 if not specified
			title: data.title || 'New Conversation'
		})
	});

	if (!response.ok) {
			const error = await response.json();
			const message = getErrorMessage(error);
			toast.error(`Failed to createConversation: ${message}`);
			throw new Error(error.detail || 'Failed to create conversation');
	}

	const result = await response.json();
		toast.success('New conversation started');
		return result;
	} catch (err) {
		if (err instanceof TypeError) {
			toast.error('Network error. Please check your connection.');
		}
		throw err;
	}
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
	try {
	// REAL API IMPLEMENTATION
	const response = await fetch(API_ENDPOINTS.conversations.update(conversationId), {
		method: 'PATCH',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});

	if (!response.ok) {
			const error = await response.json();
			const message = getErrorMessage(error);
			toast.error(`Failed to updateConversation: ${message}`);
			throw new Error(error.detail || `Failed to update conversation ${conversationId}`);
	}

	const result = await response.json();
		toast.success('Conversation updated');
		return result;
	} catch (err) {
		if (err instanceof TypeError) {
			toast.error('Network error. Please check your connection.');
		}
		throw err;
	}
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
	try {
	// REAL API IMPLEMENTATION
	const response = await fetch(API_ENDPOINTS.conversations.delete(conversationId), {
		method: 'DELETE'
	});

	if (!response.ok) {
			const error = await response.json();
			const message = getErrorMessage(error);
			toast.error(`Failed to deleteConversation: ${message}`);
			throw new Error(error.detail || `Failed to delete conversation ${conversationId}`);
	}

	// Backend handles cascade deletion of messages
	} catch (err) {
		if (err instanceof TypeError) {
			toast.error('Network error. Please check your connection.');
		}
		throw err;
	}
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
	try {
	// REAL API IMPLEMENTATION
	const params = new URLSearchParams({
		limit: limit.toString(),
		offset: offset.toString()
	});

	const response = await fetch(`${API_ENDPOINTS.messages.get(conversationId)}?${params.toString()}`);

	if (!response.ok) {
			const error = await response.json();
			const message = getErrorMessage(error);
			toast.error(`Failed to loadMessages: ${message}`);
			throw new Error(error.detail || `Failed to fetch messages for conversation ${conversationId}`);
	}

	return await response.json();
	} catch (err) {
		if (err instanceof TypeError) {
			toast.error('Network error. Please check your connection.');
		}
		throw err;
	}
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
	try {
	// REAL API IMPLEMENTATION
	const response = await fetch(API_ENDPOINTS.messages.reaction(messageId), {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ reaction })
	});

	if (!response.ok) {
			const error = await response.json();
			const message = getErrorMessage(error);
			toast.error(`Failed to updateMessageReaction: ${message}`);
			throw new Error(error.detail || `Failed to update reaction for message ${messageId}`);
	}
	} catch (err) {
		if (err instanceof TypeError) {
			toast.error('Network error. Please check your connection.');
		}
		throw err;
	}
}
