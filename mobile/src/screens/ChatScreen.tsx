import React, { useState, useCallback, useRef } from "react";
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, ActivityIndicator, Linking, KeyboardAvoidingView, Platform } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useFocusEffect } from "@react-navigation/native";
import { useHeaderHeight } from "@react-navigation/elements";
import { AppStackParamList } from "../navigation/types";
import { Colors } from "../constants/colors";
import { conversationsService, Message } from "../services/conversations";

type Props = NativeStackScreenProps<AppStackParamList, "Chat">;

interface LocalMessage extends Message {
  isCrisis?: boolean;
}

export default function ChatScreen({ route, navigation }: Props) {
  const headerHeight = useHeaderHeight();
  const [inputText, setInputText] = useState("");
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeConvId, setActiveConvId] = useState<string | undefined>(route.params?.conversationId);
  const [safetyState, setSafetyState] = useState<"normal" | "crisis" | "post_crisis">("normal");
  const [convTitle, setConvTitle] = useState<string>("");
  const lastLoadedConvId = useRef<string | undefined>(undefined);

  // Reflect the conversation's title in the screen header.
  React.useLayoutEffect(() => {
    navigation.setOptions({ title: convTitle || "Chat" });
  }, [navigation, convTitle]);

  // Reload when tab changes or params change
  useFocusEffect(
    useCallback(() => {
      // If we got here with a specific ID, use it
      const id = route.params?.conversationId;
      if (id && id !== lastLoadedConvId.current) {
        setActiveConvId(id);
        lastLoadedConvId.current = id;
        fetchMessages(id);
      } else if (!id && !activeConvId) {
        // If we just tapped the tab without an ID and don't have one active, clear chat
        setMessages([]);
        setConvTitle("");
      }
    }, [route.params?.conversationId])
  );

  const fetchMessages = async (id: string) => {
    setLoading(true);
    try {
      const convConfig = await conversationsService.getConversation(id);
      setMessages(convConfig.messages);
      setConvTitle(convConfig.title || "");
      // Don't reset safetyState on refetch — it's driven by sendMessage responses only
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
      // We expect the backend to return { messages: [userMsg, assistantMsg], response_mode: "...", safety_state: "..." }
      const response = await conversationsService.sendMessage(currentConvId, text);
      const backendSafetyState = response.safety_state || "normal";
      if (response.title) setConvTitle(response.title);

      // Update our explicit crisis mode state based on latest backend decision
      setSafetyState(backendSafetyState);

      const newMessages = response.messages.map(m => ({
        ...m,
        // Tag the assistant's reply if it was generated in full crisis mode
        isCrisis: backendSafetyState === "crisis" && m.role === "assistant"
      }));

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
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={headerHeight}
    >
      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={Colors.primary} />
        </View>
      ) : (
        <FlatList
          data={messages}
          keyExtractor={(item, index) => item.id || `temp-${index}`}
          renderItem={({ item }) => {
            // Crisis-mode assistant messages get a dedicated card
            const isCrisisMessage = item.isCrisis || (item.role === "assistant" && item.content.includes("Please call or text 988"));
            if (isCrisisMessage) {
              return (
                <View style={styles.crisisCard}>
                  <View style={styles.crisisCardHeader}>
                    <Text style={styles.crisisCardIcon}>🤍</Text>
                    <Text style={styles.crisisCardTitle}>We're here for you</Text>
                  </View>
                  <Text style={styles.crisisCardContent}>{item.content}</Text>
                  <TouchableOpacity
                    style={styles.crisisCallButton}
                    onPress={() => Linking.openURL('tel:988')}
                  >
                    <Text style={styles.crisisCallButtonText}>Call 988 Now</Text>
                  </TouchableOpacity>
                </View>
              );
            }

            return (
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
            );
          }}
          contentContainerStyle={styles.messagesList}
          ListEmptyComponent={
            <Text style={styles.emptyText}>Send a message to start chatting!</Text>
          }
        />
      )}

      {safetyState === "crisis" && (
        <TouchableOpacity
          style={styles.crisisBanner}
          onPress={() => navigation.navigate("CrisisSupport")}
          activeOpacity={0.85}
        >
          <View style={styles.crisisBannerContent}>
            <Text style={styles.crisisBannerEmoji}>💛</Text>
            <View style={styles.crisisBannerTextBlock}>
              <Text style={styles.crisisBannerHeading}>You're not alone</Text>
              <Text style={styles.crisisBannerSubtext}>Tap here for crisis support resources</Text>
            </View>
          </View>
        </TouchableOpacity>
      )}

      {safetyState === "post_crisis" && (
        <TouchableOpacity
          style={styles.postCrisisBanner}
          onPress={() => navigation.navigate("CrisisSupport")}
          activeOpacity={0.85}
        >
          <View style={styles.crisisBannerContent}>
            <Text style={styles.crisisBannerEmoji}>🫂</Text>
            <View style={styles.crisisBannerTextBlock}>
              <Text style={styles.postCrisisBannerHeading}>We're still here if you need us</Text>
              <Text style={styles.postCrisisBannerSubtext}>View support resources →</Text>
            </View>
          </View>
        </TouchableOpacity>
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
    </KeyboardAvoidingView>
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
  // ── Crisis card (replaces regular bubble for crisis responses) ──
  crisisCard: {
    alignSelf: 'stretch',
    marginBottom: 12,
    marginHorizontal: 4,
    backgroundColor: '#FFFDF5',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#FDE68A',
    borderLeftWidth: 4,
    borderLeftColor: Colors.warning,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 3,
  },
  crisisCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
  },
  crisisCardIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  crisisCardTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: '#92400E',
  },
  crisisCardContent: {
    fontSize: 15,
    color: '#78350F',
    lineHeight: 22,
    marginBottom: 16,
  },
  crisisCallButton: {
    backgroundColor: '#F59E0B',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  crisisCallButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  userText: {
    fontSize: 16,
    color: Colors.surface,
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
  // ── Crisis banner (above input) ──
  crisisBanner: {
    backgroundColor: '#FEF3C7',
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderTopWidth: 1,
    borderTopColor: '#FDE68A',
  },
  crisisBannerContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  crisisBannerEmoji: {
    fontSize: 22,
    marginRight: 12,
  },
  crisisBannerTextBlock: {
    flex: 1,
  },
  crisisBannerHeading: {
    fontSize: 15,
    fontWeight: '700',
    color: '#92400E',
    marginBottom: 2,
  },
  crisisBannerSubtext: {
    fontSize: 13,
    color: '#B45309',
  },
  // ── Post-Crisis softer banner ──
  postCrisisBanner: {
    backgroundColor: '#EFF6FF', // Soft blue/cool grey, very calm
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderTopWidth: 1,
    borderTopColor: '#DBEAFE',
  },
  postCrisisBannerHeading: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1E3A8A',
    marginBottom: 2,
  },
  postCrisisBannerSubtext: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#3B82F6',
  },
});
