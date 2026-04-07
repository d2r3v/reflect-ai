/**
 * Auth Context
 * Provides global authentication state and methods to the entire app.
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/auth';

interface AuthContextType {
    token: string | null;
    isLoading: boolean;
    signIn: (email: string, password: string) => Promise<void>;
    signUp: (email: string, password: string) => Promise<void>;
    signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check for persisted token on mount
        const bootstrapAsync = async () => {
            console.log('AuthContext: Bootstrapping auth state...');
            try {
                const persistedToken = await authService.loadToken();
                console.log('AuthContext: Persisted token found:', !!persistedToken);
                setToken(persistedToken);
            } catch (e) {
                console.error('AuthContext: Failed to load token', e);
            } finally {
                console.log('AuthContext: Loading complete.');
                setIsLoading(false);
            }
        };

        bootstrapAsync();
    }, []);

    const signIn = async (email: string, password: string) => {
        const data = await authService.login(email, password);
        setToken(data.access_token);
    };

    const signUp = async (email: string, password: string) => {
        const data = await authService.signup(email, password);
        setToken(data.access_token);
    };

    const signOut = async () => {
        await authService.clearToken();
        setToken(null);
    };

    return (
        <AuthContext.Provider value={{ token, isLoading, signIn, signUp, signOut }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
