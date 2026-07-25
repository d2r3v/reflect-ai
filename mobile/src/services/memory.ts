import { api } from "./api";

/**
 * A single insight the AI has learned about the user, as returned by
 * GET /api/v1/memories.
 */
export interface Memory {
    id: string;
    category: string; // coping_strategy | recurring_stressor | preference
    content: string;
    created_at: string;
}

export const memoryService = {
    /**
     * Fetch all insights the AI has stored for the authenticated user,
     * newest first.
     */
    listMemories: async (): Promise<Memory[]> => {
        return api.authGet("/memories");
    },
};
