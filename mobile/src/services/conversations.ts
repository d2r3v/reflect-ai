import { api } from "./api";

export interface Message {
    id: string;
    role: "user" | "assistant" | "system";
    content: string;
    created_at: string;
}

export interface Conversation {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
}

export interface ConversationDetail extends Conversation {
    messages: Message[];
}

export interface SendMessageResponse {
    messages: Message[];
    response_mode: string;
    safety_state: "normal" | "crisis" | "post_crisis";
    title: string;
}

export const conversationsService = {
    /**
     * Create a new conversation
     * @param title Optional title
     */
    createConversation: async (title?: string): Promise<Conversation> => {
        return api.authPost("/conversations", { title });
    },

    /**
     * List all conversations for the authenticated user
     */
    listConversations: async (): Promise<Conversation[]> => {
        return api.authGet("/conversations");
    },

    /**
     * Get a conversation and its messages
     * @param id Conversation ID
     */
    getConversation: async (id: string): Promise<ConversationDetail> => {
        return api.authGet(`/conversations/${id}`);
    },

    /**
     * Send a message in a conversation. Returns the user message and the assistant reply.
     * @param id Conversation ID
     * @param content Message text
     */
    sendMessage: async (id: string, content: string): Promise<SendMessageResponse> => {
        return api.authPost(`/conversations/${id}/messages`, { content });
    },
};
