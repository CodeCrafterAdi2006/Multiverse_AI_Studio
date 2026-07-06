# Engineering Tradeoffs and Architecture Decisions

This document summarizes the architectural compromises and fallback plans designed for the **Multiverse AI Studio** multimedia generation pipeline.

---

## 1. Local GPU vs. Cloud Fallbacks (Model Swapping)

* **Decision**: Define a generic BaseModel interface (`initialize()`, `generate()`, `cleanup()`) instead of coupling pipeline execution logic to specific local Hugging Face pipeline weights.
* **Tradeoff**:
  * *Pros*: Swapping SDXL for FLUX, or replacing local MusicGen weights with the Hugging Face Serverless API, requires changing only the model's wrapper — the orchestrator (`pipeline.py`) remains untouched.
  * *Cons*: Requires writing boilerplate stubs and wrappers.
  * *Status*: Prompts and visual generation are easily modularized. The `PromptExpander` currently defaults to the serverless HF Inference API for Mistral-7B, preserving CPU VRAM for local rendering.

---

## 2. In-Memory Job Store vs. Persistent Database

* **Decision**: Use a global Python dictionary `_jobs = {}` in [`job_store.py`](file:///c:\AI Native founder\AI_Engineering\Projects\Multiverse_AI_Studio\backend\utils\job_store.py) to manage pipeline states.
* **Tradeoff**:
  * *Pros*: Zero architectural overhead. We do not need a Redis instance or database migration tables (SQLite/PostgreSQL) in the MVP stage. This speeds up dev workflow and reduces cloud deployment costs.
  * *Cons*: Job memory is volatile. If the FastAPI application server restarts or encounters a crash, all active and completed job data is permanently lost.
  * *Status*: Documented in README as a future SQLite/Redis improvement. Acceptable for dev.

---

## 3. WebSockets vs. HTTP Polling vs. Server-Sent Events

* **Decision**: Implement client-side polling (polling the result endpoint `/api/result/{job_id}` every 2 seconds) instead of a WebSockets connection.
* **Tradeoff**:
  * *Pros*: WebSockets introduce bidirectional complexity. Since our pipeline progress stream is strictly unidirectional (Server → Browser), WebSockets would add unnecessary protocol handshakes, connection state tracking, and port management. Polling is simple to scale and requires no extra backend infrastructure.
  * *Cons*: Repeated HTTP request overhead.
  * *Status*: Current polling tracks progressive asset URLs. SSE (Server-Sent Events) is the recommended middle-ground upgrade to avoid socket complexity.

---

## 4. Video Conditional Fallback (Image-to-Video vs. Text-to-Video)

* **Decision**: Image-conditioned video generation is the preferred method to keep the generated base image as the "visual anchor" for the video. If the GPU VRAM is restricted (< 16 GB), the pipeline falls back to text-conditioned video models.
* **Tradeoff**:
  * *Pros*: Image-conditioned video results in high temporal visual coherence.
  * *Cons*: Massive memory footprint. If the system fails to run I2VGen-XL, prompt fallbacks are executed.

---

## 5. Developer Mock Inference Mode

* **Decision**: Add a `MOCK_INFERENCE` toggle that generates custom mock visual canvases, grayscale depth gradients, sine waves, and moving circles (compiling a real compressed MP4) in-memory using `Pillow` and `imageio`.
* **Tradeoff**:
  * *Pros*: Allows the entire stack (FastAPI server, file management, static mounts, Vite frontend, and polling loops) to be validated in 1 second on any machine without downloading 20 GB of neural network weights.
  * *Cons*: Mock visuals do not represent final model outputs.

---

## 6. Adaptive Hardware Profiling & CPU Bypasses

* **Decision**: Implement automatic hardware accelerator detection. When running in production mode (`MOCK_INFERENCE=False`) on a CPU-only host (`DEVICE == "cpu"`), the backend automatically bypasses loading heavy transformer weights locally (Meta's `MusicGen` and Alibaba's `i2vgen-xl`) to prevent RAM exhaustion and application lockups.
* **Toggles**:
  * `MOCK_INFERENCE`: Toggles the entire pipeline into mock mode (instant 1s runs).
  * `FORCE_CPU_INFERENCE`: Overrides the CPU safety guards. When set to `True`, it forces the CPU to download and execute the real `MusicGen` and `i2vgen-xl` models, allowing reviewers to verify local CPU executions (at the expense of generation time).
* **Tradeoff**:
  * *Pros*:
    * **Zero Friction Developer Experience (DX)**: Reviewers without dedicated GPU hardware can run the project instantly and see real cloud image generation (FLUX) and real local depth map synthesis, without their systems freezing or crashing on the audio/video stages.
    * **CUDA Transparent**: If the project is run on a GPU-enabled machine (e.g. Paperspace, lambda labs, or desktop with NVIDIA card), the code automatically uses CUDA and executes the full transformer pipelines.
  * *Cons*: On CPU hosts without `FORCE_CPU_INFERENCE` active, the generated video and audio remain mock files.
