/**
 * MSW Request Handlers
 *
 * Mock API responses for integration testing.
 * Simulates backend API behavior without requiring running backend.
 */

import { http, HttpResponse } from 'msw';

// Mock data store
let projects: any[] = [
	{ id: 1, name: 'Test Project', description: 'Test description', conversation_count: 5, created_at: '2025-01-01T10:00:00Z' },
	{ id: 2, name: 'Demo Project', description: '', conversation_count: 3, created_at: '2025-01-02T10:00:00Z' }
];

let conversations: any[] = [
	{ id: 1, project_id: 1, title: 'Chat 1', message_count: 10, created_at: '2025-01-01T10:00:00Z', updated_at: '2025-01-01T11:00:00Z' },
	{ id: 2, project_id: 1, title: 'Chat 2', message_count: 5, created_at: '2025-01-01T12:00:00Z', updated_at: '2025-01-01T13:00:00Z' }
];

let messages: any[] = [
	{ id: 1, conversation_id: 1, role: 'user', content: 'Hello', created_at: '2025-01-01T10:00:00Z' },
	{ id: 2, conversation_id: 1, role: 'assistant', content: 'Hi there!', created_at: '2025-01-01T10:00:05Z' }
];

let nextProjectId = 3;
let nextConversationId = 3;
let nextMessageId = 3;

// Use relative URLs - in dev mode, the API client uses relative paths
// (Vite proxy handles /api/* → http://localhost:8000/api/*)

export const handlers = [
	// CSRF token
	http.get('/api/csrf-token', () => {
		return HttpResponse.json({ csrf_token: 'mock-csrf-token-12345' });
	}),

	// Projects
	http.get('/api/projects', () => {
		return HttpResponse.json({
			projects: projects.map(p => ({
				...p,
				conversation_count: conversations.filter(c => c.project_id === p.id).length
			}))
		});
	}),

	http.get('/api/projects/list', () => {
		return HttpResponse.json({
			projects: projects.map(p => ({
				...p,
				conversation_count: conversations.filter(c => c.project_id === p.id).length
			}))
		});
	}),

	http.get('/api/projects/:id', ({ params }) => {
		const id = parseInt(params.id as string);
		const project = projects.find(p => p.id === id);
		if (!project) {
			return new HttpResponse(null, { status: 404 });
		}
		return HttpResponse.json(project);
	}),

	http.post('/api/projects/create', async ({ request }) => {
		const body: any = await request.json();
		const project = {
			id: nextProjectId++,
			name: body.name,
			description: body.description || '',
			conversation_count: 0,
			created_at: new Date().toISOString()
		};
		projects.push(project);
		return HttpResponse.json(project);
	}),

	http.put('/api/projects/:id', async ({ params, request }) => {
		const id = parseInt(params.id as string);
		const body: any = await request.json();
		const projectIndex = projects.findIndex(p => p.id === id);
		if (projectIndex === -1) {
			return new HttpResponse(null, { status: 404 });
		}
		projects[projectIndex] = { ...projects[projectIndex], ...body };
		return HttpResponse.json(projects[projectIndex]);
	}),

	http.patch('/api/projects/:id', async ({ params, request }) => {
		const id = parseInt(params.id as string);
		const body: any = await request.json();
		const projectIndex = projects.findIndex(p => p.id === id);
		if (projectIndex === -1) {
			return new HttpResponse(null, { status: 404 });
		}
		projects[projectIndex] = { ...projects[projectIndex], ...body };
		return HttpResponse.json(projects[projectIndex]);
	}),

	http.delete('/api/projects/:id', ({ params }) => {
		const id = parseInt(params.id as string);
		const projectIndex = projects.findIndex(p => p.id === id);
		if (projectIndex === -1) {
			return new HttpResponse(null, { status: 404 });
		}
		// Cascade delete conversations and messages
		const projectConversations = conversations.filter(c => c.project_id === id);
		projectConversations.forEach(conv => {
			messages = messages.filter(m => m.conversation_id !== conv.id);
		});
		conversations = conversations.filter(c => c.project_id !== id);
		projects.splice(projectIndex, 1);
		return new HttpResponse(null, { status: 204 });
	}),

	http.get('/api/projects/:id/stats', ({ params }) => {
		const id = parseInt(params.id as string);
		const projectConversations = conversations.filter(c => c.project_id === id);
		const projectMessages = messages.filter(m =>
			projectConversations.some(c => c.id === m.conversation_id)
		);
		return HttpResponse.json({
			project_id: id,
			document_count: 0,
			conversation_count: projectConversations.length,
			message_count: projectMessages.length,
			total_tokens: projectMessages.length * 50 // Mock token count
		});
	}),

	// Conversations
	http.get('/api/projects/:projectId/conversations', ({ params }) => {
		const projectId = parseInt(params.projectId as string);
		const projectConversations = conversations.filter(c => c.project_id === projectId);
		return HttpResponse.json({
			conversations: projectConversations.map(c => ({
				...c,
				message_count: messages.filter(m => m.conversation_id === c.id).length
			}))
		});
	}),

	http.get('/api/conversations/:id', ({ params }) => {
		const id = parseInt(params.id as string);
		const conversation = conversations.find(c => c.id === id);
		if (!conversation) {
			return new HttpResponse(null, { status: 404 });
		}
		return HttpResponse.json(conversation);
	}),

	http.post('/api/conversations/create', async ({ request }) => {
		const body: any = await request.json();
		const conversation = {
			id: nextConversationId++,
			project_id: body.project_id,
			title: body.title || 'New Chat',
			message_count: 0,
			created_at: new Date().toISOString(),
			updated_at: new Date().toISOString()
		};
		conversations.push(conversation);
		return HttpResponse.json(conversation);
	}),

	http.put('/api/conversations/:id', async ({ params, request }) => {
		const id = parseInt(params.id as string);
		const body: any = await request.json();
		const conversationIndex = conversations.findIndex(c => c.id === id);
		if (conversationIndex === -1) {
			return new HttpResponse(null, { status: 404 });
		}
		conversations[conversationIndex] = {
			...conversations[conversationIndex],
			...body,
			updated_at: new Date().toISOString()
		};
		return HttpResponse.json(conversations[conversationIndex]);
	}),

	http.delete('/api/conversations/:id', ({ params }) => {
		const id = parseInt(params.id as string);
		const conversationIndex = conversations.findIndex(c => c.id === id);
		if (conversationIndex === -1) {
			return new HttpResponse(null, { status: 404 });
		}
		// Cascade delete messages
		messages = messages.filter(m => m.conversation_id !== id);
		conversations.splice(conversationIndex, 1);
		return new HttpResponse(null, { status: 204 });
	}),

	// Messages
	http.get('/api/conversations/:conversationId/messages', ({ params }) => {
		const conversationId = parseInt(params.conversationId as string);
		const conversationMessages = messages.filter(m => m.conversation_id === conversationId);
		return HttpResponse.json({
			messages: conversationMessages
		});
	}),

	http.get('/api/messages/:id', ({ params }) => {
		const id = parseInt(params.id as string);
		const message = messages.find(m => m.id === id);
		if (!message) {
			return new HttpResponse(null, { status: 404 });
		}
		return HttpResponse.json(message);
	}),

	http.post('/api/messages/create', async ({ request }) => {
		const body: any = await request.json();
		const message = {
			id: nextMessageId++,
			conversation_id: body.conversation_id,
			role: body.role || 'user',
			content: body.content,
			created_at: new Date().toISOString(),
			metadata: null,
			reaction: null
		};
		messages.push(message);
		return HttpResponse.json(message);
	}),

	http.put('/api/messages/:id/update', async ({ params, request }) => {
		const id = parseInt(params.id as string);
		const body: any = await request.json();
		const messageIndex = messages.findIndex(m => m.id === id);
		if (messageIndex === -1) {
			return new HttpResponse(null, { status: 404 });
		}
		messages[messageIndex] = { ...messages[messageIndex], ...body };
		return HttpResponse.json(messages[messageIndex]);
	}),

	http.put('/api/messages/:id/reaction', async ({ params, request }) => {
		const id = parseInt(params.id as string);
		const body: any = await request.json();
		const messageIndex = messages.findIndex(m => m.id === id);
		if (messageIndex === -1) {
			return new HttpResponse(null, { status: 404 });
		}
		messages[messageIndex] = {
			...messages[messageIndex],
			reaction: body.reaction
		};
		return HttpResponse.json(messages[messageIndex]);
	}),

	http.patch('/api/messages/:id/reaction', async ({ params, request }) => {
		const id = parseInt(params.id as string);
		const body: any = await request.json();
		const messageIndex = messages.findIndex(m => m.id === id);
		if (messageIndex === -1) {
			return new HttpResponse(null, { status: 404 });
		}
		messages[messageIndex] = {
			...messages[messageIndex],
			reaction: body.reaction
		};
		return HttpResponse.json(messages[messageIndex]);
	}),

	// Error scenarios for testing
	http.get('/api/test/400-error', () => {
		return HttpResponse.json(
			{ detail: 'Bad request validation error' },
			{ status: 400 }
		);
	}),

	http.get('/api/test/401-error', () => {
		return HttpResponse.json(
			{ detail: 'Unauthorized access' },
			{ status: 401 }
		);
	}),

	http.get('/api/test/403-csrf-error', () => {
		return HttpResponse.json(
			{ detail: 'CSRF token validation failed' },
			{ status: 403 }
		);
	}),

	http.get('/api/test/404-error', () => {
		return HttpResponse.json(
			{ detail: 'Resource not found' },
			{ status: 404 }
		);
	}),

	http.get('/api/test/500-error', () => {
		return HttpResponse.json(
			{ detail: 'Internal server error' },
			{ status: 500 }
		);
	})
];

/**
 * Reset mock data (for test isolation)
 */
export function resetMockData() {
	projects = [
		{ id: 1, name: 'Test Project', description: 'Test description', conversation_count: 5, created_at: '2025-01-01T10:00:00Z' },
		{ id: 2, name: 'Demo Project', description: '', conversation_count: 3, created_at: '2025-01-02T10:00:00Z' }
	];
	conversations = [
		{ id: 1, project_id: 1, title: 'Chat 1', message_count: 10, created_at: '2025-01-01T10:00:00Z', updated_at: '2025-01-01T11:00:00Z' },
		{ id: 2, project_id: 1, title: 'Chat 2', message_count: 5, created_at: '2025-01-01T12:00:00Z', updated_at: '2025-01-01T13:00:00Z' }
	];
	messages = [
		{ id: 1, conversation_id: 1, role: 'user', content: 'Hello', created_at: '2025-01-01T10:00:00Z' },
		{ id: 2, conversation_id: 1, role: 'assistant', content: 'Hi there!', created_at: '2025-01-01T10:00:05Z' }
	];
	nextProjectId = 3;
	nextConversationId = 3;
	nextMessageId = 3;
}
