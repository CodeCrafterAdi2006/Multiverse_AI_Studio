# routes.py placeholder
"""
WHAT: This file defines the REST API endpoints for the Multiverse AI Studio backend.
WHY: It serves as the bridge between the frontend (React/Vue/etc.) and our Python backend logic.
     It exposes the necessary routes to submit prompts, check job progress, and fetch final assets.
HOW: We use FastAPI's `APIRouter` to modularize these endpoints. The router will be imported 
     and attached to the main app in `main.py`.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

# Import our job state manager to create and fetch job records
from ..utils.job_store import create_job, get_job

# Import the orchestrator function that will actually run the 5 models.
# (This will be implemented in services/pipeline.py)
from ..services.pipeline import run_pipeline

# Initialize the router
router = APIRouter()

class GenerateRequest(BaseModel):
    """
    Pydantic schema for the incoming POST /generate request body.
    Ensures the user sends a valid JSON object with a 'prompt' string.
    """
    prompt: str


@router.get("/health")
def health_check():
    """
    WHAT: A simple endpoint to verify the API server is alive.
    WHY: Essential for monitoring and deployment (e.g., Docker/Kubernetes health checks) 
         to know when the backend is ready to accept traffic.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/generate")
def generate_assets(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    WHAT: Endpoint to start the AI generation pipeline based on a user's prompt.
    
    WHY RETURN A JOB_ID IMMEDIATELY?
    Running 5 heavy AI models (LLM, Image, Depth, Audio, Video) sequentially can take 
    anywhere from 30 seconds to several minutes depending on hardware. If we kept the HTTP 
    request open waiting for the result, it would likely hit a server or browser timeout limit. 
    Instead, we immediately return a unique `job_id` and process the generation asynchronously. 
    The frontend can then use this ID to poll for status updates.

    WHY FASTAPI BACKGROUND TASKS?
    BackgroundTasks are built directly into FastAPI/Starlette. They allow us to execute a 
    function after returning a response. 
    - Pros over Threading: Cleaner API, integrated seamlessly with FastAPI's request lifecycle.
    - Pros over Celery/RQ: Zero infrastructure overhead. We don't need to install, configure, 
      or run separate Redis brokers and worker processes. Since this is an MVP/Studio app, 
      keeping everything in a single process is much simpler to deploy and maintain.
      (Note: Starlette runs standard `def` functions added to BackgroundTasks in a separate 
      threadpool, so it won't block the main async event loop from serving other requests).
    """
    # 1. Create a new job in our in-memory store
    job_id = create_job()
    
    # 2. Hand off the heavy lifting to a background task
    background_tasks.add_task(run_pipeline, job_id, request.prompt)
    
    # 3. Return the ID immediately to the client
    return {"job_id": job_id}


@router.get("/status/{job_id}")
def get_job_status(job_id: str):
    """
    WHAT: Endpoint for the frontend to poll the current progress of a specific job.
    WHY: Keeps the user informed about which model is currently running (e.g., "Generating Image...").
         A responsive UI during a multi-minute wait is critical for user experience.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "job_id": job_id,
        "status": job["status"],
        "stage": job["stage"]
    }


@router.get("/result/{job_id}")
def get_job_result(job_id: str):
    """
    WHAT: Endpoint to fetch the final outputs (URLs) and any errors of a job.
    WHY: Once the frontend sees that the status is COMPLETED (or FAILED), it calls this 
         endpoint to retrieve the dictionary of generated static file URLs (image, video, etc.) 
         to render on the screen.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "job_id": job_id,
        "status": job["status"],
        "stage": job["stage"],
        "assets": job["assets"],
        "error": job["error"],
        "scene_description": job["scene_description"]
    }