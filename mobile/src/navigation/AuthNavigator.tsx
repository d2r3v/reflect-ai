import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { AuthStackParamList } from "./types";
import LoginScreen from "../screens/LoginScreen";
import SignupScreen from "../screens/SignupScreen";

const Stack = createNativeStackNavigator<AuthStackParamList>();

/**
 * AuthNavigator
 * Handles login and signup flow. Shown when user is not authenticated.
 */
export function AuthNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true,
      }}
    >
      <Stack.Screen
        name="Login"
        component={LoginScreen}
        options={{ title: "Sign In" }}
      />
      <Stack.Screen
        name="Signup"
        component={SignupScreen}
        options={{ title: "Create Account" }}
      />
    </Stack.Navigator>
  );
}
