# video_generator.py placeholder
"""
WHAT: This module defines the Video Generator, the fifth and final stage of our AI pipeline.
WHY: This stage pulls together the visual foundation (image) and animating prompt to synthesize 
     a dynamic, moving scene. It turns static media into a living cinematic experience.
HOW: It implements the `BaseModel` interface. It loads Alibaba's `i2vgen-xl` Image-to-Video 
     pipeline using Hugging Face's `diffusers` library. It processes the source image and prompt, 
     generates a sequential list of video frames, compiles them into a standard MP4 byte stream, 
     and unloads itself completely to free the GPU.
"""

import gc
import os
import tempfile
import numpy as np
import torch
from typing import Dict, Union, List
from PIL import Image

# Import the Image-to-Video pipeline from Diffusers
from diffusers import I2VGenXLPipeline

# Import imageio for assembling individual PIL images into a video stream
import imageio

# Import our base interface and global configurations
from .base import BaseModel
from ..config import HF_TOKEN, MODEL_IDS, DEVICE, MOCK_INFERENCE, FORCE_CPU_INFERENCE

class VideoGenerator(BaseModel):
    """
    Wrapper for the Image-to-Video generation model (i2vgen-xl).
    Takes a PIL Image and a motion prompt, generates frames, and compiles them into MP4 bytes.
    """

    def __init__(self):
        self.pipe = None
        self.model_id = MODEL_IDS["video_generation"]

    def initialize(self) -> None:
        # If running on CPU and FORCE_CPU_INFERENCE is False, bypass the heavy video model load to prevent system crash.
        if MOCK_INFERENCE or (DEVICE == "cpu" and not FORCE_CPU_INFERENCE):
            print("[VideoGenerator] Running in MOCK mode or CPU bypass active. Bypassing video model load.")
            return

        try:
            torch_dtype = torch.float16 if DEVICE == "cuda" else torch.float32

            self.pipe = I2VGenXLPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch_dtype,
                token=HF_TOKEN
            )
            self.pipe.to(DEVICE)
        except Exception as e:
            print(f"[VideoGenerator Warning] Failed to load local weights: {e}. Degrading gracefully to MOCK fallback.")
            self.pipe = None

    def generate(self, **kwargs) -> bytes:
        """
        WHAT: Generates a sequence of video frames and encodes them into a temporary MP4 file.
        WHY: The output of the model is a list of raw image frames. To deliver a playable video 
             to the user, we must compile these frames into a standard compressed .mp4 container.
         HOW:
             1. Extracts the generated `image` from Stage 2.
             2. Extracts the `video_prompt` from the Stage 1 dictionary.
             3. Runs the model to generate frames (usually 16 to 24 frames).
             4. Writes the frames to a temporary MP4 file using `imageio` and `ffmpeg`.
             5. Reads the file back as raw bytes to return them safely.
        """
        # 1. Extract inputs
        pil_image: Image.Image = kwargs.get("image")
        prompt_data: Union[Dict[str, str], str] = kwargs.get("prompt", "")
        
        # Note: If your video model accepts a depth map (like a ControlNet-guided video model),
        # you would extract `depth_map = kwargs.get("depth")` here and feed it into the model.
        # Since standard i2vgen-xl infers motion and depth internally from the RGB image, 
        # we do not pass it directly, but we keep the structure flexible for future upgrades.

        if not pil_image:
            raise ValueError("VideoGenerator requires a valid 'image' in kwargs.")
            
        if isinstance(prompt_data, dict):
            actual_prompt = prompt_data.get("video_prompt", "")
        else:
            actual_prompt = str(prompt_data)

        if MOCK_INFERENCE or self.pipe is None:
            print("[VideoGenerator] Generating mock visual video (panning anim)...")
            from PIL import ImageDraw
            frames_np = []
            for i in range(16):
                # Copy the base image to animate it
                img = pil_image.copy()
                draw = ImageDraw.Draw(img)
                # Pan a small glowing circle across the frame
                cx = int(100 + (i / 15) * 504)
                cy = 256
                draw.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(250, 204, 21)) # Yellow sun
                frames_np.append(np.array(img))

            # Compile frames into MP4 bytes
            video_bytes = b""
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
                temp_path = temp_file.name
            try:
                imageio.mimwrite(temp_path, frames_np, format="mp4", fps=16)
                with open(temp_path, "rb") as f:
                    video_bytes = f.read()
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            return video_bytes

        try:
            # 2. Prepare the image size. i2vgen-xl works best with 704x512 resolution images.
            # We resize the input image dynamically to prevent aspect-ratio stretching or crashes.
            target_size = (704, 512)
            resized_image = pil_image.resize(target_size, Image.Resampling.LANCZOS)

            # 3. Generate Video Frames
            # num_inference_steps=25 is standard to get fluid motion in a short time.
            generator = torch.manual_seed(42) # Set seed for consistency
            
            # The pipeline outputs an object with a `frames` attribute (a list of lists of PIL Images)
            output = self.pipe(
                prompt=actual_prompt,
                image=resized_image,
                num_inference_steps=25,
                generator=generator
            )
            
            # Extract the list of generated frames (each frame is a PIL Image)
            frames: List[Image.Image] = output.frames[0]

            # 4. Convert PIL Images to NumPy arrays for writing
            frames_np = [np.array(frame) for frame in frames]

            # 5. Compile into an MP4 file
            # We write to a temporary file on disk first. This is significantly more robust 
            # than trying to stream raw bytes into memory because video encoding often requires 
            # a temporary file buffer to write container headers.
            video_bytes = b""
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # We save the video at 16 frames per second (fps) for natural-looking motion
                imageio.mimwrite(temp_path, frames_np, format="mp4", fps=16)
                
                # Read the compiled binary data back from disk
                with open(temp_path, "rb") as f:
                    video_bytes = f.read()
                    
            finally:
                # Safe cleanup of the temporary file from the operating system
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            # NOTE ON AUDIO INTEGRATION:
            # In a production app, if you want to bundle the Stage 4 audio track into this video, 
            # you would write the silent MP4 to disk, write the WAV audio to disk, and execute an 
            # FFmpeg subprocess to merge (mux) them together:
            # e.g., `ffmpeg -i video.mp4 -i audio.wav -c:v copy -c:a aac output.mp4`
            # For simplicity, we return the high-quality silent MP4 video bytes, which is standard 
            # for raw model outputs and avoids requiring external system FFmpeg binaries on dev machines.

            return video_bytes
        except Exception as e:
            raise RuntimeError(f"Video generation failed: {str(e)}") from e

    def cleanup(self) -> None:
        """
        WHAT: Unloads the video model from memory and clears the hardware cache.
        WHY: VRAM MANAGEMENT. Video models are incredibly massive. Since this is the final 
             stage of the pipeline, cleaning it up immediately is polite to other processes 
             running on the system and ensures the GPU is fully reset for the next user request.
        HOW: Deletes Python references, forces garbage collection, and calls empty_cache().
        """
        if MOCK_INFERENCE:
            return

        if self.pipe is not None:
            del self.pipe
            self.pipe = None
            
        # Force Python to run garbage collection
        gc.collect()
        
        # If using a GPU, force PyTorch to release the freed memory back to the OS
        if DEVICE == "cuda":
            torch.cuda.empty_cache()