/**
 * TailwindCSS configuration for GPT-OSS frontend
 *
 * Purpose: Configure Tailwind with ChatGPT-inspired design system
 *
 * Design decisions:
 * - Light mode focus (dark mode in future stage)
 * - ChatGPT-inspired color palette (grays, accent colors)
 * - Responsive breakpoints for mobile-first design
 * - Custom animations for smooth transitions
 */
export default {
	// Content sources for Tailwind class scanning
	content: ['./src/**/*.{html,js,svelte,ts}'],

	theme: {
		extend: {
			/**
			 * ChatGPT-inspired color palette
			 *
			 * Color strategy:
			 * - neutral: Main UI backgrounds and borders
			 * - primary: Accent color for interactive elements
			 * - user: User message background
			 * - assistant: Assistant message background
			 */
			colors: {
				// Neutral grays (ChatGPT UI)
				neutral: {
					50: '#f9fafb',   // Lightest background
					100: '#f3f4f6',  // Sidebar background
					200: '#e5e7eb',  // Border light
					300: '#d1d5db',  // Border medium
					400: '#9ca3af',  // Text muted
					500: '#6b7280',  // Text secondary
					600: '#4b5563',  // Text primary
					700: '#374151',  // Text emphasis
					800: '#1f2937',  // Dark background
					900: '#111827'   // Darkest
				},

				// Primary accent (teal/green, ChatGPT style)
				primary: {
					50: '#ecfdf5',
					100: '#d1fae5',
					200: '#a7f3d0',
					300: '#6ee7b7',
					400: '#34d399',
					500: '#10b981',  // Main accent color
					600: '#059669',
					700: '#047857',
					800: '#065f46',
					900: '#064e3b'
				},

				// User message background (light blue)
				user: {
					bg: '#eff6ff',
					border: '#dbeafe'
				},

				// Assistant message background (light gray)
				assistant: {
					bg: '#f9fafb',
					border: '#e5e7eb'
				}
			},

			/**
			 * Typography scale
			 *
			 * Font sizes optimized for readability in chat interface
			 */
			fontSize: {
				'xs': ['0.75rem', { lineHeight: '1rem' }],
				'sm': ['0.875rem', { lineHeight: '1.25rem' }],
				'base': ['1rem', { lineHeight: '1.5rem' }],
				'lg': ['1.125rem', { lineHeight: '1.75rem' }],
				'xl': ['1.25rem', { lineHeight: '1.75rem' }]
			},

			/**
			 * Spacing scale
			 *
			 * Custom spacing values for consistent UI padding/margins
			 */
			spacing: {
				'sidebar': '260px',  // Sidebar width (from task requirements)
				'chat-input': '120px' // Max chat input height (5 lines)
			},

			/**
			 * Animation transitions
			 *
			 * Smooth animations for sidebar toggle, message appearance
			 */
			transitionProperty: {
				'width': 'width',
				'spacing': 'margin, padding'
			},

			transitionDuration: {
				'300': '300ms' // Sidebar toggle animation (from task requirements)
			},

			/**
			 * Custom animations
			 *
			 * Animations for loading states, message streaming
			 */
			keyframes: {
				// Typing indicator animation (three dots bouncing)
				'typing': {
					'0%, 60%, 100%': { transform: 'translateY(0)' },
					'30%': { transform: 'translateY(-10px)' }
				},

				// Fade in animation for new messages
				'fadeIn': {
					'0%': { opacity: '0', transform: 'translateY(10px)' },
					'100%': { opacity: '1', transform: 'translateY(0)' }
				},

				// Slide in from left (sidebar on mobile)
				'slideInLeft': {
					'0%': { transform: 'translateX(-100%)' },
					'100%': { transform: 'translateX(0)' }
				}
			},

			animation: {
				'typing': 'typing 1.4s infinite ease-in-out',
				'fadeIn': 'fadeIn 0.3s ease-out',
				'slideInLeft': 'slideInLeft 0.3s ease-out'
			},

			/**
			 * Box shadow for elevation
			 *
			 * Subtle shadows for cards, modals, dropdowns
			 */
			boxShadow: {
				'chat': '0 2px 8px rgba(0, 0, 0, 0.05)',
				'sidebar': '2px 0 8px rgba(0, 0, 0, 0.05)',
				'modal': '0 10px 40px rgba(0, 0, 0, 0.15)'
			}
		}
	},

	plugins: [
		// Add @tailwindcss/forms plugin for better form styling (future)
		// Add @tailwindcss/typography plugin for markdown rendering (future)
	]
};
