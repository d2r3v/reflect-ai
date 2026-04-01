import React from "react";
import { View, Text, StyleSheet, FlatList } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AppStackParamList } from "../navigation/types";
import { Colors } from "../constants/colors";

type Props = NativeStackScreenProps<AppStackParamList, "Home">;

/**
 * HomeScreen
 * Main dashboard showing recent conversations, mood, and quick actions.
 * TODO: Implement real data fetching and layout.
 */
export default function HomeScreen({ navigation }: Props) {
  const recentConversations = [
    { id: "1", title: "Conversation 1", date: "Today" },
    { id: "2", title: "Conversation 2", date: "Yesterday" },
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.heading}>Welcome Back</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Conversations</Text>
        <FlatList
          data={recentConversations}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <View style={styles.conversationCard}>
              <Text style={styles.conversationTitle}>{item.title}</Text>
              <Text style={styles.conversationDate}>{item.date}</Text>
            </View>
          )}
          scrollEnabled={false}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionCard}>
          <Text style={styles.actionText}>Start a new conversation</Text>
        </View>
        <View style={styles.actionCard}>
          <Text style={styles.actionText}>Check your mood</Text>
        </View>
      </View>
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
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: Colors.text,
    marginBottom: 12,
  },
  conversationCard: {
    backgroundColor: Colors.surface,
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  conversationTitle: {
    fontSize: 16,
    fontWeight: "500",
    color: Colors.text,
  },
  conversationDate: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  actionCard: {
    backgroundColor: Colors.surface,
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  actionText: {
    fontSize: 16,
    color: Colors.text,
  },
});
