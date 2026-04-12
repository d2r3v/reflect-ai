import React, { useState, useCallback } from "react";
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, ActivityIndicator } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useFocusEffect } from "@react-navigation/native";
import { AppStackParamList } from "../navigation/types";
import { Colors } from "../constants/colors";
import { conversationsService, Message } from "../services/conversations";

type Props = NativeStackScreenProps<AppStackParamList, "Chat">;

export default function ChatScreen({ route, navigation }: Props) {
  const [inputText, setInputText] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeConvId, setActiveConvId] = useState<string | undefined>(route.params?.conversationId);

  // Reload when tab changes or params change
  useFocusEffect(
    useCallback(() => {
      // If we got here with a specific ID, use it
      const id = route.params?.conversationId;
      if (id) {
        setActiveConvId(id);
        fetchMessages(id);
      } else if (!activeConvId) {
        // If we just tapped the tab without an ID and don't have one active, clear chat
        setMessages([]);
      }
    }, [route.params?.conversationId])
  );

  const fetchMessages = async (id: string) => {
    setLoading(true);
    try {
      const convConfig = await conversationsService.getConversation(id);
      setMessages(convConfig.messages);
    } catch (error) {
      console.error("Failed to load messages", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    const text = inputText.trim();
    if (!text) return;
    setInputText("");

    let currentConvId = activeConvId;

    // Create a conversation lazily if we don't have one yet
    if (!currentConvId) {
      try {
        const conv = await conversationsService.createConversation();
        currentConvId = conv.id;
        setActiveConvId(currentConvId);
        // Important: Update params so navigation state knows where we are
        navigation.setParams({ conversationId: currentConvId });
      } catch (err) {
        console.error("Failed to create lazy conversation", err);
        return;
      }
    }

    try {
      // We expect the backend to return { messages: [userMsg, assistantMsg], response_mode: "..." }
      const response = await conversationsService.sendMessage(currentConvId, text);
      const newMessages = response.messages;

      // We can either append the returned messages or refetch. We'll append.
      // Filter out any messages we already have by id just in case.
      setMessages((prev) => {
        const existingIds = new Set(prev.map(m => m.id));
        const toAdd = newMessages.filter(m => !existingIds.has(m.id));
        return [...prev, ...toAdd];
      });
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  return (
    <View style={styles.container}>
      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={Colors.primary} />
        </View>
      ) : (
        <FlatList
          data={messages}
          keyExtractor={(item, index) => item.id || `temp-${index}`}
          renderItem={({ item }) => (
            <View
              style={[
                styles.messageBubble,
                item.role === "user" ? styles.userBubble : styles.assistantBubble,
              ]}
            >
              <Text style={item.role === "user" ? styles.userText : styles.assistantText}>
                {item.content}
              </Text>
            </View>
          )}
          contentContainerStyle={styles.messagesList}
          ListEmptyComponent={
            <Text style={styles.emptyText}>Send a message to start chatting!</Text>
          }
        />
      )}

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Type your message..."
          value={inputText}
          onChangeText={setInputText}
          multiline
        />
        <TouchableOpacity style={styles.sendButton} onPress={handleSendMessage}>
          <Text style={styles.sendButtonText}>Send</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  messagesList: {
    padding: 16,
    paddingBottom: 32, // Extra padding at bottom
  },
  emptyText: {
    textAlign: "center",
    marginTop: 40,
    color: Colors.textSecondary,
    fontStyle: 'italic',
  },
  messageBubble: {
    marginBottom: 12,
    maxWidth: "85%",
    padding: 14,
    borderRadius: 16,
  },
  userBubble: {
    alignSelf: "flex-end",
    backgroundColor: Colors.primary,
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    alignSelf: "flex-start",
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    borderBottomLeftRadius: 4,
  },
  userText: {
    fontSize: 16,
    color: Colors.surface, // Assuming primary is dark enough
  },
  assistantText: {
    fontSize: 16,
    color: Colors.text,
  },
  inputContainer: {
    flexDirection: "row",
    padding: 16,
    backgroundColor: Colors.surface,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 12,
    marginRight: 8,
    maxHeight: 120,
    minHeight: 45,
    backgroundColor: Colors.background,
  },
  sendButton: {
    backgroundColor: Colors.primary,
    borderRadius: 20,
    justifyContent: "center",
    paddingHorizontal: 20,
    height: 45,
    alignSelf: "flex-end",
  },
  sendButtonText: {
    color: Colors.surface,
    fontWeight: "600",
  },
});
