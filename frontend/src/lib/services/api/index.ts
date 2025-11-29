/**
 * API client barrel exports
 *
 * Re-exports all API client modules for convenient imports.
 *
 * Usage:
 * ```typescript
 * // Import specific modules
 * import { projects, conversations, messages } from '$lib/services/api';
 * const projectList = await projects.fetchProjects();
 * const convList = await conversations.getConversations(projectId);
 * const msg = await messages.getMessage(messageId);
 *
 * // Or import base utilities
 * import { apiRequest } from '$lib/services/api';
 *
 * // Or import CSRF utilities for manual token management
 * import { csrfClient } from '$lib/services/api';
 * ```
 */

// Export base utilities
export { apiRequest, type ApiRequestOptions } from './base';

// Export CSRF utilities (for manual token management if needed)
export { csrfClient } from '../core/csrf';

// Export all API modules
export * as projects from './projects';
export * as conversations from './conversations';
export * as messages from './messages';
export * as documents from './documents';
