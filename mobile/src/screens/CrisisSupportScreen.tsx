import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AppStackParamList } from "../navigation/types";
import { Colors } from "../constants/colors";

type Props = NativeStackScreenProps<AppStackParamList, "CrisisSupport">;

/**
 * CrisisSupportScreen
 * Displays crisis support resources and grounding techniques.
 * This is a safety-focused screen for critical situations.
 * TODO: Implement emergency contact integration.
 */
export default function CrisisSupportScreen({ navigation }: Props) {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.heading}>Crisis Support</Text>
        <Text style={styles.subtitle}>
          If you're in immediate danger, please call emergency services.
        </Text>
      </View>

      <View style={styles.emergencySection}>
        <Text style={styles.sectionTitle}>Emergency Resources</Text>
        <View style={styles.resourceCard}>
          <Text style={styles.resourceTitle}>National Suicide Prevention Lifeline</Text>
          <Text style={styles.resourcePhone}>1-800-273-8255</Text>
          <Text style={styles.resourceNote}>Available 24/7</Text>
        </View>
        <View style={styles.resourceCard}>
          <Text style={styles.resourceTitle}>Crisis Text Line</Text>
          <Text style={styles.resourcePhone}>Text HOME to 741741</Text>
          <Text style={styles.resourceNote}>Free, confidential, 24/7</Text>
        </View>
      </View>

      <View style={styles.groundingSection}>
        <Text style={styles.sectionTitle}>Grounding Techniques</Text>
        <View style={styles.techniqueCard}>
          <Text style={styles.techniqueName}>5-4-3-2-1 Technique</Text>
          <Text style={styles.techniqueDesc}>
            Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.
          </Text>
        </View>
        <View style={styles.techniqueCard}>
          <Text style={styles.techniqueName}>Box Breathing</Text>
          <Text style={styles.techniqueDesc}>
            Breathe in for 4 counts, hold for 4, exhale for 4, hold for 4. Repeat.
          </Text>
        </View>
      </View>

      <TouchableOpacity style={styles.contactButton}>
        <Text style={styles.contactButtonText}>Contact Mental Health Professional</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    padding: 16,
    backgroundColor: Colors.danger,
  },
  heading: {
    fontSize: 28,
    fontWeight: "bold",
    color: Colors.surface,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: Colors.surface,
  },
  emergencySection: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: Colors.text,
    marginBottom: 12,
  },
  resourceCard: {
    backgroundColor: Colors.surface,
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: Colors.danger,
  },
  resourceTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: Colors.text,
    marginBottom: 8,
  },
  resourcePhone: {
    fontSize: 14,
    fontWeight: "bold",
    color: Colors.danger,
    marginBottom: 4,
  },
  resourceNote: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  groundingSection: {
    padding: 16,
  },
  techniqueCard: {
    backgroundColor: Colors.surface,
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  techniqueName: {
    fontSize: 16,
    fontWeight: "600",
    color: Colors.text,
    marginBottom: 8,
  },
  techniqueDesc: {
    fontSize: 14,
    color: Colors.textSecondary,
    lineHeight: 20,
  },
  contactButton: {
    margin: 16,
    backgroundColor: Colors.primary,
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
  },
  contactButtonText: {
    color: Colors.surface,
    fontSize: 16,
    fontWeight: "600",
  },
});
