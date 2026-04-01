/**
 * Auth Service
 * Handles API calls for login/signup and manages token persistence.
 */
import * as SecureStore from 'expo-secure-store';
import { API_URL } from './api';

const TOKEN_KEY = 'auth_token';

const parseError = async (response: Response): Promise<string> => {
    try {
        const data = await response.json();
        if (Array.isArray(data.detail)) {
            return data.detail.map((d: any) => d.msg).join(', ');
        }
        return data.detail || `Server error ${response.status}`;
    } catch {
        const text = await response.text().catch(() => '');
        return text || `Server error ${response.status}`;
    }
};

const fetchWithTimeout = async (url: string, options: RequestInit, ms = 8000) => {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), ms);
    try {
        const response = await fetch(url, { ...options, signal: controller.signal });
        clearTimeout(id);
        return response;
    } catch (err: any) {
        clearTimeout(id);
        if (err.name === 'AbortError') {
            throw new Error(`Connection timed out. Backend not reachable.\nURL: ${url}`);
        }
        throw err;
    }
};

export const authService = {
    /**
     * Login with email and password
     */
    async login(email: string, password: string) {
        const url = `${API_URL}/auth/login`;
        console.log('[auth] login →', url);
        const response = await fetchWithTimeout(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            const msg = await parseError(response);
            throw new Error(msg);
        }

        const data = await response.json();
        console.log('[auth] login OK');
        await this.saveToken(data.access_token);
        return data;
    },

    /**
     * Register a new user
     */
    async signup(email: string, password: string) {
        const url = `${API_URL}/auth/register`;
        console.log('[auth] signup →', url);
        const response = await fetchWithTimeout(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            const msg = await parseError(response);
            throw new Error(msg);
        }

        const data = await response.json();
        console.log('[auth] signup OK');
        await this.saveToken(data.access_token);
        return data;
    },

    /**
     * Persist token to secure storage
     */
    async saveToken(token: string) {
        await SecureStore.setItemAsync(TOKEN_KEY, token);
    },

    /**
     * Load token from secure storage
     */
    async loadToken() {
        return await SecureStore.getItemAsync(TOKEN_KEY);
    },

    /**
     * Remove token from secure storage
     */
    async clearToken() {
        await SecureStore.deleteItemAsync(TOKEN_KEY);
    },
};
