"""
WHAT: Prompt Expander — Stage 1 of the Multiverse AI pipeline.
WHY: Short user prompts like "a ghost ship" produce mediocre results with image/audio models.
     This stage uses an LLM to expand the prompt into rich, specialized descriptions for
     each downstream stage (image, audio, video).
HOW: Reads its backend from profiles.py (get_stage_config).
     - "gemini"       → Uses Google Gemini API (free tier, no HF credits consumed)
     - "hf_inference" → Uses HuggingFace Inference Provider (requires monthly credits)
     - "mock"         → Returns a procedural expansion instantly (for UI testing)
"""

import json
import re
from typing import Dict

from .base import BaseModel
from ..config import HF_TOKEN, GEMINI_API_KEY, GROQ_API_KEY, MOCK_INFERENCE, get_stage_config

class PromptExpander(BaseModel):
    """
    Wrapper for the LLM that enriches the user's base prompt.
    Returns a dict with tailored prompts for image, audio, video, and a scene description.
    """

    def __init__(self):
        self.client = None
        # Read stage config from the active profile (e.g. gemini_cloud, huggingface, mock)
        self.stage_config = get_stage_config("prompt_expansion")
        self.backend = self.stage_config["backend"]
        self.model_id = self.stage_config["model"]

    def initialize(self) -> None:
        """
        WHAT: Initializes the appropriate client based on the active profile backend.
        WHY: Different backends require different initialization (Gemini SDK vs HF client vs nothing).
        HOW: Reads self.backend and sets up the matching client object.
        """
        # "mock" backend — no initialization needed, generate() will return procedural data
        if MOCK_INFERENCE or self.backend == "mock":
            print("[PromptExpander] Running in MOCK mode. Bypassing client initialization.")
            return

        # "groq" backend — initialize Groq client (OpenAI-compatible SDK)
        if self.backend == "groq":
            if not GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is missing. Cannot initialize Groq PromptExpander.")
            from groq import Groq
            self.client = Groq(api_key=GROQ_API_KEY)
            print(f"[PromptExpander] Initialized Groq client with model: {self.model_id}")
            return

        # "gemini" backend — initialize Google GenAI client
        if self.backend == "gemini":
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is missing. Cannot initialize Gemini PromptExpander.")
            # Import the Google GenAI SDK (google-genai package)
            from google import genai
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            print(f"[PromptExpander] Initialized Gemini client with model: {self.model_id}")
            return

        # "hf_inference" backend — initialize HuggingFace InferenceClient
        if self.backend == "hf_inference":
            if not HF_TOKEN:
                raise ValueError("HF_TOKEN is missing. Cannot initialize HF PromptExpander.")
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(token=HF_TOKEN)
            print(f"[PromptExpander] Initialized HF InferenceClient with model: {self.model_id}")
            return

    def _build_system_message(self) -> str:
        """
        WHAT: Builds the system message that instructs the LLM how to respond.
        WHY: Both Gemini and HF use the same prompt structure, so we extract it into a helper.
        """
        return (
            "You are an expert AI prompt engineer for a multimedia generation pipeline. "
            "The user will give you a short base prompt. Your job is to expand it into highly "
            "detailed, descriptive prompts optimized for different AI models.\n\n"
            "You MUST output exactly and ONLY a valid JSON object with the following keys:\n"
            "- 'image_prompt': A comma-separated list of visual keywords "
            "(e.g., 'masterpiece, 8k, cyberpunk, neon lights, highly detailed').\n"
            "- 'audio_prompt': A description of ambient background music or sound effects "
            "(e.g., 'synthesizer drone, rainy city sounds, low bass').\n"
            "- 'video_prompt': A description of motion or camera movement "
            "(e.g., 'slow pan right, glowing lights flickering').\n"
            "- 'scene_description': A brief 2-sentence narrative description of the overall vibe.\n\n"
            "Do not include markdown blocks, greetings, or any text outside the JSON object."
        )

    def _parse_json_response(self, raw_text: str, base_prompt: str) -> Dict[str, str]:
        """
        WHAT: Robustly extracts a JSON dict from the LLM's raw text output.
        WHY: LLMs sometimes wrap JSON in markdown (```json ... ```) or add conversational text.
             We use a regex to find the first { and last } to extract just the JSON.
        HOW: Parses the cleaned string and fills in missing keys with the base prompt as fallback.
        """
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        clean_json_str = json_match.group(0) if json_match else raw_text
        expanded = json.loads(clean_json_str)
        return {
            "image_prompt": expanded.get("image_prompt", base_prompt),
            "audio_prompt": expanded.get("audio_prompt", base_prompt),
            "video_prompt": expanded.get("video_prompt", base_prompt),
            "scene_description": expanded.get("scene_description", base_prompt),
        }

    def generate(self, **kwargs) -> Dict[str, str]:
        """
        WHAT: Expands the user's short prompt into specialized prompts for each pipeline stage.
        WHY: Each downstream model (image, audio, video) needs a different kind of description.
        HOW: Routes the request to the correct backend based on self.backend.
        """
        base_prompt = kwargs.get("prompt", "")
        if not base_prompt:
            raise ValueError("PromptExpander requires a 'prompt' string in kwargs.")

        # ── MOCK backend ──────────────────────────────────────────────────────
        if MOCK_INFERENCE or self.backend == "mock":
            print(f"[PromptExpander] Mocking prompt expansion for: '{base_prompt}'")
            return {
                "image_prompt": f"masterpiece, highly detailed visual representation of {base_prompt}, rich colors, 8k resolution, cinematic lighting",
                "audio_prompt": f"low ambient background synth drone, subtle sound effects of {base_prompt}, atmospheric soundtrack",
                "video_prompt": f"slow smooth camera pan across {base_prompt}, dynamic lighting shadows moving",
                "scene_description": f"An expanded cinematic scene depicting {base_prompt} with deep atmospheric depth and custom sound design.",
            }

        system_msg = self._build_system_message()
        user_msg = f"Expand this prompt: {base_prompt}"

        # ── GROQ backend ──────────────────────────────────────────────────────
        # WHY: Groq uses the same OpenAI-style chat completions API, making it
        #      a drop-in replacement for any OpenAI-compatible LLM call.
        if self.backend == "groq":
            try:
                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ]
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7,
                )
                raw_text = response.choices[0].message.content.strip()
                return self._parse_json_response(raw_text, base_prompt)
            except Exception as e:
                print(f"[PromptExpander Warning] Groq failed, using fallback. Error: {e}")
                return {"image_prompt": base_prompt, "audio_prompt": base_prompt,
                        "video_prompt": base_prompt, "scene_description": base_prompt}

        # ── GEMINI backend ────────────────────────────────────────────────────
        if self.backend == "gemini":
            try:
                # Gemini uses a combined system+user prompt separated by a newline
                full_prompt = f"{system_msg}\n\n{user_msg}"
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=full_prompt,
                )
                raw_text = response.text.strip()
                return self._parse_json_response(raw_text, base_prompt)
            except Exception as e:
                print(f"[PromptExpander Warning] Gemini failed, using fallback. Error: {e}")
                return {"image_prompt": base_prompt, "audio_prompt": base_prompt,
                        "video_prompt": base_prompt, "scene_description": base_prompt}

        # ── HF_INFERENCE backend ──────────────────────────────────────────────
        if self.backend == "hf_inference":
            try:
                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ]
                response = self.client.chat_completion(
                    model=self.model_id,
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7,
                )
                raw_text = response.choices[0].message.content.strip()
                return self._parse_json_response(raw_text, base_prompt)
            except Exception as e:
                print(f"[PromptExpander Warning] HF Inference failed, using fallback. Error: {e}")
                return {"image_prompt": base_prompt, "audio_prompt": base_prompt,
                        "video_prompt": base_prompt, "scene_description": base_prompt}

        # Unknown backend — safe fallback
        return {"image_prompt": base_prompt, "audio_prompt": base_prompt,
                "video_prompt": base_prompt, "scene_description": base_prompt}

    def cleanup(self) -> None:
        """
        No GPU weights were loaded locally for API-based backends, so cleanup is a no-op.
        """
        pass