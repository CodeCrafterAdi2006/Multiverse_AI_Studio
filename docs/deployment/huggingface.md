# Deploying to Hugging Face Spaces (Docker)

This guide provides step-by-step instructions to deploy **Multiverse AI Studio** to Hugging Face Spaces as a monolithic Docker application.

---

## 🛠️ Step 1: Create a new Space on Hugging Face

1. Log in to [Hugging Face](https://huggingface.co/).
2. Click on your profile icon in the top right and select **New Space** (or go directly to [huggingface.co/new-space](https://huggingface.co/new-space)).
3. Fill in the Space settings:
   * **Space Name**: `Multiverse-AI-Studio` (or your choice).
   * **License**: `apache-2.0` (or your choice).
   * **SDK**: Select **Docker**.
   * **Docker Template**: Select **Blank** (do not select any pre-configured template; our local `Dockerfile` will define the container).
   * **Space Hardware**: **CPU Basic (Free)** is sufficient for our cloud image generation and local depth maps. If you want full-speed local video/audio generation, you can upgrade to a GPU instance.
   * **Visibility**: Public or Private.
4. Click **Create Space**.

---

## ⚙️ Step 2: Configure Environment Secrets

Because the pipeline requires access tokens and production flags, you must inject these variables into the Space's runtime environment:

1. In your newly created Space, navigate to the **Settings** tab.
2. Scroll down to the **Variables and secrets** section.
3. Click **New secret** to add the following credentials:
   * **`HF_TOKEN`**: Paste your Hugging Face User Access Token (needed for FLUX cloud queries and model downloads).
   * **`MOCK_INFERENCE`**: Set to `False` (to run the real production cloud FLUX image generation and local depth mapping).
   * **`FORCE_CPU_INFERENCE`**: Set to `False` (safe default to keep audio/video mock compilation on basic CPU instances to avoid memory crash, or set to `True` if you want to test CPU-only execution of all models).
4. Save the secrets.

---

## 🚀 Step 3: Push Your Code to the Space

Hugging Face Spaces are backed by a Git repository. You can push your code directly to the Space's Git remote:

### Option A: Push directly from your local repository (Recommended)
You can add your Hugging Face Space as a new git remote and push directly to it:

1. Open your terminal in the project root directory.
2. Add the Hugging Face remote (replace `<username>` and `<space-name>` with your HF details):
   ```bash
   git remote add hf https://huggingface.co/spaces/<username>/<space-name>
   ```
3. Push to Hugging Face:
   ```bash
   # You will be prompted for your Hugging Face username and token (use your HF_TOKEN as the password)
   git push -f hf main
   ```

### Option B: Clone and Copy
If you prefer to keep the repositories separate:
1. Clone the empty Hugging Face Space repository:
   ```bash
   git clone https://huggingface.co/spaces/<username>/<space-name>
   ```
2. Copy all files from your `Multiverse_AI_Studio` folder (except `.git`, `.env`, and `node_modules/`) into the cloned directory.
3. Commit and push the files:
   ```bash
   git add .
   git commit -m "Deploy Multiverse AI Studio monolithic container"
   git push
   ```

---

## 🔍 Step 4: Build and Verify

1. Go to your Hugging Face Space page.
2. You will see the status change to **Building** as it executes the `Dockerfile` steps:
   * It builds the React client.
   * It sets up the Debian/Python image, installs system requirements (libsndfile, FFmpeg).
   * It starts the uvicorn web server.
3. Once the build finishes, the status will show **Running**, and the app will load directly inside the Hugging Face Space iframe!
