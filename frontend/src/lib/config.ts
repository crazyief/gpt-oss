/**
 * Environment configuration for GPT-OSS frontend
 *
 * Purpose: Centralized configuration for API URLs and app settings
 *
 * Configuration loading strategy:
 * - Development: Use localhost URLs
 * - Production: Use environment variables (VITE_API_URL)
 *
 * Security notes:
 * - All Vite env vars must be prefixed with VITE_ to be exposed to client
 * - Never commit sensitive data to this file
 * - Use .env.local for local overrides (gitignored)
 */

/**
 * API base URL for backend communication
 *
 * Default: http://localhost:8000 (development)
 * Production: Set via VITE_API_URL environment variable
 */
export const API_BASE_URL: string =
	import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * API endpoints configuration
 *
 * Centralized endpoint paths for easy maintenance
 *
 * WHY use nested object structure instead of flat constants:
 * - Namespacing: Groups related endpoints (projects.*, conversations.*, etc.)
 * - Discoverability: IDE autocomplete shows all endpoints for a resource
 * - Scalability: Easy to add new resources without naming collisions
 * - Readability: import { API_ENDPOINTS } from '$lib/config'; API_ENDPOINTS.projects.create
 *
 * WHY use functions for parameterized endpoints:
 * - Type safety: TypeScript enforces parameter types (number for IDs, string for session IDs)
 * - Runtime validation: Functions can validate/sanitize IDs before string interpolation
 * - Consistency: Single pattern for all parameterized endpoints
 * - Prevents typos: get(123) vs. manual string concat `/api/projects/${id}` in every component
 *
 * WHY 'as const' assertion:
 * - Literal types: TypeScript infers exact string values, not generic 'string'
 * - Immutability: Prevents accidental modification (API_ENDPOINTS.health = '/new-path')
 * - Better autocomplete: IDE knows exact endpoint strings
 * - Type narrowing: Enables exhaustive switch/case checks
 *
 * Design decision: Keep /api prefix in paths
 * - WHY: Works with Vite proxy (proxy forwards /api/* to backend)
 * - Alternative considered: Strip /api prefix, add in fetch wrapper
 * - Chosen approach: Explicit paths match backend routes exactly (less magic)
 */
export const API_ENDPOINTS = {
	// Project management
	projects: {
		create: '/api/projects/create',
		list: '/api/projects/list',
		get: (id: number) => `/api/projects/${id}`,
		delete: (id: number) => `/api/projects/${id}`
	},

	// Conversation management
	conversations: {
		create: '/api/conversations/create',
		list: '/api/conversations/list',
		get: (id: number) => `/api/conversations/${id}`,
		update: (id: number) => `/api/conversations/${id}`,
		delete: (id: number) => `/api/conversations/${id}`,
		search: '/api/conversations/search'
	},

	// Chat and messages
	chat: {
		stream: '/api/chat/stream', // SSE endpoint
		cancel: (sessionId: string) => `/api/chat/cancel/${sessionId}`
	},

	messages: {
		get: (conversationId: number) => `/api/messages/${conversationId}`,
		reaction: (messageId: number) => `/api/messages/${messageId}/reaction`,
		regenerate: (messageId: number) => `/api/messages/${messageId}/regenerate`
	},

	// Health check
	health: '/api/health'
} as const;

/**
 * Application configuration constants
 *
 * UI behavior constants referenced from task requirements
 *
 * WHY centralize magic numbers in APP_CONFIG:
 * - Single source of truth: Change animation speed once, affects all components
 * - Consistency: All debounces, timeouts, sizes use same values across app
 * - Testability: Easy to override in tests (mock APP_CONFIG with faster timeouts)
 * - Documentation: Values are named and explained (300ms vs. mysterious number in component)
 * - Type safety: 'as const' prevents accidental modification
 *
 * WHY specific values chosen:
 * - sidebar.toggleAnimationMs: 300ms = smooth but not sluggish (Material Design guideline)
 * - sidebar.searchDebounceMs: 300ms = balance between responsiveness and API call reduction
 * - chat.maxMessageLength: 10000 chars = reasonable limit for LLM context (GPT-4 ~3000 tokens)
 * - sse.maxRetries: 5 = enough for transient network issues, not infinite (prevents runaway reconnects)
 * - sse.retryDelays: Exponential backoff prevents thundering herd on server restart
 */
export const APP_CONFIG = {
	// Sidebar configuration (from Stage1-task-005)
	sidebar: {
		width: '260px',
		toggleAnimationMs: 300,
		searchDebounceMs: 300
	},

	// Chat input configuration (from Stage1-task-006)
	chat: {
		maxMessageLength: 10000,
		inputMaxHeight: '120px', // 5 lines
		autoScrollThreshold: 100 // px from bottom
	},

	// SSE configuration (from Stage1-task-006)
	sse: {
		maxRetries: 5,
		retryDelays: [1000, 2000, 4000, 8000, 16000], // Exponential backoff (ms)
		keepAliveIntervalMs: 30000 // Server keep-alive interval
	},

	// Pagination defaults (from API contracts)
	pagination: {
		defaultLimit: 50,
		maxLimit: 100
	}
} as const;

/**
 * Feature flags
 *
 * Enable/disable features for development and testing
 */
export const FEATURES = {
	// Stage 1 features (enabled)
	chatStreaming: true,
	conversationManagement: true,
	projectManagement: true,

	// Future stage features (disabled for Stage 1)
	documentUpload: false,
	knowledgeGraph: false,
	authentication: false
} as const;

/**
 * Development mode check
 *
 * Returns true if running in Vite development mode
 */
export const isDevelopment = (): boolean => {
	return import.meta.env.DEV;
};

/**
 * Production mode check
 *
 * Returns true if running in production build
 */
export const isProduction = (): boolean => {
	return import.meta.env.PROD;
};
