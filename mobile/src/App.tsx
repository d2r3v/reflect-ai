import React from "react";
import { StatusBar } from "expo-status-bar";
import { NavigationContainer } from "@react-navigation/native";
import { RootNavigator } from "./navigation/RootNavigator";

/**
 * App Component
 * Main entry point for the React Native application.
 * Initializes navigation and global setup.
 */
export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="dark" />
      <RootNavigator />
    </NavigationContainer>
  );
}
