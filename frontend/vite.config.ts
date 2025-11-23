import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

/**
 * Vite configuration for GPT-OSS frontend
 *
 * Purpose: Configure Vite build tool, dev server, and testing
 *
 * Key features:
 * - SvelteKit plugin integration
 * - Vitest for unit testing
 * - Dev server on port 3000
 * - API proxy to backend (avoid CORS in development)
 */
export default defineConfig({
	// SvelteKit plugin enables HMR and SSR
	plugins: [sveltekit()],

	// Vitest test configuration
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
		globals: true,
		environment: 'jsdom',
		coverage: {
			provider: 'v8',
			reporter: ['text', 'html'],
			lines: 70, // Minimum 70% line coverage
			functions: 70,
			branches: 70,
			statements: 70
		}
	},

	// Dev server configuration
	server: {
		port: 5173,
		host: true, // Listen on all network interfaces (required for Docker)
		strictPort: true,

		/**
		 * API proxy configuration
		 *
		 * WHY proxy is essential for development:
		 * - Frontend runs on http://localhost:5173 (Vite dev server)
		 * - Backend runs on http://localhost:8000 (FastAPI server)
		 * - Without proxy: Browser blocks requests due to CORS (different ports = different origins)
		 * - With proxy: Vite forwards /api/* requests to backend, same-origin to browser
		 *
		 * HOW it works:
		 * 1. Component calls: fetch('/api/projects/list')
		 * 2. Browser sends to: http://localhost:5173/api/projects/list (same origin, no CORS)
		 * 3. Vite proxy forwards to: http://backend:8000/api/projects/list (in Docker)
		 * 4. Backend responds to Vite, Vite forwards to browser
		 *
		 * WHY these specific options:
		 * - target: Backend server URL (env var VITE_API_URL or default)
		 * - changeOrigin: true = Sets Host header to target (required for virtual hosts)
		 * - secure: false = Allows self-signed SSL certs in development (http → http, not needed but safe)
		 * - rewrite NOT used: Keep /api prefix (backend routes expect /api/*)
		 *
		 * Docker note:
		 * - In Docker, use service name 'backend' instead of 'localhost'
		 * - Set VITE_BACKEND_URL env var in docker-compose.yml
		 *
		 * Production note:
		 * - In production, frontend and backend share same domain (nginx reverse proxy)
		 * - This proxy only runs in development (vite dev)
		 * - Build output (vite build) is static files, proxy not included
		 *
		 * Example request flow:
		 * fetch('/api/projects/list') → http://backend:8000/api/projects/list → Backend
		 */
		proxy: {
			'/api': {
				target: process.env.VITE_BACKEND_URL || 'http://localhost:8000',
				changeOrigin: true,
				secure: false
			}
		}
	},

	// Build optimization
	build: {
		// Target modern browsers for smaller bundle size
		target: 'esnext'
	}
});
