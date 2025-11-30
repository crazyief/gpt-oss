/**
 * Unit tests for SSE message factory
 *
 * Tests: Message creation from SSE events
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { fetchCompleteMessage } from './message-factory';

describe('fetchCompleteMessage', () => {
	beforeEach(() => {
		vi.useFakeTimers();
		vi.setSystemTime(new Date('2025-11-30T10:00:00Z'));
	});

	afterEach(() => {
		vi.useRealTimers();
	});

	describe('message creation', () => {
		it('should create message with correct id', async () => {
			const message = await fetchCompleteMessage(123, 456, 100, 2500);
			expect(message.id).toBe(123);
		});

		it('should create message with correct conversation_id', async () => {
			const message = await fetchCompleteMessage(123, 456, 100, 2500);
			expect(message.conversation_id).toBe(456);
		});

		it('should create message with assistant role', async () => {
			const message = await fetchCompleteMessage(123, 456, 100, 2500);
			expect(message.role).toBe('assistant');
		});

		it('should create message with empty content (populated later by finishStreaming)', async () => {
			const message = await fetchCompleteMessage(123, 456, 100, 2500);
			expect(message.content).toBe('');
		});

		it('should create message with current timestamp', async () => {
			const message = await fetchCompleteMessage(123, 456, 100, 2500);
			expect(message.created_at).toBe('2025-11-30T10:00:00.000Z');
		});

		it('should create message with null reaction', async () => {
			const message = await fetchCompleteMessage(123, 456, 100, 2500);
			expect(message.reaction).toBeNull();
		});

		it('should create message with null parent_message_id', async () => {
			const message = await fetchCompleteMessage(123, 456, 100, 2500);
			expect(message.parent_message_id).toBeNull();
		});

		it('should create message with provided token_count', async () => {
			const message = await fetchCompleteMessage(123, 456, 150, 2500);
			expect(message.token_count).toBe(150);
		});

		it('should create message with default model_name', async () => {
			const message = await fetchCompleteMessage(123, 456, 100, 2500);
			expect(message.model_name).toBe('gpt-oss-20b');
		});

		it('should create message with provided completion_time_ms', async () => {
			const message = await fetchCompleteMessage(123, 456, 100, 3500);
			expect(message.completion_time_ms).toBe(3500);
		});
	});

	describe('edge cases', () => {
		it('should handle zero token_count', async () => {
			const message = await fetchCompleteMessage(123, 456, 0, 1000);
			expect(message.token_count).toBe(0);
		});

		it('should handle zero completion_time_ms', async () => {
			const message = await fetchCompleteMessage(123, 456, 100, 0);
			expect(message.completion_time_ms).toBe(0);
		});

		it('should handle large token counts', async () => {
			const message = await fetchCompleteMessage(123, 456, 10000, 60000);
			expect(message.token_count).toBe(10000);
		});

		it('should handle large completion times', async () => {
			const message = await fetchCompleteMessage(123, 456, 100, 300000);
			expect(message.completion_time_ms).toBe(300000);
		});

		it('should handle negative message IDs (error case)', async () => {
			// Function should not throw, even with invalid IDs
			const message = await fetchCompleteMessage(-1, -2, 100, 2500);
			expect(message.id).toBe(-1);
			expect(message.conversation_id).toBe(-2);
		});
	});

	describe('return type', () => {
		it('should return a Promise', () => {
			const result = fetchCompleteMessage(123, 456, 100, 2500);
			expect(result).toBeInstanceOf(Promise);
		});

		it('should resolve to a Message object with all required fields', async () => {
			const message = await fetchCompleteMessage(123, 456, 100, 2500);

			// Check all required Message fields exist
			expect(message).toHaveProperty('id');
			expect(message).toHaveProperty('conversation_id');
			expect(message).toHaveProperty('role');
			expect(message).toHaveProperty('content');
			expect(message).toHaveProperty('created_at');
			expect(message).toHaveProperty('reaction');
			expect(message).toHaveProperty('parent_message_id');
			expect(message).toHaveProperty('token_count');
			expect(message).toHaveProperty('model_name');
			expect(message).toHaveProperty('completion_time_ms');
		});
	});
});
