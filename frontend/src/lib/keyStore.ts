/**
 * keyStore.ts
 *
 * WHAT: A tiny utility module that manages the visitor's Groq API key in sessionStorage.
 *
 * WHY: We centralise all key read/write operations here so that:
 *   1. No other file reaches into sessionStorage directly (single responsibility).
 *   2. If we ever change the storage mechanism, we only update this file.
 *
 * HOW sessionStorage vs localStorage:
 *   - localStorage persists FOREVER across tabs and browser restarts.
 *   - sessionStorage is scoped to ONE TAB and is automatically wiped when that
 *     tab is closed. This is exactly what we want for temporary API keys.
 */

const SESSION_KEY = "multiverse_groq_key";

/** Save the visitor's Groq API key to their browser's sessionStorage. */
export function saveApiKey(key: string): void {
  sessionStorage.setItem(SESSION_KEY, key);
}

/**
 * Retrieve the stored Groq API key, or null if not set.
 * This is called by the API client before every request.
 */
export function getStoredApiKey(): string | null {
  return sessionStorage.getItem(SESSION_KEY);
}

/**
 * Remove the key from sessionStorage immediately.
 * Called when the user clicks "Clear Key & Leave".
 * Note: sessionStorage also clears automatically on tab close,
 * so this is just for users who want to be extra careful.
 */
export function clearApiKey(): void {
  sessionStorage.removeItem(SESSION_KEY);
}
