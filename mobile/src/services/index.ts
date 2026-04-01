/**
 * Service stubs for API calls to the backend.
 * Will be implemented with real API integration later.
 */

const API_BASE_URL = process.env.API_BASE_URL || "http://localhost:8000";

class ApiService {
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/health`);
      return await response.json();
    } catch (error) {
      console.error("Health check failed:", error);
      throw error;
    }
  }

  // Auth stubs
  async login(email: string, password: string) {
    // TODO: Implement login
    throw new Error("Not implemented");
  }

  async signup(email: string, password: string) {
    // TODO: Implement signup
    throw new Error("Not implemented");
  }

  // Chat stubs
  async sendMessage(conversationId: string, message: string) {
    // TODO: Implement send message
    throw new Error("Not implemented");
  }

  async getConversation(conversationId: string) {
    // TODO: Implement get conversation
    throw new Error("Not implemented");
  }

  // Memory stubs
  async getMemories() {
    // TODO: Implement get memories
    throw new Error("Not implemented");
  }

  // Mood stubs
  async logMood(mood: string, intensity: number) {
    // TODO: Implement log mood
    throw new Error("Not implemented");
  }
}

export const apiService = new ApiService();
