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
from ..config import HF_TOKEN, GEMINI_API_KEY, GROQ_API_KEY, MOCK_INFERENCE, DEVICE, get_stage_config
import torch

class PromptExpander(BaseModel):
    """
    Wrapper for the LLM that enriches the user's base prompt.
    Returns a dict with tailored prompts for image, audio, video, and a scene description.
    """

    def __init__(self):
        self.client = None
        self.pipe = None
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
                print("[PromptExpander] GROQ_API_KEY missing — will use local template expansion fallback.")
                return
            from groq import Groq
            self.client = Groq(api_key=GROQ_API_KEY)
            print(f"[PromptExpander] Initialized Groq client with model: {self.model_id}")
            return

        # "gemini" backend — initialize Google GenAI client
        if self.backend == "gemini":
            if not GEMINI_API_KEY:
                print("[PromptExpander] GEMINI_API_KEY missing — will use local template expansion fallback.")
                return
            # Import the Google GenAI SDK (google-genai package)
            from google import genai
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            print(f"[PromptExpander] Initialized Gemini client with model: {self.model_id}")
            return

        # "hf_inference" backend — initialize HuggingFace InferenceClient
        if self.backend == "hf_inference":
            if not HF_TOKEN:
                print("[PromptExpander] HF_TOKEN missing — will use local template expansion fallback.")
                return
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(token=HF_TOKEN)
            print(f"[PromptExpander] Initialized HF InferenceClient with model: {self.model_id}")
            return

        # "local" backend — load a text-generation pipeline on this machine (no cloud).
        if self.backend == "local":
            try:
                from transformers import pipeline as hf_pipeline
                torch_dtype = torch.float16 if DEVICE == "cuda" else torch.float32
                self.pipe = hf_pipeline(
                    "text-generation",
                    model=self.model_id,
                    device=DEVICE,
                    torch_dtype=torch_dtype,
                )
                print(f"[PromptExpander] Loaded local LLM pipeline: {self.model_id}")
            except Exception as e:
                print(f"[PromptExpander Warning] Failed to load local LLM ({e}). Falling back to template expansion.")
                self.pipe = None
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

        # WHAT: Accept a per-request Groq key override from the visitor.
        # WHY: If the visitor supplied their own key via the frontend modal, we use it
        #      so that their quota is consumed, not the server's.
        # HOW: If present, we temporarily reassign self.client to use this key for this call.
        runtime_groq_key = kwargs.get("groq_key")
        if runtime_groq_key and self.backend == "groq":
            from groq import Groq
            # Create a one-off client with the visitor's key for this request only
            groq_client = Groq(api_key=runtime_groq_key)
        else:
            groq_client = self.client  # Fall back to the server's pre-initialized client

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

        # Graceful degradation: if no working client is available for a cloud LLM backend,
        # fall back to a deterministic local expansion so the demo never breaks.
        if self.backend == "groq" and groq_client is None:
            return self._local_expand(base_prompt)
        if self.backend in ("gemini", "hf_inference") and self.client is None:
            return self._local_expand(base_prompt)

        # ── GROQ backend ──────────────────────────────────────────────────────
        # WHY: Groq uses the same OpenAI-style chat completions API, making it
        #      a drop-in replacement for any OpenAI-compatible LLM call.
        if self.backend == "groq":
            try:
                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ]
                # Use groq_client — either the visitor's key or the server's fallback
                response = groq_client.chat.completions.create(
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

        # ── LOCAL backend ─────────────────────────────────────────────────────
        # WHY: Runs a local causal-LM text-generation pipeline (e.g. Mistral-7B) with no cloud.
        # HOW: Builds the same system+user prompt, generates tokens, and parses the JSON.
        if self.backend == "local":
            if self.pipe is None:
                return self._local_expand(base_prompt)
            try:
                full_prompt = f"{system_msg}\n\n{user_msg}"
                output = self.pipe(
                    full_prompt,
                    max_new_tokens=512,
                    temperature=0.7,
                    do_sample=True,
                    return_full_text=False,
                )
                raw_text = output[0]["generated_text"].strip()
                return self._parse_json_response(raw_text, base_prompt)
            except Exception as e:
                print(f"[PromptExpander Warning] Local LLM failed, using fallback. Error: {e}")
                return {"image_prompt": base_prompt, "audio_prompt": base_prompt,
                        "video_prompt": base_prompt, "scene_description": base_prompt}

        # Unknown backend — safe fallback
        return {"image_prompt": base_prompt, "audio_prompt": base_prompt,
                "video_prompt": base_prompt, "scene_description": base_prompt}

    def _local_expand(self, base_prompt: str) -> Dict[str, str]:
        """
        WHAT: A deterministic, offline expansion used when no cloud LLM key is available.
        WHY: Keeps the demo fully functional (zero API keys) while still enriching the
              prompt with structured, model-friendly descriptions for each stage.
        HOW: Builds tailored strings from the user's base prompt with no network calls.
        """
        theme = base_prompt.strip().rstrip(".") or "a mysterious abstract scene"
        return {
            "image_prompt": (
                f"masterpiece, highly detailed cinematic visual of {theme}, "
                f"rich volumetric lighting, 8k resolution, intricate details, dramatic atmosphere"
            ),
            "audio_prompt": f"ambient atmospheric soundscape evoking {theme}, subtle drone, soft textures",
            "video_prompt": f"slow cinematic camera drift across {theme}, gentle parallax, shifting light",
            "scene_description": (
                f"A cinematic, atmospheric interpretation of '{theme}' with rich detail, "
                f"depth, and a matching ambient soundscape."
            ),
        }

    def cleanup(self) -> None:
        """
        WHAT: Releases the local LLM pipeline and frees GPU memory when running the "local" backend.
        WHY: A local 7B model holds several GB of VRAM; the orchestrator unloads each stage after use.
        HOW: Deletes the pipeline reference and flushes the CUDA cache if a local model was loaded.
        """
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()