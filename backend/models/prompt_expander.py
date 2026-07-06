# prompt_expander.py placeholder
"""
WHAT: This module defines the Prompt Expander, the first stage of the Multiverse AI pipeline.
WHY: Users often provide short, simple prompts (e.g., "a futuristic city"). Text-to-image and 
     text-to-audio models require highly descriptive, comma-separated keywords to produce high-quality 
     results. We use an LLM (Mistral) to "expand" the short prompt into specialized prompts tailored 
     for each downstream model.
HOW: It implements the `BaseModel` interface. Instead of loading a massive LLM locally (which 
     would consume 14GB+ of VRAM), it utilizes the Hugging Face Serverless Inference API via 
     `huggingface_hub`. It forces the LLM to output a structured JSON dictionary.
"""

import json
import re
from typing import Dict, Any

# Import the official Hugging Face Python client
from huggingface_hub import InferenceClient

# Import our base interface and global configuration
from .base import BaseModel
from ..config import HF_TOKEN, MODEL_IDS, MOCK_INFERENCE

class PromptExpander(BaseModel):
    """
    Wrapper for the LLM that enriches the user's base prompt.
    Expected to return a dictionary containing tailored prompts for image, audio, and video.
    """

    def __init__(self):
        self.client = None
        self.model_id = MODEL_IDS["prompt_expansion"]

    def initialize(self) -> None:
        """
        WHAT: Initializes the connection to the Hugging Face Inference API.
        WHY: We need an authenticated client to communicate with the remote Mistral model.
        HOW: Instantiates `InferenceClient` using the token loaded from `config.py`.
        """
        if MOCK_INFERENCE:
            print("[PromptExpander] Running in MOCK mode. Bypassing client initialization.")
            return

        if not HF_TOKEN:
            raise ValueError("HF_TOKEN is missing. Cannot initialize PromptExpander.")
        
        # We don't load heavy weights locally; we just setup a lightweight HTTP client.
        self.client = InferenceClient(token=HF_TOKEN)

    def generate(self, **kwargs) -> Dict[str, str]:
        """
        WHAT: Sends the short user prompt to the LLM and asks for a structured JSON response.
        WHY: The downstream models (Image Generator, Audio Generator, Video Generator) all need 
             slightly different textual inputs to perform optimally.
        HOW: Constructs a system message with strict JSON output instructions, calls the chat API, 
             extracts the JSON payload from the response string, and returns it as a Python dict.
        """
        # Extract the user prompt from kwargs
        base_prompt = kwargs.get("prompt", "")
        if not base_prompt:
            raise ValueError("PromptExpander requires a 'prompt' string in kwargs.")

        if MOCK_INFERENCE:
            print(f"[PromptExpander] Mocking prompt expansion for: '{base_prompt}'")
            return {
                "image_prompt": f"masterpiece, highly detailed visual representation of {base_prompt}, rich colors, 8k resolution, cinematic lighting",
                "audio_prompt": f"low ambient background synth drone, subtle sound effects of {base_prompt}, atmospheric soundtrack",
                "video_prompt": f"slow smooth camera pan across {base_prompt}, dynamic lighting shadows moving",
                "scene_description": f"An expanded cinematic scene depicting {base_prompt} with deep atmospheric depth and custom sound design."
            }


        # Craft the system message instructing the LLM on exactly how to behave.
        system_message = (
            "You are an expert AI prompt engineer for a multimedia generation pipeline. "
            "The user will give you a short base prompt. Your job is to expand it into highly "
            "detailed, descriptive prompts optimized for different AI models.\n\n"
            "You MUST output exactly and ONLY a valid JSON object with the following keys:\n"
            "- 'image_prompt': A comma-separated list of visual keywords (e.g., 'masterpiece, 8k, cyberpunk, neon lights, highly detailed').\n"
            "- 'audio_prompt': A description of ambient background music or sound effects (e.g., 'synthesizer drone, rainy city sounds, low bass').\n"
            "- 'video_prompt': A description of motion or camera movement (e.g., 'slow pan right, glowing lights flickering').\n"
            "- 'scene_description': A brief 2-sentence narrative description of the overall vibe.\n\n"
            "Do not include markdown blocks, greetings, or any text outside the JSON object."
        )

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Expand this prompt: {base_prompt}"}
        ]

        try:
            # Call the Hugging Face API to generate the response
            response = self.client.chat_completion(
                model=self.model_id,
                messages=messages,
                max_tokens=500,
                temperature=0.7 # Add slight creativity
            )
            
            # Extract the raw text from the LLM's response
            raw_text = response.choices[0].message.content.strip()

            # Robust JSON extraction: Sometimes LLMs wrap JSON in markdown (e.g., ```json ... ```)
            # We use a regex to find the first '{' and last '}' to strip away unwanted conversational text.
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match:
                clean_json_str = json_match.group(0)
            else:
                clean_json_str = raw_text

            # Parse the string into a Python dictionary
            expanded_dict = json.loads(clean_json_str)

            # Ensure all required keys exist, fallback to the base prompt if missing
            return {
                "image_prompt": expanded_dict.get("image_prompt", base_prompt),
                "audio_prompt": expanded_dict.get("audio_prompt", base_prompt),
                "video_prompt": expanded_dict.get("video_prompt", base_prompt),
                "scene_description": expanded_dict.get("scene_description", base_prompt)
            }

        except Exception as e:
            # FALLBACK MECHANISM
            # If the API fails, times out, or returns invalid JSON, we do not want the 
            # whole pipeline to crash. We gracefully fall back to using the user's original 
            # prompt for all stages.
            print(f"[PromptExpander Warning] Failed to expand prompt, using fallback. Error: {str(e)}")
            return {
                "image_prompt": base_prompt,
                "audio_prompt": base_prompt,
                "video_prompt": base_prompt,
                "scene_description": base_prompt
            }

    def cleanup(self) -> None:
        """
        WHAT: Cleans up model resources.
        WHY: To satisfy the BaseModel interface contract.
        HOW: Since this is an API-based model (cloud inference), no heavy PyTorch models 
             were loaded into local GPU VRAM. Therefore, this method is simply a no-op (does nothing).
        """
        pass