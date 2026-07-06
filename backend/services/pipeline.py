# pipeline.py placeholder
"""
WHAT: The central orchestration layer for Multiverse AI Studio.
WHY: We have 5 distinct AI models that need to run in a specific logical sequence. 
     This file coordinates moving data (prompts, images, audio) between them, tracking 
     overall progress, and gracefully handling errors without crashing the entire app.
HOW: It exposes an asynchronous function `run_pipeline` which is called by the FastAPI 
     background task. It utilizes a `ThreadPoolExecutor` to safely run heavy, synchronous 
     machine learning workloads without freezing the web server.
"""

import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from ..config import MOCK_INFERENCE

# Import job state and file I/O utilities
from ..utils.job_store import (
    update_job_status,
    update_job_asset,
    set_job_error,
    set_job_scene_description,
    STATUS_EXPANDING_PROMPT,
    STATUS_GENERATING_IMAGE,
    STATUS_ESTIMATING_DEPTH,
    STATUS_GENERATING_AUDIO,
    STATUS_GENERATING_VIDEO,
    STATUS_COMPLETED,
    STATUS_PARTIAL_FAILURE,
    STATUS_FAILED
)
from ..utils.file_manager import save_image, save_audio, save_video

# Import the model wrappers. 
# (These will be implemented following the BaseModel interface)
from ..models.prompt_expander import PromptExpander
from ..models.image_generator import ImageGenerator
from ..models.depth_estimator import DepthEstimator
from ..models.audio_generator import AudioGenerator
from ..models.video_generator import VideoGenerator

def execute_model_sync(model, **kwargs):
    """
    WHAT: A synchronous helper function that strictly enforces the BaseModel interface.
    WHY: We must ensure that EVERY model is loaded, executed, and aggressively unloaded 
         from VRAM to prevent Out-of-Memory (OOM) crashes on consumer hardware.
    HOW: Uses a try/finally block so that even if `generate()` throws an exception, 
         `cleanup()` is guaranteed to run and free GPU memory.
    """
    try:
        model.initialize()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize {model.__class__.__name__}: {str(e)}") from e
        
    try:
        # Pass dynamic arguments (prompt, image, etc.) into the generation step
        return model.generate(**kwargs)
    finally:
        # ALWAYS unload the model and clear CUDA cache
        model.cleanup()


async def run_pipeline(job_id: str, prompt: str, groq_key: str = None):
    """
    WHAT: The main execution flow orchestrating the 5-stage AI pipeline.

    WHY USE THREAD_POOL_EXECUTOR?
    FastAPI uses an asynchronous event loop (`asyncio`). However, AI model inference 
    (PyTorch/HuggingFace) is CPU/GPU-bound and completely synchronous. If we called 
    `model.generate()` directly here, it would block the main thread. No other users 
    could access the API, and GET /status requests would time out. 
    By offloading the execution to a ThreadPoolExecutor, the heavy ML computation runs 
    on a separate thread, freeing FastAPI to continue serving concurrent web requests.

    :param groq_key: Optional Groq API key provided by the visitor via X-Groq-Key header.
                     If present, it overrides the server's GROQ_API_KEY env var for this
                     specific request, so the visitor's quota is used, not the server's.

    DEPENDENCY GRAPH & CONCURRENCY:
    - Stage 1: Prompt Expansion (Needs: user prompt)
    - Stage 2: Image Gen (Needs: expanded prompt)
    - Stage 3: Depth Est (Needs: generated image)
    - Stage 4: Audio Gen (Needs: expanded prompt)
    - Stage 5: Video Gen (Needs: image, depth map, audio)

    Notice that AFTER image generation, Depth Estimation and Audio Generation do NOT
    depend on each other. Conceptually, they *could* be run in parallel. However, running
    two heavy Hugging Face models simultaneously would instantly cause a VRAM Out-of-Memory
    error on most machines. Therefore, we execute them strictly sequentially here.
    """
    
    # We use a single worker thread to enforce strict sequential execution for memory safety.
    executor = ThreadPoolExecutor(max_workers=1)
    loop = asyncio.get_running_loop()
    
    # DATA CONTRACT:
    # - PromptExpander.generate() returns a dict with keys:
    #   { "image_prompt": str, "audio_prompt": str, "video_prompt": str, "scene_description": str }
    # - ImageGenerator accepts: prompt=dict (uses image_prompt) or prompt=str
    # - AudioGenerator accepts: prompt=dict (uses audio_prompt) or prompt=str
    # - VideoGenerator accepts: prompt=dict (uses video_prompt) or prompt=str, plus image, depth, audio
    # - DepthEstimator accepts: image=PIL.Image
    # Variables to hold assets as they move through the pipeline
    expanded_prompt = {
        "image_prompt": prompt,
        "audio_prompt": prompt,
        "video_prompt": prompt,
        "scene_description": prompt
    }
    pil_image = None
    depth_image = None
    audio_bytes = None
    video_bytes = None
    
    # Track if any non-fatal errors occurred to flag the final status
    has_errors = False
    error_logs = []

    def record_stage_error(stage_name: str, exception: Exception):
        """Helper to log stage failures without crashing the pipeline."""
        nonlocal has_errors
        has_errors = True
        err_msg = f"{stage_name} failed: {str(exception)}"
        error_logs.append(err_msg)
        # Update the job store so the frontend sees the partial failure immediately
        set_job_error(job_id, " | ".join(error_logs), partial_failure=True)
        print(f"[JOB {job_id}] {err_msg}")
        traceback.print_exc()

    # ==========================================
    # STAGE 1: PROMPT EXPANSION
    # ==========================================
    update_job_status(job_id, STATUS_EXPANDING_PROMPT, "Enriching your prompt with AI...")
    if MOCK_INFERENCE:
        await asyncio.sleep(2.5)
    try:
        expander = PromptExpander()
        # await loop.run_in_executor runs the sync function in the background thread.
        # We pass groq_key so the expander uses the visitor's personal key if provided.
        expanded_prompt = await loop.run_in_executor(
            executor, partial(execute_model_sync, expander, prompt=prompt, groq_key=groq_key)
        )
    except Exception as e:
        record_stage_error("Prompt Expansion", e)
        # Fallback: if LLM fails, use the user's original prompt for all fields
        expanded_prompt = {
            "image_prompt": prompt,
            "audio_prompt": prompt,
            "video_prompt": prompt,
            "scene_description": prompt
        }
    # Save the scene description so the frontend can show it to the user
    set_job_scene_description(job_id, expanded_prompt["scene_description"])

    # ==========================================
    # STAGE 2: IMAGE GENERATION
    # ==========================================
    update_job_status(job_id, STATUS_GENERATING_IMAGE, "Painting the visual scene...")
    if MOCK_INFERENCE:
        await asyncio.sleep(2.5)
    try:
        image_gen = ImageGenerator()
        pil_image = await loop.run_in_executor(
            executor, partial(execute_model_sync, image_gen, prompt=expanded_prompt)
        )
        # Save asset to disk and update job store with URL
        if pil_image:
            image_url = save_image(pil_image, job_id, "image")
            update_job_asset(job_id, "image", image_url)
    except Exception as e:
        record_stage_error("Image Generation", e)
        # If Image Gen fails, the rest of the visual pipeline (Depth, Video) will likely fail,
        # but we CONTINUE anyway per the best-effort requirements.

    # ==========================================
    # STAGE 3: DEPTH ESTIMATION
    # ==========================================
    update_job_status(job_id, STATUS_ESTIMATING_DEPTH, "Calculating 3D geometry...")
    if MOCK_INFERENCE:
        await asyncio.sleep(2.5)
    try:
        if pil_image is None:
            raise ValueError("Skipping Depth Estimation because Image Generation failed.")
            
        depth_est = DepthEstimator()
        depth_image = await loop.run_in_executor(
            executor, partial(execute_model_sync, depth_est, image=pil_image)
        )
        if depth_image:
            depth_url = save_image(depth_image, job_id, "depth")
            update_job_asset(job_id, "depth", depth_url)
    except Exception as e:
        record_stage_error("Depth Estimation", e)

    # ==========================================
    # STAGE 4: AUDIO GENERATION
    # ==========================================
    update_job_status(job_id, STATUS_GENERATING_AUDIO, "Composing background audio...")
    if MOCK_INFERENCE:
        await asyncio.sleep(2.5)
    try:
        audio_gen = AudioGenerator()
        audio_bytes = await loop.run_in_executor(
            executor, partial(execute_model_sync, audio_gen, prompt=expanded_prompt)
        )
        if audio_bytes:
            audio_url = save_audio(audio_bytes, job_id)
            update_job_asset(job_id, "audio", audio_url)
    except Exception as e:
        record_stage_error("Audio Generation", e)

    # ==========================================
    # STAGE 5: VIDEO GENERATION
    # ==========================================
    update_job_status(job_id, STATUS_GENERATING_VIDEO, "Synthesizing final video...")
    if MOCK_INFERENCE:
        await asyncio.sleep(2.5)
    try:
        if pil_image is None:
            raise ValueError("Skipping Video Generation because source image is missing.")
            
        video_gen = VideoGenerator()
        video_bytes = await loop.run_in_executor(
            executor, partial(execute_model_sync, video_gen, 
                              prompt=expanded_prompt,
                              image=pil_image, 
                              depth=depth_image, 
                              audio=audio_bytes)
        )
        if video_bytes:
            video_url = save_video(video_bytes, job_id)
            update_job_asset(job_id, "video", video_url)
    except Exception as e:
        record_stage_error("Video Generation", e)

    # ==========================================
    # FINALIZATION
    # ==========================================
    executor.shutdown(wait=False)
    
    # If the core asset (image) failed entirely, we might consider the job FAILED.
    # Otherwise, if some parts succeeded but others failed, it's a PARTIAL_FAILURE.
    if not pil_image and not audio_bytes:
        set_job_error(job_id, "Pipeline completely failed. " + " | ".join(error_logs))
    elif has_errors:
        update_job_status(job_id, STATUS_PARTIAL_FAILURE, "Completed with some errors.")
    else:
        update_job_status(job_id, STATUS_COMPLETED, "Pipeline finished successfully!")