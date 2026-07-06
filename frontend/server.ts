import express from 'express';
import path from 'path';
import { createServer as createViteServer } from 'vite';
import crypto from 'crypto';

const STATUSES = [
  { status: 'QUEUED', stage: 'Initializing...' },
  { status: 'EXPANDING_PROMPT', stage: 'Enriching your prompt with AI...' },
  { status: 'GENERATING_IMAGE', stage: 'Painting the visual scene...' },
  { status: 'ESTIMATING_DEPTH', stage: 'Calculating 3D geometry...' },
  { status: 'GENERATING_AUDIO', stage: 'Composing background audio...' },
  { status: 'GENERATING_VIDEO', stage: 'Synthesizing final video...' },
  { status: 'COMPLETED', stage: 'Pipeline finished successfully!' },
];

const jobs = new Map<string, any>();

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // API Routes
  app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  app.post('/api/generate', (req, res) => {
    const { prompt } = req.body;
    const jobId = crypto.randomUUID();
    
    jobs.set(jobId, {
      job_id: jobId,
      status: STATUSES[0].status,
      stage: STATUSES[0].stage,
      stepIndex: 0,
      assets: {},
      error: null,
      prompt
    });

    // Mock background progression
    const interval = setInterval(() => {
      const job = jobs.get(jobId);
      if (!job) {
        clearInterval(interval);
        return;
      }

      job.stepIndex++;
      
      if (job.stepIndex >= STATUSES.length - 1) {
        // COMPLETED
        job.status = STATUSES[STATUSES.length - 1].status;
        job.stage = STATUSES[STATUSES.length - 1].stage;
        
        // Mock Assets
        job.assets = {
          image: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop', // beautiful abstract art
          depth: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop&monochrome=1', // grayscale version for mock
          audio: 'https://cdn.pixabay.com/download/audio/2022/10/25/audio_24db8a23d9.mp3?filename=ambient-piano-125067.mp3', // royalty free ambient
          video: 'https://cdn.pixabay.com/video/2022/11/17/139369-772223838_tiny.mp4' // abstract particle video
        };
        clearInterval(interval);
      } else {
        job.status = STATUSES[job.stepIndex].status;
        job.stage = STATUSES[job.stepIndex].stage;
      }
    }, 4000); // 4 seconds per stage for testing

    res.json({ job_id: jobId });
  });

  app.get('/api/status/:jobId', (req, res) => {
    const job = jobs.get(req.params.jobId);
    if (!job) {
      return res.status(404).json({ detail: 'Job not found' });
    }
    res.json({
      job_id: job.job_id,
      status: job.status,
      stage: job.stage
    });
  });

  app.get('/api/result/:jobId', (req, res) => {
    const job = jobs.get(req.params.jobId);
    if (!job) {
      return res.status(404).json({ detail: 'Job not found' });
    }
    res.json({
      job_id: job.job_id,
      status: job.status,
      assets: job.assets,
      error: job.error
    });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*all', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
