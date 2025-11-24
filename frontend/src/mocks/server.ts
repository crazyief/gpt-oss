/**
 * MSW Server Setup (Node.js environment)
 *
 * Used in Vitest test environment to intercept API requests.
 */

import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
