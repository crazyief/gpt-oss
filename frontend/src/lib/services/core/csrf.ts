/**
 * CSRF Token Client
 *
 * Manages CSRF token lifecycle:
 * - Lazy fetch (only when needed)
 * - SessionStorage cache (survives page refresh)
 * - Auto-refresh on 403 error
 * - Transparent to API consumers
 */

import { API_BASE_URL } from '$lib/config';

const CSRF_TOKEN_KEY = 'csrf_token';
const CSRF_EXPIRY_KEY = 'csrf_token_expiry';
const TOKEN_TTL = 3600000; // 1 hour in milliseconds

class CSRFClient {
	private token: string | null = null;
	private tokenExpiry: number = 0;
	private fetchPromise: Promise<string> | null = null;
	private refreshPromise: Promise<string> | null = null;

	/**
	 * Check if SessionStorage is available.
	 * @private
	 */
	private isStorageAvailable(): boolean {
		try {
			const testKey = '__csrf_storage_test__';
			sessionStorage.setItem(testKey, 'test');
			sessionStorage.removeItem(testKey);
			return true;
		} catch {
			// SessionStorage disabled (private browsing, storage full, etc.)
			return false;
		}
	}

	/**
	 * Get current CSRF token.
	 * Fetches from server if not cached or expired.
	 *
	 * @returns Promise<string> - CSRF token
	 */
	async getToken(): Promise<string> {
		// Check if token is still valid
		if (this.token && Date.now() < this.tokenExpiry) {
			return this.token;
		}

		// Check sessionStorage cache
		const cachedToken = this.loadFromCache();
		if (cachedToken) {
			return cachedToken;
		}

		// Fetch new token (prevent concurrent fetches)
		if (this.fetchPromise) {
			return this.fetchPromise;
		}

		this.fetchPromise = this.fetchToken();

		try {
			const token = await this.fetchPromise;
			return token;
		} finally {
			this.fetchPromise = null;
		}
	}

	/**
	 * Fetch new CSRF token from server.
	 * @private
	 */
	private async fetchToken(): Promise<string> {
		try {
			// In development, use relative URL (Vite proxy handles /api/* → backend)
			// In production, use absolute URL with API_BASE_URL
			const url = import.meta.env.DEV ? '/api/csrf-token' : `${API_BASE_URL}/api/csrf-token`;
			console.log('[CSRF] Fetching token from:', url, 'DEV mode:', import.meta.env.DEV);
			const response = await fetch(url);
			console.log('[CSRF] Response status:', response.status);

			if (!response.ok) {
				throw new Error(`Failed to fetch CSRF token: ${response.statusText}`);
			}

			const data = await response.json();
			const token = data.csrf_token;

			if (!token) {
				throw new Error('CSRF token not found in response');
			}

			// Cache token
			this.token = token;
			this.tokenExpiry = Date.now() + TOKEN_TTL;
			this.saveToCache(token);

			return token;
		} catch (error) {
			console.error('CSRF token fetch failed:', error);
			throw error;
		}
	}

	/**
	 * Load token from sessionStorage.
	 * @private
	 */
	private loadFromCache(): string | null {
		if (!this.isStorageAvailable()) {
			console.warn('SessionStorage unavailable, CSRF token caching disabled');
			return null;
		}

		try {
			const token = sessionStorage.getItem(CSRF_TOKEN_KEY);
			const expiryStr = sessionStorage.getItem(CSRF_EXPIRY_KEY);

			if (!token || !expiryStr) {
				return null;
			}

			const expiry = parseInt(expiryStr, 10);
			if (Date.now() >= expiry) {
				// Expired, clear cache
				this.clearCache();
				return null;
			}

			// Restore in-memory cache
			this.token = token;
			this.tokenExpiry = expiry;

			return token;
		} catch (error) {
			console.error('Failed to load CSRF token from cache:', error);
			return null;
		}
	}

	/**
	 * Save token to sessionStorage.
	 * @private
	 */
	private saveToCache(token: string): void {
		if (!this.isStorageAvailable()) {
			// Graceful degradation: in-memory cache still works
			return;
		}

		try {
			sessionStorage.setItem(CSRF_TOKEN_KEY, token);
			sessionStorage.setItem(CSRF_EXPIRY_KEY, this.tokenExpiry.toString());
		} catch (error) {
			console.error('Failed to save CSRF token to cache:', error);
		}
	}

	/**
	 * Clear cached token (on expiry or logout).
	 */
	clearCache(): void {
		this.token = null;
		this.tokenExpiry = 0;

		if (!this.isStorageAvailable()) {
			return;
		}

		try {
			sessionStorage.removeItem(CSRF_TOKEN_KEY);
			sessionStorage.removeItem(CSRF_EXPIRY_KEY);
		} catch (error) {
			console.error('Failed to clear CSRF token cache:', error);
		}
	}

	/**
	 * Refresh token (force fetch new token).
	 * Used when 403 error suggests token expired.
	 * Prevents concurrent refresh attempts via refresh lock.
	 */
	async refreshToken(): Promise<string> {
		// If refresh already in progress, return existing promise
		if (this.refreshPromise) {
			return this.refreshPromise;
		}

		// Start new refresh
		this.refreshPromise = this._doRefresh();

		try {
			const token = await this.refreshPromise;
			return token;
		} finally {
			this.refreshPromise = null;
		}
	}

	/**
	 * Internal refresh implementation.
	 * @private
	 */
	private async _doRefresh(): Promise<string> {
		this.clearCache();
		return this.getToken();
	}
}

// Singleton instance
export const csrfClient = new CSRFClient();
