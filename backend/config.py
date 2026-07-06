# Config file placeholder
"""
WHAT: Global configuration file for the Multiverse AI Studio backend.
WHY: Centralizing settings (tokens, model IDs, file paths, hardware configs) makes the app 
     easier to maintain and deploy. If we want to upgrade a model or change the output directory, 
     we only have to change it here.
HOW: We use Python's `os` module to read environment variables for sensitive data (HF_TOKEN) 
     and `torch` to dynamically detect hardware capabilities.
"""

import os
import torch

# WHAT: The Hugging Face API token required to download gated models or use specific HF services.
# WHY: Hardcoding tokens is a security risk. Loading from the environment ensures secrets stay safe.
# HOW: Set this in your environment or a .env file before running the server (e.g., export HF_TOKEN="hf_...").
HF_TOKEN = os.getenv("HF_TOKEN")

# WHAT: Toggle to run the pipeline using lightweight mock generators instead of heavy PyTorch models.
# WHY: Downloading 20GB+ of weights and running inference requires a high-end GPU.
#      Setting this to True allows instant testing of the server and frontend on any laptop.
# HOW: Read from the environment variable 'MOCK_INFERENCE' (as a string like 'True'/'False'), 
#      defaulting to 'True' for easier out-of-the-box local development.
MOCK_INFERENCE = os.getenv("MOCK_INFERENCE", "True").lower() in ("true", "1", "t")

# WHAT: Toggle to force CPU execution of heavy Hugging Face models (MusicGen & i2vgen-xl) when MOCK_INFERENCE is False.
# WHY: By default, when running on a CPU-only machine with MOCK_INFERENCE=False, the backend
#      automatically bypasses loading these models locally to prevent system RAM exhaustion.
#      Setting this to True overrides this safety guard and forces the CPU to execute them.
# HOW: Read from the environment variable 'FORCE_CPU_INFERENCE', defaulting to 'False'.
FORCE_CPU_INFERENCE = os.getenv("FORCE_CPU_INFERENCE", "False").lower() in ("true", "1", "t")


# WHAT: A dictionary mapping pipeline stage names to specific Hugging Face model repositories.
# WHY: Keeping model IDs centralized prevents hardcoding strings across multiple files. 
#      It allows quick model swapping (e.g., upgrading to a newer Stable Diffusion version).
# HOW: These strings will be imported by their respective model wrappers in backend/models/.
MODEL_IDS = {
    # Expands a short user prompt into a detailed, descriptive prompt for better image generation.
    "prompt_expansion": "Qwen/Qwen2.5-72B-Instruct",
    
    # Generates the foundational visual scene based on the expanded prompt.
    "image_generation": "black-forest-labs/FLUX.1-schnell",
    
    # Analyzes the generated image to create a depth map, adding 3D context for video generation.
    "depth_estimation": "depth-anything/Depth-Anything-V2-Small-hf",
    
    # Generates an ambient audio track or sound effects based on the text prompt.
    "audio_generation": "facebook/musicgen-small",
    
    # Synthesizes the final video using the image, depth map, and temporal dynamics.
    "video_generation": "ali-vilab/i2vgen-xl"
}

# WHAT: Defines the hardware accelerator to use for model inference.
# WHY: Models run significantly faster on a GPU. We need to detect if a GPU is available, 
#      and if not, gracefully fall back to CPU so the app doesn't crash on standard machines.
# HOW: Uses PyTorch's `cuda.is_available()` check. All model wrappers will use this variable
#      to move their models to the correct device (e.g., `model.to(DEVICE)`).
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# WHAT: The directory path where all generated assets (images, depth maps, audio, video) will be saved.
# WHY: We need a dedicated location on the filesystem to store the outputs so the FastAPI server 
#      can serve them back to the frontend as static files.
# HOW: The file_manager.py utility will read this path, ensure the directory exists, and write files here.
OUTPUT_DIR = "generated_assets/"