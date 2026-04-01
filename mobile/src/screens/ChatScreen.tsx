import React from "react";
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AppStackParamList } from "../navigation/types";
import { Colors } from "../constants/colors";

type Props = NativeStackScreenProps<AppStackParamList, "Chat">;

/**
 * ChatScreen
 * Main chat interface for user-AI conversations.
 * TODO: Implement message sending, receiving, and real-time updates.
 */
export default function ChatScreen({ navigation }: Props) {
  const [inputText, setInputText] = React.useState("");
  const [messages, setMessages] = React.useState([
    { id: "1", role: "assistant", content: "Hi! How are you doing today?" },
  ]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage = { id: String(messages.length + 1), role: "user" as const, content: inputText };
    setMessages((prev) => [...prev, userMessage]);
    setInputText("");

    try {
      // For the vertical slice, we call the test endpoint
      // Using Android localhost shortcut (10.0.2.2) if on emulator, or actual IP
      // Using API_BASE_URL from env if available
      const response = await fetch("http://10.0.2.2:8000/api/v1/chat/test");
      const data = await response.json();

      const assistantMessage = {
        id: String(messages.length + 2),
        role: "assistant" as const,
        content: data.reply,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error fetching from backend:", error);
      const errorMessage = {
        id: String(messages.length + 3),
        role: "assistant" as const,
        content: "Error connecting to backend. Make sure the server is running.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View
            style={[
              styles.messageBubble,
              item.role === "user" ? styles.userBubble : styles.assistantBubble,
            ]}
          >
            <Text style={styles.messageText}>{item.content}</Text>
          </View>
        )}
        contentContainerStyle={styles.messagesList}
      />

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
  messagesList: {
    padding: 16,
  },
  messageBubble: {
    marginBottom: 12,
    maxWidth: "80%",
    padding: 12,
    borderRadius: 8,
  },
  userBubble: {
    alignSelf: "flex-end",
    backgroundColor: Colors.primary,
  },
  assistantBubble: {
    alignSelf: "flex-start",
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  messageText: {
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
    borderRadius: 8,
    padding: 12,
    marginRight: 8,
    maxHeight: 100,
  },
  sendButton: {
    backgroundColor: Colors.primary,
    borderRadius: 8,
    justifyContent: "center",
    paddingHorizontal: 16,
  },
  sendButtonText: {
    color: Colors.surface,
    fontWeight: "600",
  },
});
