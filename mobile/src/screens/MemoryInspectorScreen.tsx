import React, { useState, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  RefreshControl,
  TouchableOpacity,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AppStackParamList } from "../navigation/types";
import { Colors } from "../constants/colors";
import { memoryService, Memory } from "../services/memory";

type Props = NativeStackScreenProps<AppStackParamList, "MemoryInspector">;

/**
 * MemoryInspectorScreen
 * Transparently shows the user every insight the AI has learned about them,
 * fetched live from GET /api/v1/memories.
 */
export default function MemoryInspectorScreen({ navigation }: Props) {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    setError(null);
    try {
      const data = await memoryService.listMemories();
      setMemories(data);
    } catch (e) {
      console.error("Failed to load memories", e);
      setError("Couldn't load your memories. Pull down to try again.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Refetch every time the screen comes into focus so newly-learned insights
  // appear right after chatting.
  useFocusEffect(
    useCallback(() => {
      load();
    }, [load])
  );

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

  const getCategoryLabel = (category: string) =>
    category.replace(/_/g, " ").toUpperCase();

  const formatRelative = (iso: string) => {
    const then = new Date(iso).getTime();
    if (isNaN(then)) return "";
    const diffMs = Date.now() - then;
    const mins = Math.max(0, Math.floor(diffMs / 60000));
    if (mins < 1) return "just now";
    if (mins < 60) return `${mins} min ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs} hr${hrs === 1 ? "" : "s"} ago`;
    const days = Math.floor(hrs / 24);
    return `${days} day${days === 1 ? "" : "s"} ago`;
  };

  const renderBody = () => {
    if (loading) {
      return (
        <View style={styles.centered}>
          <ActivityIndicator size="large" color={Colors.primary} />
        </View>
      );
    }

    if (error) {
      return (
        <View style={styles.centered}>
          <Text style={styles.emptyText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={() => load()}>
            <Text style={styles.retryText}>Retry</Text>
          </TouchableOpacity>
        </View>
      );
    }

    return (
      <FlatList
        data={memories}
        keyExtractor={(item) => item.id}
        contentContainerStyle={memories.length === 0 && styles.flexGrow}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => load(true)} />
        }
        ListEmptyComponent={
          <View style={styles.centered}>
            <Text style={styles.emptyTitle}>No memories yet</Text>
            <Text style={styles.emptyText}>
              Keep chatting — when you share what helps you, a stressor, or a
              preference, it'll show up here so you can see exactly what I've
              learned.
            </Text>
          </View>
        }
        renderItem={({ item }) => (
          <View
            style={[
              styles.memoryCard,
              { borderLeftColor: getCategoryColor(item.category) },
            ]}
          >
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
              <Text style={styles.extractedDate}>
                {formatRelative(item.created_at)}
              </Text>
            </View>
            <Text style={styles.memoryContent}>{item.content}</Text>
          </View>
        )}
      />
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Your Memories</Text>
      <Text style={styles.subtitle}>
        These are insights the AI has learned about you.
      </Text>
      {renderBody()}
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
  flexGrow: {
    flexGrow: 1,
  },
  centered: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 24,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: Colors.text,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 14,
    color: Colors.textSecondary,
    textAlign: "center",
    lineHeight: 20,
  },
  retryButton: {
    marginTop: 16,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
    backgroundColor: Colors.primary,
  },
  retryText: {
    color: Colors.surface,
    fontWeight: "600",
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
