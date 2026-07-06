# file_manager.py placeholder
"""
WHAT: A utility module for handling local file system operations (I/O) for generated media.
WHY: AI models generate raw objects in memory (PIL Images, byte strings, numpy arrays). 
     To send these to a web frontend, we must serialize them into standard file formats 
     (.png, .wav, .mp4) on disk, and provide static URLs pointing to those files.
HOW: It reads the OUTPUT_DIR from config, ensures directories exist for each specific job_id, 
     and writes binary or image data to disk. It returns a relative URL path (e.g., /assets/...) 
     that FastAPI will be configured to serve statically.
"""

import os
from PIL import Image

# Import the configured base output directory from our config file
# Note: Ensure that Python's execution path allows this import, typically running from the backend root.
from ..config import OUTPUT_DIR

def ensure_output_dir(job_id: str) -> str:
    """
    WHAT: Creates a dedicated folder for a specific job on the local file system.
    WHY: We want to organize files by job_id so assets from different requests don't overwrite each other.
    HOW: Uses os.makedirs with exist_ok=True to safely create the directory path without throwing errors 
         if it already exists. Returns the absolute or relative path to the newly created folder.
    """
    job_dir = os.path.join(OUTPUT_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    return job_dir

def save_image(pil_image: Image.Image, job_id: str, asset_name: str) -> str:
    """
    WHAT: Saves a PIL (Python Imaging Library) Image object to disk as a PNG.
    WHY: The Image Generator and Depth Estimator outputs in-memory PIL objects. They must be saved.
         We use `asset_name` because we need to save both the base image ("image") and depth map ("depth").
    HOW: Calls ensure_output_dir(), saves the file, and returns the relative static URL.
    """
    job_dir = ensure_output_dir(job_id)
    filename = f"{asset_name}.png"
    filepath = os.path.join(job_dir, filename)
    
    # Save the PIL image object directly to the file system
    pil_image.save(filepath, format="PNG")
    
    # Return the relative URL path that FastAPI will use to serve this file.
    # Assuming main.py will mount OUTPUT_DIR at the route "/assets"
    return f"/assets/{job_id}/{filename}"

def save_audio(audio_bytes: bytes, job_id: str) -> str:
    """
    WHAT: Saves raw audio byte data to disk as a WAV file.
    WHY: The Audio Generator outputs raw audio data that must be serialized for frontend playback 
         and eventually muxed into the final video.
    HOW: Writes the bytes to disk in binary mode ("wb").
    """
    job_dir = ensure_output_dir(job_id)
    filename = "audio.wav"
    filepath = os.path.join(job_dir, filename)
    
    # Write raw bytes to file
    with open(filepath, "wb") as f:
        f.write(audio_bytes)
        
    return f"/assets/{job_id}/{filename}"

def save_video(video_bytes: bytes, job_id: str) -> str:
    """
    WHAT: Saves raw video byte data to disk as an MP4 file.
    WHY: The Video Generator outputs the final culmination of our pipeline. This MP4 is the 
         end product delivered to the user.
    HOW: Writes the bytes to disk in binary mode ("wb").
    """
    job_dir = ensure_output_dir(job_id)
    filename = "video.mp4"
    filepath = os.path.join(job_dir, filename)
    
    # Write raw bytes to file
    with open(filepath, "wb") as f:
        f.write(video_bytes)
        
    return f"/assets/{job_id}/{filename}"