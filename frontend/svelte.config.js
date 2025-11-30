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

		// Alias configuration for cleaner imports
		// Note: kit.files.* options are deprecated in SvelteKit 2.x
		// Using default file locations instead (src/routes, src/lib, static, etc.)
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
