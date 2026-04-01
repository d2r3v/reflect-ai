import React, { useEffect, useState } from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { RootStackParamList } from "./types";
import { AuthNavigator } from "./AuthNavigator";
import { AppNavigator } from "./AppNavigator";
import SplashScreen from "../screens/SplashScreen";

const Stack = createNativeStackNavigator<RootStackParamList>();

/**
 * RootNavigator
 * Top-level navigator that handles auth state and route selection.
 * Flows:
 * - Splash (initial load)
 * - Auth (login/signup) if not authenticated
 * - App (main app) if authenticated
 */
export function RootNavigator() {
  const [isLoading, setIsLoading] = useState(true);
  const [isSignedIn, setIsSignedIn] = useState(false);

  useEffect(() => {
    // Simulate auth check (will be replaced with real auth logic)
    const timer = setTimeout(() => {
      setIsLoading(false);
      // For now, start at auth flow
      setIsSignedIn(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Splash" component={SplashScreen} />
      </Stack.Navigator>
    );
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {isSignedIn ? (
        <Stack.Screen name="App" component={AppNavigator} />
      ) : (
        <Stack.Screen name="Auth" component={AuthNavigator} />
      )}
    </Stack.Navigator>
  );
}
