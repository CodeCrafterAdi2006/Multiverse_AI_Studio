/**
 * KeySetupModal.tsx
 *
 * WHAT: A first-visit chooser that asks the visitor how they want to use Multiverse AI Studio.
 *
 * WHY: Visitors arrive with different needs:
 *   1. Some want to run the FULL local pipeline on their own GPU (no cloud, no keys).
 *   2. Some want to use the free Groq cloud LLM (BYOK — their quota, not the server's).
 *   3. Some just want to see the demo right away (no key → real Pollinations images + local
 *      depth + mock audio/video, served by the Space's default groq_cloud profile).
 *
 * HOW:
 *   - On mount it checks sessionStorage for an existing key. If found, skip straight to the app.
 *   - Otherwise it shows three choice cards. Selecting one reveals a contextual panel:
 *       • "Run locally" → informational setup steps (the heavy models run on THEIR machine).
 *       • "Use Groq"    → the existing key input (validated as gsk_…) or a demo skip.
 *       • "Just demo"   → proceeds immediately.
 *   - The chosen Groq key is stored in sessionStorage and sent by the API client as a header.
 *   - A persistent top-banner reminds the visitor that an active key is session-only.
 */

import React, { useState, useEffect } from "react";
import { saveApiKey, clearApiKey, getStoredApiKey } from "../lib/keyStore";

interface Props {
  onReady: () => void; // Called when the visitor is ready to use the Studio
}

type Mode = "local" | "groq" | "demo" | null;

const LOCAL_STEPS: { title: string; detail: string }[] = [
  { title: "Requirements", detail: "Python 3.10+, an NVIDIA GPU (≈8GB+ VRAM). CPU-only is impractical for video/audio." },
  { title: "Install CUDA PyTorch", detail: "pip install torch --index-url https://download.pytorch.org/whl/cu121" },
  { title: "Install dependencies", detail: "pip install -r backend/requirements.txt" },
  { title: "Select local models", detail: "Set INFERENCE_PROFILE=local_gpu (depth runs on CPU; image/audio on GPU; video needs more VRAM)." },
  { title: "Run the server", detail: "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000" },
];

export default function KeySetupModal({ onReady }: Props) {
  const [visible, setVisible] = useState(false);
  const [mode, setMode] = useState<Mode>(null);
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const [bannerVisible, setBannerVisible] = useState(false);
  const [keyCleared, setKeyCleared] = useState(false);

  // On first mount: if a key is already stored, skip the modal entirely.
  useEffect(() => {
    const stored = getStoredApiKey();
    if (stored) {
      setBannerVisible(true);
      onReady();
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
    // Continue without a personal key — the Space's default profile serves the demo.
    setVisible(false);
    onReady();
  };

  const handleClear = () => {
    clearApiKey();
    setBannerVisible(false);
    setKeyCleared(true);
    setInput("");
    setMode(null);
    setVisible(true);
  };

  const choose = (m: Mode) => setMode(m);

  return (
    <>
      {/* ── TOP BANNER (only when a visitor key is active) ─────────────────── */}
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

      {/* ── MODAL OVERLAY ──────────────────────────────────────────────────── */}
      {visible && (
        <div style={styles.overlay}>
          <div style={styles.modal}>
            <div style={styles.header}>
              <div style={styles.logo}>🌌</div>
              <h2 style={styles.title}>Welcome to Multiverse AI Studio</h2>
              <p style={styles.subtitle}>
                How would you like to use the Studio? You can run the full pipeline on your own
                GPU, use the free Groq cloud LLM, or just explore the demo.
              </p>
            </div>

            {/* Three choice cards */}
            <div style={styles.cards}>
              <button
                style={{ ...styles.card, ...(mode === "local" ? styles.cardActive : {}) }}
                onClick={() => choose("local")}
              >
                <span style={styles.cardIcon}>🖥️</span>
                <span style={styles.cardTitle}>Run locally</span>
                <span style={styles.cardDesc}>Full models on your own GPU — no cloud, no keys.</span>
              </button>

              <button
                style={{ ...styles.card, ...(mode === "groq" ? styles.cardActive : {}) }}
                onClick={() => choose("groq")}
              >
                <span style={styles.cardIcon}>☁️</span>
                <span style={styles.cardTitle}>Use Groq</span>
                <span style={styles.cardDesc}>Free cloud LLM. Bring your own key (BYOK).</span>
              </button>

              <button
                style={{ ...styles.card, ...(mode === "demo" ? styles.cardActive : {}) }}
                onClick={() => choose("demo")}
              >
                <span style={styles.cardIcon}>▶️</span>
                <span style={styles.cardTitle}>Just demo</span>
                <span style={styles.cardDesc}>No key needed — real images + mock audio/video.</span>
              </button>
            </div>

            {/* ── LOCAL PANEL ───────────────────────────────────────────────── */}
            {mode === "local" && (
              <div style={styles.localPanel}>
                <p style={styles.localIntro}>
                  The heavy models run on <strong>your</strong> machine, not this Space. Follow the
                  steps below, then open the app on your computer. See the README section{" "}
                  <em>“Run locally (full models)”</em> for the complete guide.
                </p>
                <ol style={styles.localList}>
                  {LOCAL_STEPS.map((s, i) => (
                    <li key={i} style={styles.localItem}>
                      <span style={styles.localItemTitle}>{s.title}</span>
                      <span style={styles.localItemDetail}>{s.detail}</span>
                    </li>
                  ))}
                </ol>
                <p style={styles.localNote}>
                  Tip: models download once and cache locally, so subsequent runs work offline.
                </p>
              </div>
            )}

            {/* ── GROQ PANEL ────────────────────────────────────────────────── */}
            {mode === "groq" && (
              <>
                <div style={styles.steps}>
                  <div style={styles.step}>
                    <span style={styles.stepNum}>1</span>
                    <span>
                      Get a free key at{" "}
                      <a href="https://console.groq.com" target="_blank" rel="noopener noreferrer" style={styles.link}>
                        console.groq.com
                      </a>{" "}
                      (no credit card).
                    </span>
                  </div>
                  <div style={styles.step}>
                    <span style={styles.stepNum}>2</span>
                    <span>
                      Paste it below (starts with <code style={styles.code}>gsk_</code>). Your key is
                      used only for this session.
                    </span>
                  </div>
                </div>

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

                <p style={styles.privacy}>
                  🔒 Your key is stored only in your browser&apos;s <code style={styles.code}>sessionStorage</code>.
                  It is <strong>never sent to or stored on our servers</strong> — only included as a
                  request header to the AI pipeline.
                </p>
              </>
            )}

            {/* ── DEMO PANEL ────────────────────────────────────────────────── */}
            {mode === "demo" && (
              <div style={styles.demoPanel}>
                <p style={styles.demoText}>
                  No setup required. The Studio will generate <strong>real images</strong> (via
                  Pollinations) and <strong>real depth maps</strong> locally, with procedural
                  audio/video — no API key needed.
                </p>
              </div>
            )}

            {/* ── ACTIONS ───────────────────────────────────────────────────── */}
            {mode === "groq" && (
              <div style={styles.actions}>
                <button style={styles.skipBtn} onClick={handleSkip}>
                  Continue without key (demo)
                </button>
                <button style={styles.saveBtn} onClick={handleSave}>
                  Save Key &amp; Start →
                </button>
              </div>
            )}
            {mode === "demo" && (
              <div style={styles.actions}>
                <button style={styles.saveBtn} onClick={handleSkip}>
                  Start demo →
                </button>
              </div>
            )}
            {mode === "local" && (
              <div style={styles.actions}>
                <button style={styles.skipBtn} onClick={() => choose(null)}>
                  Back
                </button>
                <button style={styles.skipBtn} onClick={handleSkip}>
                  Use the demo instead →
                </button>
              </div>
            )}
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
    maxWidth: "640px",
    width: "100%",
    maxHeight: "90vh",
    overflowY: "auto",
    boxShadow: "0 25px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(139,92,246,0.15)",
    color: "#e2e8f0",
  },
  header: { textAlign: "center", marginBottom: "1.5rem" },
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

  cards: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "0.75rem",
    marginBottom: "1.5rem",
  },
  card: {
    display: "flex",
    flexDirection: "column",
    gap: "0.4rem",
    textAlign: "left",
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: "1rem",
    padding: "1rem",
    cursor: "pointer",
    color: "#e2e8f0",
    transition: "all 0.2s",
  },
  cardActive: {
    borderColor: "#8b5cf6",
    background: "rgba(139,92,246,0.12)",
    boxShadow: "0 0 0 1px rgba(139,92,246,0.4)",
  },
  cardIcon: { fontSize: "1.5rem" },
  cardTitle: { fontWeight: 700, fontSize: "0.95rem" },
  cardDesc: { fontSize: "0.78rem", color: "#94a3b8", lineHeight: 1.4 },

  localPanel: {
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: "1rem",
    padding: "1.25rem",
    marginBottom: "1rem",
  },
  localIntro: { fontSize: "0.85rem", color: "#cbd5e1", lineHeight: 1.6, margin: "0 0 1rem" },
  localList: { margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: "0.75rem" },
  localItem: { display: "flex", flexDirection: "column", gap: "0.2rem" },
  localItemTitle: { fontWeight: 600, fontSize: "0.85rem", color: "#c4b5fd" },
  localItemDetail: {
    fontSize: "0.8rem",
    color: "#94a3b8",
    fontFamily: "monospace",
    background: "rgba(0,0,0,0.3)",
    borderRadius: "0.5rem",
    padding: "0.4rem 0.6rem",
    lineHeight: 1.4,
    wordBreak: "break-word",
  },
  localNote: { fontSize: "0.78rem", color: "#64748b", marginTop: "1rem", marginBottom: 0 },

  steps: { display: "flex", flexDirection: "column", gap: "0.75rem", marginBottom: "1.25rem" },
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
  demoPanel: {
    background: "rgba(16,185,129,0.08)",
    border: "1px solid rgba(16,185,129,0.25)",
    borderRadius: "1rem",
    padding: "1.25rem",
    marginBottom: "1rem",
  },
  demoText: { fontSize: "0.85rem", color: "#a7f3d0", lineHeight: 1.6, margin: 0 },

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
