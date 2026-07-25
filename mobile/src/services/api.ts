/**
 * API Service
 * Handles communication with the FastAPI backend.
 */
import Constants from 'expo-constants';

import { Platform } from 'react-native';

const getBaseUrl = () => {
    const debuggerHost = Constants.expoConfig?.hostUri;
    if (__DEV__) {
        let host = debuggerHost ? debuggerHost.split(':')[0] : undefined;
        // Inside the Android emulator, `localhost` is the emulator itself — the host
        // machine (where the backend runs) is reachable at 10.0.2.2. Metro connects
        // over adb reverse as localhost, so rewrite it here.
        if (Platform.OS === 'android' && (!host || host === 'localhost' || host === '127.0.0.1')) {
            host = '10.0.2.2';
        }
        if (host) {
            return `http://${host}:8000/api/v1`;
        }
    }
    return 'http://localhost:8000/api/v1'; // Default
};

import { storage } from './storage';

export const API_URL = getBaseUrl();

const getAuthHeaders = async () => {
    const token = await storage.getItemAsync('auth_token');
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
