/**
 * KeySetupModal.tsx
 *
 * WHAT: A first-visit modal that asks the user to enter their own free Groq API key.
 *
 * WHY: This app uses a BYOK (Bring Your Own Key) model so that:
 *   1. Each visitor's usage comes out of THEIR quota, not the developer's.
 *   2. No one can exhaust the Space's shared API key.
 *   3. Visitors stay in control of their own credentials.
 *
 * HOW:
 *   - On mount it checks sessionStorage for an existing key.
 *   - If none found, the modal is shown.
 *   - The key is saved to sessionStorage (auto-deleted when the tab closes).
 *   - A persistent top-banner reminds the visitor that the key is session-only.
 *   - A "Clear Key" button lets them manually wipe it before leaving.
 */

import { useState, useEffect } from "react";
import { saveApiKey, clearApiKey, getStoredApiKey } from "../lib/keyStore";

interface Props {
  onReady: () => void; // Called when key is set or user chooses to continue without one
}

export default function KeySetupModal({ onReady }: Props) {
  const [visible, setVisible] = useState(false);
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const [bannerVisible, setBannerVisible] = useState(false);
  const [keyCleared, setKeyCleared] = useState(false);

  // On first mount: if no key stored, show the modal
  useEffect(() => {
    const stored = getStoredApiKey();
    if (stored) {
      setBannerVisible(true);
      onReady(); // Key already set, skip modal
    } else {
      setVisible(true);
    }
  }, []);

  const handleSave = () => {
    const trimmed = input.trim();
    if (!trimmed.startsWith("gsk_")) {
      setError("That doesn't look like a Groq key. It should start with gsk_…");
      return;
    }
    saveApiKey(trimmed);
    setVisible(false);
    setBannerVisible(true);
    setError("");
    onReady();
  };

  const handleSkip = () => {
    // Continue without a personal key — server's fallback key will be used if available
    setVisible(false);
    onReady();
  };

  const handleClear = () => {
    clearApiKey();
    setBannerVisible(false);
    setKeyCleared(true);
    // Show the modal again so they can re-enter if needed
    setInput("");
    setVisible(true);
  };

  return (
    <>
      {/* ── TOP BANNER ─────────────────────────────────────────────── */}
      {bannerVisible && !keyCleared && (
        <div style={styles.banner}>
          <span style={styles.bannerIcon}>🔑</span>
          <span style={styles.bannerText}>
            Your Groq API key is active — stored in this session only.
            <strong> It will be automatically deleted when you close this tab.</strong>
          </span>
          <button style={styles.clearBtn} onClick={handleClear} title="Remove your key now">
            Clear Key &amp; Leave
          </button>
        </div>
      )}

      {/* ── MODAL OVERLAY ──────────────────────────────────────────── */}
      {visible && (
        <div style={styles.overlay}>
          <div style={styles.modal}>
            {/* Header */}
            <div style={styles.header}>
              <div style={styles.logo}>🌌</div>
              <h2 style={styles.title}>Welcome to Multiverse AI Studio</h2>
              <p style={styles.subtitle}>
                To generate real AI content, please enter your own free&nbsp;
                <a
                  href="https://console.groq.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={styles.link}
                >
                  Groq API key
                </a>
                . It is completely free — no credit card required.
              </p>
            </div>

            {/* Steps */}
            <div style={styles.steps}>
              <div style={styles.step}>
                <span style={styles.stepNum}>1</span>
                <span>
                  Go to{" "}
                  <a href="https://console.groq.com" target="_blank" rel="noopener noreferrer" style={styles.link}>
                    console.groq.com
                  </a>{" "}
                  → Sign up (free) → Create an API Key
                </span>
              </div>
              <div style={styles.step}>
                <span style={styles.stepNum}>2</span>
                <span>Paste your key below (starts with <code style={styles.code}>gsk_</code>)</span>
              </div>
              <div style={styles.step}>
                <span style={styles.stepNum}>3</span>
                <span>
                  When you&apos;re done,{" "}
                  <strong style={{ color: "#f87171" }}>delete your key</strong> using the banner at
                  the top — or just close the tab (keys auto-delete on tab close).
                </span>
              </div>
            </div>

            {/* Input */}
            <div style={styles.inputRow}>
              <input
                style={{ ...styles.input, ...(error ? styles.inputError : {}) }}
                type="password"
                placeholder="gsk_xxxxxxxxxxxxxxxxxxxxxxxx"
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  setError("");
                }}
                onKeyDown={(e) => e.key === "Enter" && handleSave()}
                autoFocus
              />
            </div>
            {error && <p style={styles.errorText}>{error}</p>}

            {/* Privacy note */}
            <p style={styles.privacy}>
              🔒 Your key is stored only in your browser&apos;s <code style={styles.code}>sessionStorage</code>.
              It is <strong>never sent to or stored on our servers</strong> — only included as a
              request header to the AI pipeline.
            </p>

            {/* Actions */}
            <div style={styles.actions}>
              <button style={styles.skipBtn} onClick={handleSkip}>
                Continue without key (demo mode)
              </button>
              <button style={styles.saveBtn} onClick={handleSave}>
                Save Key &amp; Start →
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// ── STYLES ─────────────────────────────────────────────────────────────────────
const styles: Record<string, React.CSSProperties> = {
  overlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.75)",
    backdropFilter: "blur(8px)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 9999,
    padding: "1rem",
  },
  modal: {
    background: "linear-gradient(135deg, #0f0c29, #1a1a3e, #0f0c29)",
    border: "1px solid rgba(139,92,246,0.4)",
    borderRadius: "1.5rem",
    padding: "2.5rem",
    maxWidth: "560px",
    width: "100%",
    boxShadow: "0 25px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(139,92,246,0.15)",
    color: "#e2e8f0",
  },
  header: { textAlign: "center", marginBottom: "1.75rem" },
  logo: { fontSize: "3rem", marginBottom: "0.75rem" },
  title: {
    fontSize: "1.5rem",
    fontWeight: 700,
    background: "linear-gradient(135deg, #a78bfa, #60a5fa)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    margin: "0 0 0.5rem",
  },
  subtitle: { color: "#94a3b8", fontSize: "0.9rem", margin: 0, lineHeight: 1.6 },
  steps: { display: "flex", flexDirection: "column", gap: "0.75rem", marginBottom: "1.5rem" },
  step: {
    display: "flex",
    alignItems: "flex-start",
    gap: "0.75rem",
    background: "rgba(255,255,255,0.04)",
    borderRadius: "0.75rem",
    padding: "0.75rem 1rem",
    fontSize: "0.875rem",
    lineHeight: 1.5,
    color: "#cbd5e1",
  },
  stepNum: {
    background: "linear-gradient(135deg, #7c3aed, #3b82f6)",
    color: "white",
    borderRadius: "50%",
    width: "1.5rem",
    height: "1.5rem",
    minWidth: "1.5rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: 700,
    fontSize: "0.75rem",
  },
  inputRow: { marginBottom: "0.5rem" },
  input: {
    width: "100%",
    padding: "0.875rem 1rem",
    background: "rgba(255,255,255,0.06)",
    border: "1px solid rgba(139,92,246,0.3)",
    borderRadius: "0.75rem",
    color: "#e2e8f0",
    fontSize: "0.9rem",
    outline: "none",
    boxSizing: "border-box",
    transition: "border-color 0.2s",
    fontFamily: "monospace",
  },
  inputError: { borderColor: "#f87171" },
  errorText: { color: "#f87171", fontSize: "0.8rem", margin: "0 0 0.75rem" },
  privacy: {
    background: "rgba(59,130,246,0.1)",
    border: "1px solid rgba(59,130,246,0.2)",
    borderRadius: "0.75rem",
    padding: "0.75rem 1rem",
    fontSize: "0.8rem",
    color: "#93c5fd",
    lineHeight: 1.6,
    margin: "0.75rem 0 1.5rem",
  },
  actions: { display: "flex", gap: "0.75rem", justifyContent: "flex-end" },
  skipBtn: {
    padding: "0.7rem 1.25rem",
    background: "transparent",
    border: "1px solid rgba(255,255,255,0.15)",
    borderRadius: "0.75rem",
    color: "#94a3b8",
    fontSize: "0.85rem",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  saveBtn: {
    padding: "0.7rem 1.5rem",
    background: "linear-gradient(135deg, #7c3aed, #3b82f6)",
    border: "none",
    borderRadius: "0.75rem",
    color: "white",
    fontWeight: 600,
    fontSize: "0.9rem",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  link: { color: "#818cf8", textDecoration: "underline" },
  code: {
    background: "rgba(255,255,255,0.1)",
    borderRadius: "0.25rem",
    padding: "0.1rem 0.3rem",
    fontFamily: "monospace",
    fontSize: "0.85em",
  },
  // Banner at top of page
  banner: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    zIndex: 9998,
    background: "linear-gradient(90deg, rgba(124,58,237,0.9), rgba(59,130,246,0.9))",
    backdropFilter: "blur(8px)",
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    padding: "0.6rem 1.5rem",
    fontSize: "0.8rem",
    color: "white",
    boxShadow: "0 2px 12px rgba(0,0,0,0.3)",
  },
  bannerIcon: { fontSize: "1rem" },
  bannerText: { flex: 1, lineHeight: 1.4 },
  clearBtn: {
    background: "rgba(248,113,113,0.2)",
    border: "1px solid rgba(248,113,113,0.5)",
    borderRadius: "0.5rem",
    color: "#fca5a5",
    padding: "0.3rem 0.75rem",
    cursor: "pointer",
    fontSize: "0.8rem",
    fontWeight: 600,
    whiteSpace: "nowrap",
    transition: "all 0.2s",
  },
};
