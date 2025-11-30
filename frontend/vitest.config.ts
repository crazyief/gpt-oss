import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import path from 'path';

export default defineConfig({
	plugins: [svelte({ hot: !process.env.VITEST })],
	test: {
		globals: true,
		environment: 'jsdom',
		include: ['src/**/*.test.ts', 'src/**/*.integration.test.ts'],
		setupFiles: ['./src/mocks/setup.ts'],
		coverage: {
			provider: 'v8',
			reporter: ['text', 'json', 'html'],
			exclude: [
				'node_modules/',
				'src/**/*.d.ts',
				'src/**/*.config.*',
				'src/routes/**', // E2E tested separately
				'.svelte-kit/',
				'src/mocks/**' // Exclude mock files
			],
			thresholds: {
				lines: 70,
				functions: 70,
				branches: 70,
				statements: 70
			}
		}
	},
	resolve: {
		alias: {
			$lib: path.resolve(__dirname, './src/lib'),
			// Mock $app modules for testing (SvelteKit runtime not available in tests)
			'$app/environment': path.resolve(__dirname, './src/mocks/app-environment.ts'),
			'$app/navigation': path.resolve(__dirname, './src/mocks/app-navigation.ts'),
			'$app/stores': path.resolve(__dirname, './src/mocks/app-stores.ts')
		}
	}
});
