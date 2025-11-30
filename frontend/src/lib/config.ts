/**
 * Environment configuration for GPT-OSS frontend
 *
 * Purpose: Centralized configuration for API URLs and app settings
 *
 * Configuration loading strategy:
 * - Development: Use localhost URLs (.env.development)
 * - Production: Use environment variables (.env.production or deployment env vars)
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
 * WebSocket base URL for real-time communication
 *
 * Default: ws://localhost:8000 (development)
 * Production: Set via VITE_WS_URL environment variable
 */
export const WS_BASE_URL: string =
	import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

/**
 * Analytics configuration
 *
 * Enable/disable analytics tracking
 */
export const ENABLE_ANALYTICS: boolean =
	import.meta.env.VITE_ENABLE_ANALYTICS === 'true';

/**
 * Debug mode configuration
 *
 * Enable/disable debug logging
 */
export const ENABLE_DEBUG: boolean =
	import.meta.env.VITE_ENABLE_DEBUG === 'true' || import.meta.env.DEV;

/**
 * API endpoints configuration
 *
 * Centralized endpoint paths for easy maintenance
 *
 * NOTE: Vite dev proxy handles /api/* routes, so we use relative paths
 * In production, these will be prefixed with API_BASE_URL via fetch wrapper
 */
export const API_ENDPOINTS = {
	// Project management
	projects: {
		create: '/api/projects/create',
		list: '/api/projects/list',
		default: '/api/projects/default',
		get: (id: number) => `/api/projects/${id}`,
		delete: (id: number) => `/api/projects/${id}`,
		stats: (id: number) => `/api/projects/${id}/stats`,
		conversations: (id: number) => `/api/projects/${id}/conversations`
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
		stream: '/api/chat/stream',
		cancel: (sessionId: string) => `/api/chat/cancel/${sessionId}`
	},

	messages: {
		get: (conversationId: number) => `/api/messages/${conversationId}`,
		reaction: (messageId: number) => `/api/messages/${messageId}/reaction`,
		regenerate: (messageId: number) => `/api/messages/${messageId}/regenerate`
	},

	// Health check
	health: '/api/health',

	// CSRF token (for future security enhancement)
	csrf: '/api/csrf-token',

	// Document management (Stage 2)
	documents: {
		upload: (projectId: number) => `/api/projects/${projectId}/documents/upload`,
		list: (projectId: number) => `/api/projects/${projectId}/documents`,
		get: (documentId: number) => `/api/documents/${documentId}`,
		download: (documentId: number) => `/api/documents/${documentId}/download`,
		delete: (documentId: number) => `/api/documents/${documentId}`
	}
} as const;

/**
 * Application configuration constants
 *
 * UI behavior constants referenced from task requirements
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

	// Stage 2 features (enabled)
	documentUpload: true, // Stage 2 implemented

	// Future stage features (disabled)
	knowledgeGraph: false,
	authentication: false
} as const;

/**
 * Application metadata
 */
export const APP_METADATA = {
	name: 'GPT-OSS Assistant',
	version: '1.0.0',
	description: 'Local AI Knowledge Assistant'
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

/**
 * Default export: consolidated configuration object
 *
 * Provides clean import pattern:
 * import config from '$lib/config';
 * config.api.baseUrl
 * config.features.analytics
 */
export default {
	api: {
		baseUrl: API_BASE_URL,
		wsUrl: WS_BASE_URL,
		endpoints: API_ENDPOINTS
	},
	features: {
		analytics: ENABLE_ANALYTICS,
		debug: ENABLE_DEBUG,
		...FEATURES
	},
	app: APP_CONFIG,
	metadata: APP_METADATA,
	isDevelopment,
	isProduction
} as const;
