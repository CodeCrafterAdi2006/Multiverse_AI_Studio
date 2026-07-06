// API client for Multiverse AI Studio
// The backend uses FastAPI with all routes prefixed with /api to separate backend
// This avoids conflicts with frontend routes (we keep all backend logic under /api namespace
// Detect the hosting URL dynamically. If running in a browser, use the current origin.
// In local dev, this falls back to localhost:8000 if needed (e.g. cross-port calls).
const BACKEND_BASE_URL = typeof window !== "undefined" && window.location.port === "3000"
  ? "http://localhost:8000"
  : (typeof window !== "undefined" ? window.location.origin : "http://localhost:8000");

const API_BASE_URL = `${BACKEND_BASE_URL}/api`;

export interface JobStatus {
  job_id: string;
  status: string;
  stage: string;
}

export interface JobResult {
  job_id: string;
  status: string;
  stage?: string;
  assets?: {
    image?: string;
    depth?: string;
    audio?: string;
    video?: string;
  };
  error?: string;
  error_at?: string;
  scene_description?: string;
}

function fixAssetUrl(assetUrl?: string): string | undefined {
  if (!assetUrl) return undefined;
  // If asset URL is a relative path starting with /, prepend the backend base URL
  if (assetUrl.startsWith("/")) {
    return `${BACKEND_BASE_URL}${assetUrl}`;
  }
  // Otherwise return as is (for absolute URLs)
  return assetUrl;
}

// Import the key store utility so we can attach the visitor's key to every request.
// WHY: The server uses whatever key is in this header first, falling back to its own
// env-var key if no header is present. This means visitors use their own quota.
import { getStoredApiKey } from "./keyStore";

export async function generateAssets(prompt: string): Promise<{ job_id: string }> {
  // Build headers — attach visitor's Groq key if one is stored in their session
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const visitorKey = getStoredApiKey();
  if (visitorKey) {
    // The backend reads this header in routes.py and passes it to the pipeline
    headers["X-Groq-Key"] = visitorKey;
  }

  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: "POST",
    headers,
    body: JSON.stringify({ prompt }),
  });
  if (!response.ok) {
    throw new Error("Failed to start generation");
  }
  return response.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const response = await fetch(`${API_BASE_URL}/status/${jobId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch job status");
  }
  return response.json();
}

export async function getJobResult(jobId: string): Promise<JobResult> {
  const response = await fetch(`${API_BASE_URL}/result/${jobId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch job result");
  }
  const data = await response.json();
  // Fix asset URLs to point to backend static server
  if (data.assets) {
    data.assets = {
      image: fixAssetUrl(data.assets.image),
      depth: fixAssetUrl(data.assets.depth),
      audio: fixAssetUrl(data.assets.audio),
      video: fixAssetUrl(data.assets.video),
    };
  }
  return data;
}

export async function healthCheck(): Promise<{ status: string; timestamp: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error("Health check failed");
  }
  return response.json();
}
