"""
WHAT: Image Generator — Stage 2 of the Multiverse AI pipeline.
WHY: Converts the text prompt (from Stage 1) into a high-quality base visual scene.
HOW: Reads its backend from profiles.py (get_stage_config).
     - "gemini"       → Uses Gemini's native image generation (free quota, no HF credits)
     - "hf_inference" → Uses HuggingFace Inference Provider (FLUX.1-schnell, requires credits)
     - "local"        → Loads a diffusion model locally via `diffusers` (requires GPU)
     - "mock"         → Returns a procedurally generated PIL Image instantly
"""

import gc
from io import BytesIO
from typing import Dict, Union

import torch
from PIL import Image

from .base import BaseModel
from ..config import HF_TOKEN, GEMINI_API_KEY, DEVICE, MOCK_INFERENCE, get_stage_config


class ImageGenerator(BaseModel):
    """
    Wrapper for the Text-to-Image model.
    Routes to Gemini, HF Inference, local diffusers, or mock based on the active profile.
    """

    def __init__(self):
        self.client = None
        self.pipeline = None  # Used only by the "local" backend (diffusers)
        self.stage_config = get_stage_config("image_generation")
        self.backend = self.stage_config["backend"]
        self.model_id = self.stage_config["model"]

    def initialize(self) -> None:
        """
        WHAT: Initializes the appropriate image generation client based on the active profile.
        WHY: Gemini, HF, and local diffusers all need different initialization steps.
        HOW: Reads self.backend and sets up the matching client/pipeline object.
        """
        if MOCK_INFERENCE or self.backend == "mock":
            print("[ImageGenerator] Running in MOCK mode. Bypassing model download & load.")
            return

        # ── GEMINI backend ────────────────────────────────────────────────────
        if self.backend == "gemini":
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is missing. Cannot initialize Gemini ImageGenerator.")
            from google import genai
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            print(f"[ImageGenerator] Initialized Gemini client with model: {self.model_id}")
            return

        # ── HF_INFERENCE backend ──────────────────────────────────────────────
        if self.backend == "hf_inference":
            if not HF_TOKEN:
                raise ValueError("HF_TOKEN is missing. Cannot initialize HF ImageGenerator.")
            from huggingface_hub import InferenceClient
            # provider="hf-inference" routes through HF's own serverless tier
            self.client = InferenceClient(token=HF_TOKEN, provider="hf-inference")
            print(f"[ImageGenerator] Initialized HF InferenceClient with model: {self.model_id}")
            return

        # ── LOCAL backend ─────────────────────────────────────────────────────
        if self.backend == "local":
            # Import diffusers only when actually needed (avoids slow import on mock/cloud runs)
            from diffusers import StableDiffusionPipeline
            print(f"[ImageGenerator] Loading local diffusion model: {self.model_id}...")
            # torch_dtype=float16 halves VRAM usage — essential for 6GB GPUs
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            ).to(DEVICE)
            print("[ImageGenerator] Local diffusion pipeline ready.")
            return

    def generate(self, **kwargs) -> Image.Image:
        """
        WHAT: Generates a PIL Image from the expanded prompt.
        WHY: Returns a real or mock image depending on the active backend.
        HOW: Routes to the correct backend generation method.
        """
        prompt_data: Union[Dict[str, str], str] = kwargs.get("prompt", "")

        # Extract the image-specific sub-prompt if a full dict was passed in
        if isinstance(prompt_data, dict):
            actual_prompt = prompt_data.get("image_prompt", "")
        else:
            actual_prompt = str(prompt_data)

        # ── MOCK backend ──────────────────────────────────────────────────────
        if MOCK_INFERENCE or self.backend == "mock":
            print("[ImageGenerator] Generating mock visual scene image...")
            from PIL import ImageDraw
            img = Image.new("RGB", (704, 512), color=(79, 70, 229))
            draw = ImageDraw.Draw(img)
            draw.ellipse([277, 181, 427, 331], fill=(225, 29, 72))
            label = actual_prompt[:40] if actual_prompt else "Mock Scene"
            draw.text((20, 20), f"Scene: {label}", fill=(255, 255, 255))
            return img

        if not actual_prompt:
            raise ValueError("ImageGenerator requires a valid 'prompt' in kwargs.")

        # ── GEMINI backend ────────────────────────────────────────────────────
        if self.backend == "gemini":
            try:
                print(f"[ImageGenerator] Calling Gemini image generation model: {self.model_id}...")
                from google.genai import types
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=actual_prompt,
                    config=types.GenerateContentConfig(
                        # Request both text AND image in the response
                        response_modalities=["TEXT", "IMAGE"],
                    ),
                )
                # Gemini returns parts — find the first IMAGE part
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        # inline_data.data is raw image bytes — wrap in PIL
                        return Image.open(BytesIO(part.inline_data.data)).convert("RGB")
                raise RuntimeError("Gemini returned no image in its response parts.")
            except Exception as e:
                raise RuntimeError(f"Gemini Image Generation failed: {e}") from e

        # ── HF_INFERENCE backend ──────────────────────────────────────────────
        if self.backend == "hf_inference":
            try:
                print(f"[ImageGenerator] Calling HF Inference API for model: {self.model_id}...")
                pil_image = self.client.text_to_image(actual_prompt, model=self.model_id)
                return pil_image
            except Exception as e:
                raise RuntimeError(f"HF Cloud Image Generation failed: {e}") from e

        # ── LOCAL backend ─────────────────────────────────────────────────────
        if self.backend == "local":
            try:
                print(f"[ImageGenerator] Running local diffusion inference on {DEVICE}...")
                with torch.inference_mode():
                    result = self.pipeline(actual_prompt, num_inference_steps=25)
                return result.images[0]
            except Exception as e:
                raise RuntimeError(f"Local Image Generation failed: {e}") from e

        raise RuntimeError(f"Unknown backend '{self.backend}' for ImageGenerator.")

    def cleanup(self) -> None:
        """
        WHAT: Releases GPU VRAM after inference completes.
        WHY: The local diffusion pipeline holds ~4GB of VRAM. Releasing it after Stage 2
             allows Stage 4 (MusicGen) and Stage 5 (Video) to load without OOM errors.
        HOW: Deletes the pipeline reference and calls gc.collect() + torch.cuda.empty_cache().
        """
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print("[ImageGenerator] Released local pipeline from VRAM.")