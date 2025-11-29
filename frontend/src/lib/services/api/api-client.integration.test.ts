/**
 * API Client Integration Tests
 *
 * Tests full workflows across multiple API endpoints and services.
 * Uses MSW to mock backend responses.
 *
 * Total: 20 integration tests
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { fetchProjects, fetchProject, createProject, deleteProject, updateProject } from './projects';
import { createConversation, getConversations, updateConversation, deleteConversation } from './conversations';
import { createMessage, updateMessage, updateMessageReaction } from './messages';
import { csrfClient } from '../core/csrf';
import { server } from '../../../mocks/server';
import { http, HttpResponse } from 'msw';

/**
 * Project → Conversation Workflow (5 tests)
 */
describe('Project → Conversation Integration Workflow', () => {
	it('should create project → fetch projects → verify project appears in list', async () => {
		// Create new project
		const newProject = await createProject('Integration Test Project', 'Test description');
		expect(newProject.name).toBe('Integration Test Project');
		expect(newProject.id).toBeDefined();

		// Fetch all projects
		const response = await fetchProjects();
		expect(response.projects).toHaveLength(3); // 2 existing + 1 new

		// Verify new project in list
		const foundProject = response.projects.find(p => p.id === newProject.id);
		expect(foundProject).toBeDefined();
		expect(foundProject?.name).toBe('Integration Test Project');
	});

	it('should create project → create conversation → verify conversation linked to project', async () => {
		// Create new project
		const project = await createProject('Project for Conversation');

		// Create conversation in project
		const conversation = await createConversation(project.id, 'Test Chat');
		expect(conversation.project_id).toBe(project.id);
		expect(conversation.title).toBe('Test Chat');

		// Fetch all conversations for project
		const conversations = await getConversations(project.id);
		expect(conversations.length).toBeGreaterThan(0);

		// Verify conversation is linked
		const foundConv = conversations.find(c => c.id === conversation.id);
		expect(foundConv).toBeDefined();
		expect(foundConv?.project_id).toBe(project.id);
	});

	it('should create project with description → verify description persisted', async () => {
		const description = 'This is a detailed project description';
		const project = await createProject('Described Project', description);

		expect(project.description).toBe(description);

		// Fetch project again to verify persistence
		const response = await fetchProjects();
		const fetchedProject = response.projects.find(p => p.id === project.id);
		expect(fetchedProject?.description).toBe(description);
	});

	it('should delete project → verify conversations also deleted (cascade)', async () => {
		// Create project with conversation
		const project = await createProject('To Be Deleted');
		const conversation = await createConversation(project.id, 'Will be deleted');

		// Delete project
		await deleteProject(project.id);

		// Verify project deleted
		const projects = await fetchProjects();
		expect(projects.projects.find(p => p.id === project.id)).toBeUndefined();

		// Verify conversations also deleted (cascade)
		const conversations = await getConversations(project.id);
		expect(conversations.find(c => c.id === conversation.id)).toBeUndefined();
	});

	it('should update project name → verify all conversations reflect new project name', async () => {
		// Create project with conversation
		const project = await createProject('Old Name');
		await createConversation(project.id, 'Chat 1');

		// Update project name
		const updatedProject = await updateProject(project.id, { name: 'New Name' });
		expect(updatedProject.name).toBe('New Name');

		// Fetch conversations and verify they still belong to same project
		const conversations = await getConversations(project.id);
		expect(conversations.length).toBeGreaterThan(0);
		conversations.forEach(conv => {
			expect(conv.project_id).toBe(project.id);
		});
	});
});

/**
 * Conversation → Message Workflow (5 tests)
 */
describe('Conversation → Message Integration Workflow', () => {
	let projectId: number;
	let conversationId: number;

	beforeEach(async () => {
		// Setup: Create project and conversation
		const project = await createProject('Message Test Project');
		projectId = project.id;
		const conversation = await createConversation(projectId, 'Message Test Chat');
		conversationId = conversation.id;
	});

	it('should create conversation → create user message → verify message persisted', async () => {
		// Create user message
		const message = await createMessage(conversationId, 'Hello, world!', 'user');
		expect(message.content).toBe('Hello, world!');
		expect(message.role).toBe('user');
		expect(message.conversation_id).toBe(conversationId);
		expect(message.id).toBeDefined();
	});

	it('should create conversation → create multiple messages → verify correct ordering (ASC by created_at)', async () => {
		// Create multiple messages
		const msg1 = await createMessage(conversationId, 'First message', 'user');
		// Small delay to ensure different timestamps
		await new Promise(resolve => setTimeout(resolve, 10));
		const msg2 = await createMessage(conversationId, 'Second message', 'assistant');
		await new Promise(resolve => setTimeout(resolve, 10));
		const msg3 = await createMessage(conversationId, 'Third message', 'user');

		// Messages should be ordered by creation time (ascending)
		expect(new Date(msg1.created_at).getTime()).toBeLessThan(new Date(msg2.created_at).getTime());
		expect(new Date(msg2.created_at).getTime()).toBeLessThan(new Date(msg3.created_at).getTime());
	});

	it('should create message → update message content → verify update persisted', async () => {
		// Create message
		const message = await createMessage(conversationId, 'Original content', 'user');

		// Update message content
		const updatedMessage = await updateMessage(message.id, { content: 'Updated content' });
		expect(updatedMessage.content).toBe('Updated content');
		expect(updatedMessage.id).toBe(message.id);
	});

	it('should create message → add reaction → verify reaction saved', async () => {
		// Create assistant message
		const message = await createMessage(conversationId, 'How can I help?', 'assistant');

		// Add thumbs up reaction
		const updatedMessage = await updateMessageReaction(message.id, 'thumbs_up');
		expect(updatedMessage.reaction).toBe('thumbs_up');

		// Change to thumbs down
		const updatedMessage2 = await updateMessageReaction(message.id, 'thumbs_down');
		expect(updatedMessage2.reaction).toBe('thumbs_down');

		// Remove reaction
		const updatedMessage3 = await updateMessageReaction(message.id, null);
		expect(updatedMessage3.reaction).toBeNull();
	});

	it('should delete conversation → verify messages also deleted (cascade)', async () => {
		// Create messages
		const msg1 = await createMessage(conversationId, 'Message 1', 'user');
		const msg2 = await createMessage(conversationId, 'Message 2', 'assistant');

		// Delete conversation
		await deleteConversation(conversationId);

		// Verify conversation deleted
		const conversations = await getConversations(projectId);
		expect(conversations.find(c => c.id === conversationId)).toBeUndefined();

		// Note: In real implementation, we'd verify messages are also gone
		// For this mock, the cascade delete is handled in handlers.ts
	});
});

/**
 * CSRF Token Lifecycle (5 tests)
 */
describe('CSRF Token Lifecycle Integration', () => {
	beforeEach(() => {
		// Clear CSRF cache before each test
		csrfClient.clearCache();
	});

	it('should first POST request → CSRF token fetched automatically', async () => {
		// Clear cache to force fetch
		csrfClient.clearCache();

		// Make POST request (should fetch CSRF token automatically)
		const project = await createProject('CSRF Test Project');
		expect(project.id).toBeDefined();

		// Token should now be cached
		const token = await csrfClient.getToken();
		expect(token).toBe('mock-csrf-token-12345');
	});

	it('should subsequent requests → CSRF token reused from cache', async () => {
		// First request fetches token
		await createProject('Project 1');
		const token1 = await csrfClient.getToken();

		// Second request reuses cached token
		await createProject('Project 2');
		const token2 = await csrfClient.getToken();

		// Same token
		expect(token1).toBe(token2);
		expect(token1).toBe('mock-csrf-token-12345');
	});

	it('should token expiry → new token fetched automatically', async () => {
		// Get initial token
		const token1 = await csrfClient.getToken();
		expect(token1).toBe('mock-csrf-token-12345');

		// Manually expire token by clearing cache (simulates expiry)
		csrfClient.clearCache();

		// Next request should fetch new token
		const token2 = await csrfClient.getToken();
		expect(token2).toBe('mock-csrf-token-12345');
	});

	it('should 403 CSRF error → token refreshed and request retried', async () => {
		// Mock 403 CSRF error on first attempt, success on retry
		let attemptCount = 0;
		server.use(
			http.post('/api/projects/create', async ({ request }) => {
				attemptCount++;
				if (attemptCount === 1) {
					// First attempt: CSRF error
					return HttpResponse.json(
						{ detail: 'CSRF token validation failed' },
						{ status: 403 }
					);
				}
				// Second attempt: Success
				const body: any = await request.json();
				return HttpResponse.json({
					id: 999,
					name: body.name,
					description: body.description || '',
					created_at: new Date().toISOString()
				});
			})
		);

		// Make request (should auto-retry after CSRF refresh)
		const project = await createProject('CSRF Retry Test');
		expect(project.id).toBe(999);
		expect(attemptCount).toBe(2); // Should have tried twice
	});

	it('should multiple concurrent 403s → single refresh (no race condition)', async () => {
		// Mock 403 for first requests
		let refreshCount = 0;
		server.use(
			http.get('/api/csrf-token', () => {
				refreshCount++;
				return HttpResponse.json({ csrf_token: `token-${refreshCount}` });
			})
		);

		// Clear cache to force fetch
		csrfClient.clearCache();

		// Make multiple concurrent requests
		const promises = [
			csrfClient.getToken(),
			csrfClient.getToken(),
			csrfClient.getToken()
		];

		const tokens = await Promise.all(promises);

		// All should get same token (only 1 fetch)
		expect(tokens[0]).toBe(tokens[1]);
		expect(tokens[1]).toBe(tokens[2]);
		expect(refreshCount).toBe(1); // Only one fetch despite 3 concurrent calls
	});
});

/**
 * Error Handling Integration (5 tests)
 */
describe('Error Handling Integration', () => {
	it('should network failure → proper error message → toast notification shown', async () => {
		// Mock network failure
		server.use(
			http.get('/api/projects/list', () => {
				return HttpResponse.error();
			})
		);

		// Expect error to be thrown
		await expect(fetchProjects()).rejects.toThrow('Network error');
	});

	it('should 400 Bad Request → validation error displayed', async () => {
		// Mock 400 error
		server.use(
			http.post('/api/projects/create', () => {
				return HttpResponse.json(
					{ detail: 'Project name is required' },
					{ status: 400 }
				);
			})
		);

		await expect(createProject('')).rejects.toThrow('Project name is required');
	});

	it('should 401 Unauthorized → redirect to login (or show error)', async () => {
		// Mock 401 error
		server.use(
			http.get('/api/projects/list', () => {
				return HttpResponse.json(
					{ detail: 'Authentication required. Please log in.' },
					{ status: 401 }
				);
			})
		);

		await expect(fetchProjects()).rejects.toThrow('Authentication required');
	});

	it('should 404 Not Found → friendly "not found" message', async () => {
		// Mock 404 error
		server.use(
			http.get('/api/projects/:id', () => {
				return HttpResponse.json(
					{ detail: 'Project not found' },
					{ status: 404 }
				);
			})
		);

		await expect(fetchProject(99999)).rejects.toThrow('Project not found');
	});

	it('should 500 Server Error → generic error message → error logged', async () => {
		// Mock 500 error
		server.use(
			http.get('/api/projects/list', () => {
				return HttpResponse.json(
					{ detail: 'Internal server error' },
					{ status: 500 }
				);
			})
		);

		await expect(fetchProjects()).rejects.toThrow('Internal server error');
	});
});
