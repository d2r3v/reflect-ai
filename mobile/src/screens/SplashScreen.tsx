import React from "react";
import { View, Text, StyleSheet, ActivityIndicator } from "react-native";
import { Colors } from "../constants/colors";

/**
 * SplashScreen
 * Shown during app initialization.
 */
export default function SplashScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Memory-Aware Support Companion</Text>
      <ActivityIndicator size="large" color={Colors.primary} />
      <Text style={styles.subtitle}>Initializing...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: Colors.background,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: Colors.text,
    marginBottom: 16,
  },
  subtitle: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginTop: 16,
  },
});
