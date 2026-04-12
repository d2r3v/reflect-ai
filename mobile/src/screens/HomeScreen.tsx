import React, { useCallback, useState } from "react";
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ScrollView, ActivityIndicator } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useFocusEffect } from "@react-navigation/native";
import { AppStackParamList } from "../navigation/types";
import { Colors } from "../constants/colors";
import { useAuth } from "../context/AuthContext";
import { conversationsService, Conversation } from "../services/conversations";

type Props = NativeStackScreenProps<AppStackParamList, "Home">;

export default function HomeScreen({ navigation }: Props) {
  const { signOut } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchConversations = useCallback(async () => {
    try {
      const data = await conversationsService.listConversations();
      setConversations(data);
    } catch (err) {
      console.error("Failed to load conversations", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      fetchConversations();
    }, [fetchConversations])
  );

  const handleStartNewConversation = async () => {
    try {
      const conv = await conversationsService.createConversation();
      navigation.navigate("Chat", { conversationId: conv.id });
    } catch (err) {
      console.error("Failed to create conversation", err);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.heading}>Welcome Back</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Conversations</Text>
        {loading ? (
          <ActivityIndicator size="small" color={Colors.primary} />
        ) : conversations.length === 0 ? (
          <Text style={styles.emptyText}>No conversations yet.</Text>
        ) : (
          <FlatList
            data={conversations}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.conversationCard}
                onPress={() => navigation.navigate("Chat", { conversationId: item.id })}
              >
                <Text style={styles.conversationTitle}>{item.title}</Text>
                <Text style={styles.conversationDate}>
                  {new Date(item.created_at).toLocaleDateString()}
                </Text>
              </TouchableOpacity>
            )}
            scrollEnabled={false}
          />
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <TouchableOpacity style={styles.actionCard} onPress={handleStartNewConversation}>
          <Text style={styles.actionText}>Start a new conversation</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={signOut}>
        <Text style={styles.logoutButtonText}>Sign Out</Text>
      </TouchableOpacity>
    </ScrollView>
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
  emptyText: {
    color: Colors.textSecondary,
    fontStyle: 'italic',
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
  logoutButton: {
    backgroundColor: Colors.danger,
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 8,
    marginBottom: 32,
  },
  logoutButtonText: {
    color: Colors.surface,
    fontSize: 16,
    fontWeight: "600",
  },
});
