import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/**
 * SvelteKit configuration for GPT-OSS frontend
 *
 * Purpose: Configure SvelteKit build, routing, and preprocessing
 *
 * Key settings:
 * - adapter-auto: Auto-detects deployment target (Node.js, Vercel, etc.)
 * - vitePreprocess: Enables TypeScript and PostCSS processing
 * - kit.files: Maps source directories for routes, app structure, assets
 */
const config = {
	// Compile Svelte components with preprocessing for TypeScript and CSS
	preprocess: vitePreprocess(),

	kit: {
		// Adapter for deployment (auto-detects environment)
		adapter: adapter(),

		// File structure configuration
		files: {
			// SvelteKit app structure
			assets: 'static',
			hooks: {
				client: 'src/hooks.client',
				server: 'src/hooks.server'
			},
			lib: 'src/lib',
			params: 'src/params',
			routes: 'src/routes',
			appTemplate: 'src/app.html'
		},

		// Alias configuration for cleaner imports
		alias: {
			$lib: 'src/lib',
			$components: 'src/lib/components',
			$stores: 'src/lib/stores',
			$types: 'src/lib/types',
			$utils: 'src/lib/utils',
			$api: 'src/lib/api'
		}
	}
};

export default config;
