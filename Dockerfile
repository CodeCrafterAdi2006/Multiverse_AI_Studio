# Stage 1: Build the React frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve using Python FastAPI
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
# - git: needed for certain pip dependencies
# - libsndfile1: needed for SciPy audio file writes
# - ffmpeg: needed for imageio video compilations
RUN apt-get update && apt-get install -y \
    git \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first to leverage Docker build cache
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy source code and frontend build output
COPY backend ./backend
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port 7860 (Hugging Face Spaces default container port)
EXPOSE 7860

# Start uvicorn server on port 7860, binding to all interfaces
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
