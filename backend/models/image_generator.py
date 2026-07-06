import gc
import torch
from typing import Dict, Union
from PIL import Image
from huggingface_hub import InferenceClient

# Import our base interface and global configurations
from .base import BaseModel
from ..config import HF_TOKEN, MODEL_IDS, DEVICE, MOCK_INFERENCE

class ImageGenerator(BaseModel):
    """
    Wrapper for the Text-to-Image model.
    Queries Hugging Face Serverless API for cloud-based FLUX generation in production.
    """

    def __init__(self):
        self.client = None
        self.model_id = MODEL_IDS["image_generation"]

    def initialize(self) -> None:
        """
        WHAT: Initializes the Hugging Face InferenceClient.
        WHY: Connects to HF Serverless endpoints using the user's HF_TOKEN.
        HOW: Instantiates InferenceClient with hf-inference provider.
        """
        if MOCK_INFERENCE:
            print("[ImageGenerator] Running in MOCK mode. Bypassing model download & load.")
            return

        if not HF_TOKEN:
            raise ValueError("HF_TOKEN is missing. Cannot initialize ImageGenerator.")
        
        self.client = InferenceClient(token=HF_TOKEN, provider="hf-inference")

    def generate(self, **kwargs) -> Image.Image:
        """
        WHAT: Sends the expanded prompt to Hugging Face Cloud and returns the PIL Image.
        WHY: Performs real image synthesis on HF's high-end cloud GPUs, using 0 VRAM locally.
        HOW: Extracts prompt_data, queries client.text_to_image(), and returns the PIL Image.
        """
        prompt_data: Union[Dict[str, str], str] = kwargs.get("prompt", "")

        if MOCK_INFERENCE:
            print("[ImageGenerator] Generating mock visual scene image...")
            from PIL import ImageDraw
            img = Image.new("RGB", (704, 512), color=(79, 70, 229)) # Indigo base color (matches UI)
            draw = ImageDraw.Draw(img)
            draw.ellipse([277, 181, 427, 331], fill=(225, 29, 72)) # Crimson circle
            draw.text((20, 20), f"Universe: {prompt_data.get('scene_description', 'Mock') if isinstance(prompt_data, dict) else str(prompt_data)[:30]}", fill=(255, 255, 255))
            return img

        if isinstance(prompt_data, dict):
            actual_prompt = prompt_data.get("image_prompt", "")
        else:
            actual_prompt = str(prompt_data)

        if not actual_prompt:
            raise ValueError("ImageGenerator requires a valid 'prompt' in kwargs.")

        try:
            print(f"[ImageGenerator] Calling cloud HF Inference API for model {self.model_id}...")
            # Query FLUX model on HF serverless provider
            pil_image = self.client.text_to_image(actual_prompt, model=self.model_id)
            return pil_image
        except Exception as e:
            raise RuntimeError(f"Cloud Image Generation failed: {str(e)}") from e

    def cleanup(self) -> None:
        """
        No-op since we do not load heavy weights locally in cloud mode.
        """
        pass