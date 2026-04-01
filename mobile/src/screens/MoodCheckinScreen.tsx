import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AppStackParamList } from "../navigation/types";
import { Colors } from "../constants/colors";

type Props = NativeStackScreenProps<AppStackParamList, "MoodCheckin">;

/**
 * MoodCheckinScreen
 * Allows users to log their mood and intensity.
 * TODO: Implement mood logging and history visualization.
 */
export default function MoodCheckinScreen({ navigation }: Props) {
  const [selectedMood, setSelectedMood] = React.useState<string | null>(null);
  const [intensity, setIntensity] = React.useState(5);

  const moods = ["😢", "😐", "🙂", "😊", "😄"];
  const moodLabels = ["Anxious", "Okay", "Calm", "Happy", "Excited"];

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>How are you feeling?</Text>

      <View style={styles.moodGrid}>
        {moods.map((emoji, index) => (
          <TouchableOpacity
            key={index}
            style={[
              styles.moodButton,
              selectedMood === index && styles.moodButtonSelected,
            ]}
            onPress={() => setSelectedMood(index)}
          >
            <Text style={styles.emoji}>{emoji}</Text>
            <Text style={styles.moodLabel}>{moodLabels[index]}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          Intensity: {intensity}
        </Text>
        <View style={styles.sliderContainer}>
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
            <TouchableOpacity
              key={num}
              style={[
                styles.sliderButton,
                intensity === num && styles.sliderButtonActive,
              ]}
              onPress={() => setIntensity(num)}
            >
              <Text style={styles.sliderLabel}>{num}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <TouchableOpacity style={styles.submitButton}>
        <Text style={styles.submitButtonText}>Save Mood</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: Colors.background,
  },
  heading: {
    fontSize: 28,
    fontWeight: "bold",
    color: Colors.text,
    marginBottom: 24,
  },
  moodGrid: {
    flexDirection: "row",
    justifyContent: "space-around",
    marginBottom: 32,
  },
  moodButton: {
    alignItems: "center",
    padding: 16,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: "transparent",
  },
  moodButtonSelected: {
    borderColor: Colors.primary,
    backgroundColor: Colors.surface,
  },
  emoji: {
    fontSize: 32,
    marginBottom: 8,
  },
  moodLabel: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: Colors.text,
    marginBottom: 12,
  },
  sliderContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  sliderButton: {
    padding: 8,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  sliderButtonActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  sliderLabel: {
    fontSize: 12,
    color: Colors.text,
  },
  submitButton: {
    backgroundColor: Colors.primary,
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 16,
  },
  submitButtonText: {
    color: Colors.surface,
    fontSize: 16,
    fontWeight: "600",
  },
});
