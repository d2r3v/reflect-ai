/**
 * Navigation type definitions for type-safe navigation.
 * Each navigator has its own param list defined here.
 */

export type RootStackParamList = {
  Splash: undefined;
  Auth: undefined;
  App: undefined;
};

export type AuthStackParamList = {
  Login: undefined;
  Signup: undefined;
};

export type AppStackParamList = {
  Home: undefined;
  Chat: { conversationId?: string };
  MoodCheckin: undefined;
  MemoryInspector: undefined;
  CrisisSupport: undefined;
};
