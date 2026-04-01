import React from "react";
import { View, Text, StyleSheet, FlatList } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AppStackParamList } from "../navigation/types";
import { Colors } from "../constants/colors";

type Props = NativeStackScreenProps<AppStackParamList, "MemoryInspector">;

/**
 * MemoryInspectorScreen
 * Allows users to view extracted memories and see memory transparency.
 * TODO: Implement memory editing, deletion, and categorization.
 */
export default function MemoryInspectorScreen({ navigation }: Props) {
  const [memories] = React.useState([
    {
      id: "1",
      category: "recurring_stressor",
      content: "Work deadlines cause anxiety",
      extractedAt: "2 days ago",
    },
    {
      id: "2",
      category: "coping_strategy",
      content: "Deep breathing exercises help calm down",
      extractedAt: "1 week ago",
    },
    {
      id: "3",
      category: "preference",
      content: "Prefers reflection over advice",
      extractedAt: "3 days ago",
    },
  ]);

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "recurring_stressor":
        return Colors.danger;
      case "coping_strategy":
        return Colors.success;
      case "preference":
        return Colors.primary;
      default:
        return Colors.border;
    }
  };

  const getCategoryLabel = (category: string) => {
    return category.replace("_", " ").toUpperCase();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Your Memories</Text>
      <Text style={styles.subtitle}>
        These are insights the AI has learned about you.
      </Text>

      <FlatList
        data={memories}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.memoryCard}>
            <View style={styles.memoryHeader}>
              <View
                style={[
                  styles.categoryBadge,
                  { backgroundColor: getCategoryColor(item.category) },
                ]}
              >
                <Text style={styles.categoryLabel}>
                  {getCategoryLabel(item.category)}
                </Text>
              </View>
              <Text style={styles.extractedDate}>{item.extractedAt}</Text>
            </View>
            <Text style={styles.memoryContent}>{item.content}</Text>
          </View>
        )}
      />
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
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 24,
  },
  memoryCard: {
    backgroundColor: Colors.surface,
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  memoryHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  categoryBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  categoryLabel: {
    fontSize: 11,
    fontWeight: "600",
    color: Colors.surface,
  },
  extractedDate: {
    fontSize: 12,
    color: Colors.textSecondary,
  },
  memoryContent: {
    fontSize: 16,
    color: Colors.text,
    lineHeight: 22,
  },
});
