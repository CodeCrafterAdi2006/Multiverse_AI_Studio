"""
WHAT: The main entry point for the Multiverse AI Studio FastAPI application.
WHY: This file bootstraps the entire web server. It configures Cross-Origin Resource Sharing (CORS), 
     mounts physical filesystem directories to virtual web URLs, registers the API routes, 
     and handles server lifecycle hooks (such as creating storage folders on startup).
HOW: It instantiates a `FastAPI` application, applies standard middlewares (CORSMiddleware), 
     mounts `StaticFiles`, and registers the router imported from `api/routes.py`.
"""

import os
from dotenv import load_dotenv

# WHY: Load .env variables *before* importing config.py. That way,
# os.getenv("HF_TOKEN") calls in config.py will find the loaded token.
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import configurations and routers (relative to the backend package)
from .config import OUTPUT_DIR
from .api.routes import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    WHAT: A lifecyle manager handling startup and shutdown operations for the application.
    WHY: Before the server begins accepting client requests, we must guarantee that the local 
         filesystem is ready to receive generated assets. If we don't create the OUTPUT_DIR, 
         subsequent file write operations will throw directory-not-found errors.
    HOW: Uses Python's `contextlib.asynccontextmanager` decorator. Everything before the `yield` 
         runs on startup; everything after runs on shutdown.
    """
    # STARTUP: Create the asset output folder if it doesn't exist yet
    if not os.path.exists(OUTPUT_DIR):
        print(f"[Startup] Creating directory for generated assets: {OUTPUT_DIR}")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    else:
        print(f"[Startup] Output directory already exists: {OUTPUT_DIR}")
        
    yield  # The application runs and processes requests here
    
    # SHUTDOWN: Any cleanup logic (e.g., closing DB pools or freeing remaining models) goes here.
    print("[Shutdown] Cleaning up API resources.")


# Initialize the FastAPI application
# Using the lifespan parameter to handle our startup directory creation logic cleanly
app = FastAPI(
    title="Multiverse AI Studio API",
    description=(
        "A production-quality generative AI pipeline backend that chains five Hugging Face models: "
        "Prompt Expansion (LLM), Image Generation (SDXL), Depth Estimation (Depth-Anything), "
        "Audio Generation (MusicGen), and Video Generation (i2vgen-xl)."
    ),
    version="1.0.0",
    lifespan=lifespan
)


# ==========================================
# CORS CONFIGURATION (Cross-Origin Resource Sharing)
# ==========================================
# WHAT: Specifies which web domains are permitted to communicate with this backend API.
# WHY: By default, web browsers block frontend code (e.g., running on localhost:3000) from 
#      making requests to a different domain/port (e.g., running on localhost:8000). 
#      Configuring CORS allows our Next.js/React frontend to talk to our FastAPI backend safely.
# HOW: We use FastAPI's built-in CORSMiddleware and supply an explicit list of allowed origins.
origins = [
    "http://localhost:3000",      # Standard React / Next.js development server
    "http://127.0.0.1:3000",    # Alternative local address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],          # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],          # Allows all HTTP headers (Content-Type, Authorization, etc.)
)


# ==========================================
# STATIC FILES MOUNTING
# ==========================================
# WHAT: Maps a directory on the server's hard drive to a virtual web route.
# WHY: When we save a generated video to `generated_assets/job_123/video.mp4`, we need a way 
#      for the frontend to download and display it. Instead of writing custom download endpoints, 
#      FastAPI can serve everything in this folder statically.
# HOW: We mount the `OUTPUT_DIR` to the path `/assets`. 
#      Example: Opening `http://localhost:8000/assets/123/image.png` will load the file 
#               stored at `generated_assets/123/image.png` on disk.
# WHY ORDER MATTERS: FastAPI's StaticFiles will crash immediately if the directory doesn't exist 
# at mount time (which happens *before* the lifespan function runs). So we create the directory first.
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount(
    "/assets", 
    StaticFiles(directory=OUTPUT_DIR), 
    name="assets"
)


# ==========================================
# API ROUTE REGISTRATION
# ==========================================
# WHAT: Registers our logical endpoints under a standard url path.
# WHY: Keeps code modular by keeping route definitions inside `api/routes.py` rather than 
#      cluttering `main.py`.
# HOW: We prefix all routes with `/api` so that endpoints become `/api/generate`, `/api/status`, etc.
app.include_router(
    api_router, 
    prefix="/api"
)

# ==========================================
# FRONTEND STATIC FILES MOUNTING (FOR MONOLITHIC PRODUCTION DEPLOYMENT)
# ==========================================
# WHAT: Serves the built React frontend bundle.
# WHY: In platforms like Hugging Face Spaces, the container can only expose a single port (7860).
#      FastAPI serves the static HTML/JS/CSS React bundle and handles API requests on "/api".
# HOW: We mount the bundled assets under "/static" and serve "index.html" for both "/" and any
#      unknown client-side route (SPA fallback), so deep links like /studio/<jobId> survive a refresh.
FRONTEND_DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
FRONTEND_INDEX = os.path.join(FRONTEND_DIST_DIR, "index.html")
if os.path.exists(FRONTEND_DIST_DIR):
    print(f"[Startup] Serving frontend static files from: {FRONTEND_DIST_DIR}")
    frontend_static_dir = os.path.join(FRONTEND_DIST_DIR, "static")
    if os.path.isdir(frontend_static_dir):
        app.mount(
            "/static",
            StaticFiles(directory=frontend_static_dir),
            name="frontend_static",
        )

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Unknown routes fall back to index.html so client-side (React Router) routing works.
        return FileResponse(FRONTEND_INDEX)
else:
    print("[Startup Warning] Frontend build directory not found. Server running API-only mode.")


# Standard run instruction comment
# To run this server, execute the following command in your terminal from the backend directory:
# `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`