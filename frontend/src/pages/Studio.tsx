import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import { CheckCircle2, Circle, Loader2, ArrowLeft, Download, AlertCircle, Play, ChevronDown, Sparkles } from 'lucide-react';
import { getJobStatus, getJobResult, type JobStatus, type JobResult } from '../lib/api';
import DepthSlider from '../components/DepthSlider';
import AudioPlayer from '../components/AudioPlayer';
import VideoPlayer from '../components/VideoPlayer';

const STAGES = [
  'QUEUED',
  'EXPANDING_PROMPT',
  'GENERATING_IMAGE',
  'ESTIMATING_DEPTH',
  'GENERATING_AUDIO',
  'GENERATING_VIDEO'
];

export default function Studio() {
  const { jobId } = useParams<{ jobId: string }>();
  const [status, setStatus] = useState<string>('QUEUED');
  const [stageDesc, setStageDesc] = useState<string>('Initializing...');
  const [result, setResult] = useState<JobResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSceneExpanded, setIsSceneExpanded] = useState<boolean>(false);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    const checkJob = async () => {
      try {
        const data: JobResult = await getJobResult(jobId!);
        
        setStatus(data.status);
        if (data.stage) {
          setStageDesc(data.stage);
        }
        
        // Update the result progressively as assets are generated
        setResult(data);

        if (data.status === 'COMPLETED' || data.status === 'FAILED' || data.status === 'PARTIAL_FAILURE') {
          clearInterval(intervalId);
        }
      } catch (err) {
        console.error(err);
        setError('Connection lost. Retrying...');
      }
    };

    if (status !== 'COMPLETED' && status !== 'FAILED' && status !== 'PARTIAL_FAILURE') {
      intervalId = setInterval(checkJob, 2000);
      checkJob(); // initial check
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [jobId, status]);

  const getStageState = (stageName: string) => {
    const currentIndex = STAGES.indexOf(status);
    const stageIndex = STAGES.indexOf(stageName);
    
    // For PARTIAL_FAILURE or FAILED: figure out which stages completed
    if (status === 'FAILED') {
      if (stageIndex < currentIndex) return 'complete';
      if (stageIndex === currentIndex) return 'error';
      return 'pending';
    }
    if (status === 'PARTIAL_FAILURE') {
      if (stageIndex < currentIndex) return 'complete';
      if (stageIndex === currentIndex) return 'error';
      return 'pending';
    }
    
    // Normal completion flow
    if (status === 'COMPLETED') return 'complete';
    if (stageIndex < currentIndex) return 'complete';
    if (stageIndex === currentIndex) return 'active';
    return 'pending';
  };

  const getStageLabel = (stageName: string) => {
    const labels: Record<string, string> = {
      QUEUED: 'Queued',
      EXPANDING_PROMPT: 'Expanding Prompt',
      GENERATING_IMAGE: 'Generating Image',
      ESTIMATING_DEPTH: 'Estimating Depth',
      GENERATING_AUDIO: 'Generating Audio',
      GENERATING_VIDEO: 'Generating Video'
    };
    return labels[stageName] || stageName;
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white p-6 md:p-12 font-sans">
      <Link to="/" className="inline-flex items-center text-gray-400 hover:text-white transition-colors mb-12">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Generator
      </Link>

      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12">
        
        {/* Sidebar: Pipeline Tracker */}
        <div className="lg:col-span-4 space-y-8">
          <div>
            <h2 className="text-2xl font-display font-semibold mb-2">Pipeline Status</h2>
            <p className="text-gray-400 text-sm">Tracking synthesis progress in real-time.</p>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-xl">
            <div className="space-y-6">
              {STAGES.map((stage, idx) => {
                const state = getStageState(stage);
                return (
                  <div key={stage} className="flex items-start">
                    <div className="flex flex-col items-center mr-4">
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center border-2 transition-colors duration-500 ${
                        state === 'complete' ? 'bg-green-500/20 border-green-500 text-green-500' :
                        state === 'active' ? 'bg-blue-500/20 border-blue-500 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.5)]' :
                        state === 'error' ? 'bg-red-500/20 border-red-500 text-red-500' :
                        'bg-gray-800/50 border-gray-700 text-gray-600'
                      }`}>
                        {state === 'complete' && <CheckCircle2 className="w-5 h-5" />}
                        {state === 'active' && <Loader2 className="w-5 h-5 animate-spin" />}
                        {state === 'error' && <AlertCircle className="w-5 h-5" />}
                        {state === 'pending' && <Circle className="w-4 h-4" />}
                      </div>
                      {idx !== STAGES.length - 1 && (
                        <div className={`w-[2px] h-10 mt-2 transition-colors duration-500 ${
                          state === 'complete' ? 'bg-green-500/50' : 'bg-gray-800'
                        }`} />
                      )}
                    </div>
                    <div className="pt-1">
                      <p className={`font-medium ${
                        state === 'active' ? 'text-white' :
                        state === 'complete' ? 'text-gray-300' :
                        state === 'error' ? 'text-red-400' :
                        'text-gray-600'
                      }`}>
                        {getStageLabel(stage)}
                      </p>
                      {state === 'active' && (
                        <motion.p 
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="text-sm text-blue-400 mt-1"
                        >
                          {stageDesc}
                        </motion.p>
                      )}
                      {state === 'error' && result?.error && (
                        <motion.p
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="text-xs text-red-500 mt-1 break-words"
                        >
                          {result.error}
                        </motion.p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Collapsible Scene Description Panel */}
          {result?.scene_description && (
            <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden backdrop-blur-xl">
              <button
                onClick={() => setIsSceneExpanded(!isSceneExpanded)}
                className="w-full p-4 flex items-center justify-between text-left transition-colors hover:bg-white/5"
              >
                <span className="font-medium text-gray-300 text-sm">Your scene description</span>
                <ChevronDown
                  className={`w-4 h-4 text-gray-400 transition-transform duration-300 ${
                    isSceneExpanded ? 'rotate-180' : ''
                  }`}
                />
              </button>
              <AnimatePresence>
                {isSceneExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="px-4 pb-4 pt-2">
                      <p className="text-xs text-gray-500 leading-relaxed">
                        {result.scene_description}
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>

        {/* Main Content: Results */}
        <div className="lg:col-span-8">
          <AnimatePresence mode="wait">
            {result?.assets && Object.keys(result.assets).length > 0 ? (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
              >
                {/* Video Result */}
                {result.assets.video && (
                  <div className="bg-[#12121a] border border-white/10 rounded-2xl overflow-hidden shadow-2xl group">
                    <div className="p-4 border-b border-white/5 flex justify-between items-center">
                      <div className="flex items-center space-x-2">
                        <Play className="w-4 h-4 text-fuchsia-400" />
                        <h3 className="font-medium text-gray-200">Final Cinematic Video</h3>
                      </div>
                      <a href={result.assets.video} download className="text-gray-400 hover:text-white transition-colors p-2 bg-white/5 rounded-lg hover:bg-white/10">
                        <Download className="w-4 h-4" />
                      </a>
                    </div>
                    <div className="p-4 bg-black">
                      <VideoPlayer src={result.assets.video} />
                    </div>
                  </div>
                )}

                {/* Image and Depth Results */}
                {/* Image and Depth Results */}
                {(result.assets.image || result.assets.depth) && (
                  <div className="bg-[#12121a] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
                    <div className="p-4 border-b border-white/5 flex justify-between items-center">
                      <div className="flex items-center space-x-2">
                        <Sparkles className="w-4 h-4 text-fuchsia-400" />
                        <h3 className="font-medium text-gray-200 text-sm">Visual & Depth Alignment</h3>
                      </div>
                      <div className="flex items-center space-x-2">
                        {result.assets.image && (
                          <a 
                            href={result.assets.image} 
                            download 
                            className="text-xs text-gray-400 hover:text-white transition-colors flex items-center space-x-1.5 px-3 py-1.5 bg-white/5 rounded-lg border border-white/5"
                          >
                            <Download className="w-3.5 h-3.5" />
                            <span>Image</span>
                          </a>
                        )}
                        {result.assets.depth && (
                          <a 
                            href={result.assets.depth} 
                            download 
                            className="text-xs text-gray-400 hover:text-white transition-colors flex items-center space-x-1.5 px-3 py-1.5 bg-white/5 rounded-lg border border-white/5"
                          >
                            <Download className="w-3.5 h-3.5" />
                            <span>Depth Map</span>
                          </a>
                        )}
                      </div>
                    </div>
                    <div className="p-4">
                      {result.assets.image && result.assets.depth ? (
                        <DepthSlider image={result.assets.image} depth={result.assets.depth} />
                      ) : (
                        // Fallback: If only image is available during generation progress
                        <div className="aspect-square bg-gray-900 rounded-xl overflow-hidden relative flex items-center justify-center">
                          <img src={result.assets.image} alt="Base visual" className="w-full h-full object-cover opacity-80" />
                          <div className="absolute inset-0 bg-black/40 backdrop-blur-[2px] flex flex-col items-center justify-center text-center p-4">
                            <Loader2 className="w-8 h-8 text-fuchsia-400 animate-spin mb-3" />
                            <p className="text-sm font-medium text-white">Analyzing 3D Geometry...</p>
                            <p className="text-xs text-gray-400 mt-1">Depth map estimation will unlock comparison slider.</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Audio Result */}
                {result.assets.audio && (
                  <AudioPlayer src={result.assets.audio} />
                )}
              </motion.div>
            ) : (
              <div className="h-full min-h-[400px] border border-white/5 rounded-2xl bg-white/[0.02] flex flex-col items-center justify-center text-center p-8">
                <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-6" />
                <h3 className="text-xl font-display font-medium text-gray-200 mb-2">Synthesizing Reality</h3>
                <p className="text-gray-500 max-w-sm">
                  Our models are currently processing your request. This may take a few moments depending on the complexity.
                </p>
              </div>
            )}
          </AnimatePresence>
        </div>

      </div>
    </div>
  );
}
