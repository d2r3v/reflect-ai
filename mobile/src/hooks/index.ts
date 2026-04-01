/**
 * Custom hooks for the app.
 * Will be expanded with useAuth, useChat, etc.
 */

import { useState, useCallback } from "react";

/**
 * useAuth
 * Manages authentication state and auth operations.
 * TODO: Implement with real auth logic.
 */
export function useAuth() {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      // TODO: Call API
      console.log("Login attempt:", email);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const signup = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      // TODO: Call API
      console.log("Signup attempt:", email);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
  }, []);

  return {
    user,
    isLoading,
    error,
    login,
    signup,
    logout,
  };
}
