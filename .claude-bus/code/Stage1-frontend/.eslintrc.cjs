/**
 * ESLint configuration for GPT-OSS frontend
 *
 * Purpose: Enforce TypeScript and Svelte best practices
 *
 * Key rules:
 * - TypeScript strict mode (no implicit any, null checks)
 * - Svelte best practices (no unused $: statements, proper component structure)
 * - Accessibility checks (alt text, semantic HTML)
 */
module.exports = {
	root: true,
	extends: [
		'eslint:recommended',
		'plugin:@typescript-eslint/recommended',
		'plugin:svelte/recommended'
	],
	parser: '@typescript-eslint/parser',
	plugins: ['@typescript-eslint'],
	parserOptions: {
		sourceType: 'module',
		ecmaVersion: 2020,
		extraFileExtensions: ['.svelte']
	},
	env: {
		browser: true,
		es2017: true,
		node: true
	},
	overrides: [
		{
			files: ['*.svelte'],
			parser: 'svelte-eslint-parser',
			parserOptions: {
				parser: '@typescript-eslint/parser'
			}
		}
	],
	rules: {
		// TypeScript rules
		'@typescript-eslint/no-explicit-any': 'error', // Prevent 'any' type
		'@typescript-eslint/explicit-function-return-type': 'off', // Allow type inference
		'@typescript-eslint/no-unused-vars': [
			'error',
			{ argsIgnorePattern: '^_', varsIgnorePattern: '^_' }
		],

		// General rules
		'no-console': ['warn', { allow: ['warn', 'error'] }], // Warn on console.log
		'no-debugger': 'error' // Prevent debugger statements
	}
};
