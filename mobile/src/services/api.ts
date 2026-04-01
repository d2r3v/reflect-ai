/**
 * API Service
 * Handles communication with the FastAPI backend.
 */
import Constants from 'expo-constants';

// For Android emulator, localhost is 10.0.2.2
const getBaseUrl = () => {
    const debuggerHost = Constants.expoConfig?.hostUri;
    if (__DEV__ && debuggerHost) {
        const host = debuggerHost.split(':')[0];
        return `http://${host}:8000/api/v1`;
    }
    return 'http://localhost:8000/api/v1'; // Default
};

export const API_URL = getBaseUrl();

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
};
