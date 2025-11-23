# Frontend Production Dockerfile
# Multi-stage build for optimized production deployment

# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production
FROM node:18-alpine

WORKDIR /app

# Copy built files from builder
COPY --from=builder /app/.svelte-kit /app/.svelte-kit
COPY --from=builder /app/package.json /app/package.json
COPY --from=builder /app/package-lock.json /app/package-lock.json

# Install only production dependencies
RUN npm ci --only=production

# Expose port
EXPOSE 3000

# Set environment to production
ENV NODE_ENV=production

# Start the application (SvelteKit adapter-node)
CMD ["node", ".svelte-kit/output/server/index.js"]
