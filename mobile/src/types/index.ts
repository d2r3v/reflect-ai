/**
 * Shared TypeScript types for the app.
 */

export interface User {
  id: string;
  email: string;
  createdAt: string;
}

export interface Message {
  id: string;
  conversationId: string;
  role: "user" | "assistant";
  content: string;
  metadata?: {
    mode?: string;
    riskLevel?: string;
    memoryIds?: string[];
  };
  createdAt: string;
}

export interface Memory {
  id: string;
  category: "recurring_stressor" | "coping_strategy" | "preference";
  content: string;
  extractedAt: string;
  isApproved: boolean;
}

export interface MoodLog {
  id: string;
  mood: string;
  intensity: number;
  loggedAt: string;
}

export interface Conversation {
  id: string;
  userId: string;
  title?: string;
  createdAt: string;
  updatedAt: string;
}
