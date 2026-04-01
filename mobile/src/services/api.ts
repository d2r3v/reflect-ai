/**
 * API Service
 * Handles communication with the FastAPI backend.
 */
import Constants from 'expo-constants';

import { Platform } from 'react-native';

// For Android emulator, localhost is 10.0.2.2
const getBaseUrl = () => {
    const debuggerHost = Constants.expoConfig?.hostUri;
    if (__DEV__) {
        if (debuggerHost) {
            const host = debuggerHost.split(':')[0];
            return `http://${host}:8000/api/v1`;
        }
        // Fallback for Android emulator
        if (Platform.OS === 'android') {
            return 'http://10.0.2.2:8000/api/v1';
        }
    }
    return 'http://localhost:8000/api/v1'; // Default
};

import * as SecureStore from 'expo-secure-store';

export const API_URL = getBaseUrl();

const getAuthHeaders = async () => {
    const token = await SecureStore.getItemAsync('auth_token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    };
};

export const api = {
    get: async (path: string) => {
        const response = await fetch(`${API_URL}${path}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    },
    post: async (path: string, data: any) => {
        const response = await fetch(`${API_URL}${path}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    },
    authGet: async (path: string) => {
        const headers = await getAuthHeaders();
        const response = await fetch(`${API_URL}${path}`, { headers });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    },
    authPost: async (path: string, data: any) => {
        const headers = await getAuthHeaders();
        const response = await fetch(`${API_URL}${path}`, {
            method: 'POST',
            headers,
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    },
};
