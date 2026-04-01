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

  const handleSendMessage = () => {
    if (inputText.trim()) {
      setMessages([
        ...messages,
        { id: String(messages.length + 1), role: "user", content: inputText },
      ]);
      setInputText("");
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
