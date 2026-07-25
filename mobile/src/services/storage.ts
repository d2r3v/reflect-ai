/**
 * Cross-platform token storage.
 *
 * expo-secure-store is native-only (iOS/Android keychain); on web its methods
 * are unavailable (`setValueWithKeyAsync is not a function`). This wrapper uses
 * SecureStore on native and falls back to localStorage on web, exposing the
 * same async API so callers don't need platform checks.
 */
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const isWeb = Platform.OS === 'web';

export const storage = {
  async getItemAsync(key: string): Promise<string | null> {
    if (isWeb) {
      try {
        return globalThis.localStorage?.getItem(key) ?? null;
      } catch {
        return null;
      }
    }
    return SecureStore.getItemAsync(key);
  },

  async setItemAsync(key: string, value: string): Promise<void> {
    if (isWeb) {
      try {
        globalThis.localStorage?.setItem(key, value);
      } catch {
        /* storage unavailable (e.g. private mode) — token stays in memory only */
      }
      return;
    }
    await SecureStore.setItemAsync(key, value);
  },

  async deleteItemAsync(key: string): Promise<void> {
    if (isWeb) {
      try {
        globalThis.localStorage?.removeItem(key);
      } catch {
        /* no-op */
      }
      return;
    }
    await SecureStore.deleteItemAsync(key);
  },
};
