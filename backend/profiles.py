"""
profiles.py — Multiverse AI Studio Inference Control Panel
============================================================
WHAT: This file is the single source of truth for HOW each pipeline stage runs.
WHY: Instead of hunting through multiple model files to swap a backend or a model ID,
     you change ONE thing here — the ACTIVE_PROFILE — and the entire pipeline adapts.
HOW: Each profile is a dictionary that maps a pipeline stage to its backend and model.
     Model wrappers import their config from here instead of hardcoding their backends.

=== HOW TO SWITCH PROFILES ===
Set the INFERENCE_PROFILE environment variable in your .env file:

    INFERENCE_PROFILE=gemini_cloud    ← Default. Free, no GPU needed.
    INFERENCE_PROFILE=huggingface     ← Requires HF Inference Provider credits.
    INFERENCE_PROFILE=local_gpu       ← Requires NVIDIA GPU (8GB+ VRAM recommended).
    INFERENCE_PROFILE=mock            ← Instant mock assets. For UI development only.

=== BACKEND OPTIONS PER STAGE ===
    "gemini"       → Google Gemini API (LLM text + image generation). Free quota.
    "hf_inference" → Hugging Face Serverless Inference Providers. Requires HF credits.
    "local"        → Download + run model weights locally via transformers/diffusers.
    "mock"         → Return a procedurally generated placeholder asset instantly.
"""

import os

# ============================================================
# PROFILE DEFINITIONS
# Each profile is a dict: { stage_name: { "backend": ..., "model": ... } }
# ============================================================

PROFILES = {

    # ----------------------------------------------------------
    # PROFILE: groq_cloud (RECOMMENDED — CURRENTLY ACTIVE)
    # ----------------------------------------------------------
    # Uses Groq's free API for ultra-fast LLM prompt expansion (Llama 3.1, 14,400 req/day).
    # Uses Pollinations.ai for image generation — completely free, zero API key required.
    # Depth estimation runs locally on CPU (tiny model, ~100MB).
    # Audio and Video fall back to mock on CPU, real on GPU.
    # ----------------------------------------------------------
    "groq_cloud": {
        "prompt_expansion": {
            "backend": "groq",
            "model": "llama-3.1-8b-instant",   # Fast, free, 8B Llama — great for prompt work
        },
        "image_generation": {
            "backend": "pollinations",           # No API key. Just an HTTP request. Always free.
            "model": None,
        },
        "depth_estimation": {
            "backend": "local",
            "model": "depth-anything/Depth-Anything-V2-Small-hf",
        },
        "audio_generation": {
            "backend": "auto",
            "model": "facebook/musicgen-small",
        },
        "video_generation": {
            "backend": "auto",
            "model": "ali-vilab/i2vgen-xl",
        },
    },

    # ----------------------------------------------------------
    # PROFILE: gemini_cloud
    # ----------------------------------------------------------
    # Uses Google Gemini API for both LLM (prompt expansion) and image generation.
    # COMPLETELY FREE — no HuggingFace credits consumed, no GPU required.
    # Depth estimation runs locally on CPU (it's a tiny model, ~100MB, takes ~3s).
    # Audio and Video fall back to mock on CPU machines (require GPU for real output).
    # NOTE: Requires a Google Cloud project WITHOUT billing enabled (free tier quotas = 1500/day).
    # ----------------------------------------------------------
    "gemini_cloud": {
        "prompt_expansion": {
            "backend": "gemini",
            "model": "gemini-2.0-flash",            # Google's fastest LLM, free tier
        },
        "image_generation": {
            "backend": "gemini",
            # This model supports native image output (no separate Imagen billing)
            "model": "gemini-2.0-flash-preview-image-generation",
        },
        "depth_estimation": {
            "backend": "local",                      # Small model, runs fine on CPU
            "model": "depth-anything/Depth-Anything-V2-Small-hf",
        },
        "audio_generation": {
            "backend": "auto",  # Real on GPU, mock on CPU
            "model": "facebook/musicgen-small",
        },
        "video_generation": {
            "backend": "auto",  # Real on GPU, mock on CPU
            "model": "ali-vilab/i2vgen-xl",
        },
    },

    # ----------------------------------------------------------
    # PROFILE: huggingface
    # ----------------------------------------------------------
    # Uses HuggingFace Inference Providers for LLM + image.
    # Requires your HF account to have active Inference Provider credits.
    # Credits reset monthly. Use this once your credits refresh.
    # ----------------------------------------------------------
    "huggingface": {
        "prompt_expansion": {
            "backend": "hf_inference",
            "model": "Qwen/Qwen2.5-72B-Instruct",
        },
        "image_generation": {
            "backend": "hf_inference",
            "model": "black-forest-labs/FLUX.1-schnell",   # Highest quality cloud image model
        },
        "depth_estimation": {
            "backend": "local",
            "model": "depth-anything/Depth-Anything-V2-Small-hf",
        },
        "audio_generation": {
            "backend": "auto",
            "model": "facebook/musicgen-small",
        },
        "video_generation": {
            "backend": "auto",
            "model": "ali-vilab/i2vgen-xl",
        },
    },

    # ----------------------------------------------------------
    # PROFILE: local_gpu
    # ----------------------------------------------------------
    # Runs EVERY stage locally on your GPU. No cloud calls at all.
    # Requires NVIDIA GPU with enough VRAM:
    #   - prompt_expansion: ~4 GB VRAM (quantized 7B LLM)
    #   - image_generation: ~4 GB VRAM (Stable Diffusion 1.5, smaller than FLUX)
    #   - depth_estimation: ~0.5 GB VRAM
    #   - audio_generation: ~2.3 GB VRAM (MusicGen-Small)
    #   - video_generation: ~5-6 GB VRAM (AnimateDiff + SD1.5)
    # Your RTX 4050 (6GB) can run this with some memory juggling between stages.
    # ----------------------------------------------------------
    "local_gpu": {
        "prompt_expansion": {
            "backend": "local",
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
        },
        "image_generation": {
            "backend": "local",
            "model": "runwayml/stable-diffusion-v1-5",    # 4GB VRAM — fits on RTX 4050
        },
        "depth_estimation": {
            "backend": "local",
            "model": "depth-anything/Depth-Anything-V2-Small-hf",
        },
        "audio_generation": {
            "backend": "local",
            "model": "facebook/musicgen-small",
        },
        "video_generation": {
            "backend": "local",
            "model": "ali-vilab/i2vgen-xl",
        },
    },

    # ----------------------------------------------------------
    # PROFILE: mock
    # ----------------------------------------------------------
    # Bypasses ALL model calls. Instantly returns procedural test assets.
    # Use this when developing the frontend or testing pipeline flow.
    # Zero downloads, zero API calls, zero waiting.
    # ----------------------------------------------------------
    "mock": {
        "prompt_expansion":  {"backend": "mock", "model": None},
        "image_generation":  {"backend": "mock", "model": None},
        "depth_estimation":  {"backend": "mock", "model": None},
        "audio_generation":  {"backend": "mock", "model": None},
        "video_generation":  {"backend": "mock", "model": None},
    },
}

# ============================================================
# ACTIVE PROFILE SELECTION
# Read from environment variable, defaulting to "gemini_cloud"
# ============================================================
ACTIVE_PROFILE_NAME = os.getenv("INFERENCE_PROFILE", "gemini_cloud")

# Guard: If the user sets an unknown profile name, fall back to mock with a warning
if ACTIVE_PROFILE_NAME not in PROFILES:
    print(f"[Config Warning] Unknown INFERENCE_PROFILE='{ACTIVE_PROFILE_NAME}'. Falling back to 'mock'.")
    ACTIVE_PROFILE_NAME = "mock"

# The active profile dict — imported by all model wrappers
ACTIVE_PROFILE = PROFILES[ACTIVE_PROFILE_NAME]

print(f"[Config] Active inference profile: '{ACTIVE_PROFILE_NAME}'")


def get_stage_config(stage_name: str) -> dict:
    """
    WHAT: Returns the backend + model config for a given pipeline stage.
    WHY: Model wrappers call this to know which backend they should use.
    HOW: Looks up the stage in the ACTIVE_PROFILE and returns the config dict.
    """
    config = ACTIVE_PROFILE.get(stage_name)
    if not config:
        print(f"[Config Warning] Stage '{stage_name}' not found in profile '{ACTIVE_PROFILE_NAME}'. Using mock.")
        return {"backend": "mock", "model": None}
    return config
