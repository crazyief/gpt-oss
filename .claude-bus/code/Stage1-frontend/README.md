# GPT-OSS Frontend

SvelteKit frontend for GPT-OSS Local AI Knowledge Assistant.

## Tech Stack

- **SvelteKit**: Full-stack framework with SSR and routing
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first styling
- **Vite**: Build tool and dev server
- **Vitest**: Unit testing framework
- **marked + prism.js + DOMPurify**: Markdown rendering with syntax highlighting and XSS prevention

## Development

### Prerequisites

- Node.js 18+ (20 recommended)
- npm or pnpm

### Setup

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:3000)
npm run dev

# Type checking
npm run check

# Linting
npm run lint

# Format code
npm run format
```

### Environment Variables

Copy `.env.example` to `.env.local` and configure:

```bash
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── lib/
│   ├── components/    # Reusable Svelte components
│   ├── stores/        # Svelte stores (state management)
│   ├── api/           # API client functions
│   ├── types/         # TypeScript type definitions
│   ├── utils/         # Utility functions
│   └── config.ts      # Environment configuration
├── routes/
│   ├── +layout.svelte # Root layout
│   ├── +page.svelte   # Project list page
│   └── project/[id]/  # Chat interface (to be implemented)
├── app.html           # HTML template
└── app.css            # Global styles (TailwindCSS)
```

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run check` - Type check
- `npm run lint` - Lint code
- `npm run format` - Format code with Prettier

## Testing

```bash
# Run unit tests
npm run test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

Minimum test coverage: 70% (enforced in vite.config.ts)

## Code Quality Standards

From `.claude-bus/config/Stage1-standards.json`:

- **Max file length**: 400 lines (excluding comments)
- **Max function length**: 50 lines
- **Max nesting depth**: 3 levels
- **Min comment coverage**: 40%
- **TypeScript strict mode**: Enabled
- **Test coverage minimum**: 70%

## API Integration

The frontend communicates with the FastAPI backend running on `http://localhost:8000`.

API proxy is configured in `vite.config.ts` to avoid CORS issues during development:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

## Stage 1 Implementation Tasks

- [x] **Task 004**: SvelteKit setup with TailwindCSS
- [ ] **Task 005**: Sidebar with chat history
- [ ] **Task 006**: Chat interface with SSE streaming

## Security

- **XSS Prevention**: All LLM-generated content sanitized with DOMPurify before rendering
- **Input Validation**: Max message length enforced (10,000 characters)
- **Type Safety**: TypeScript strict mode prevents common bugs

## Performance

- **Code Splitting**: Vendor chunks separated for optimal caching
- **Bundle Size Target**: < 200KB (excluding vendor chunks)
- **Lazy Loading**: Components loaded on demand
- **Debouncing**: Search inputs debounced (300ms)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

Internal project - not for public distribution.
