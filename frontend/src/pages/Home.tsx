import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { Sparkles, ArrowRight } from 'lucide-react';
import { generateAssets } from '../lib/api';

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const data = await generateAssets(prompt);
      if (data.job_id) {
        navigate(`/studio/${data.job_id}`);
      }
    } catch (error) {
      console.error('Failed to generate:', error);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated Background Gradients */}
      <div className="absolute inset-0 z-0">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.1, 0.2, 0.1],
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[120px]"
        />
        <motion.div
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.1, 0.15, 0.1],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 1 }}
          className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-blue-600/20 rounded-full blur-[150px]"
        />
      </div>

      {/* Grid Pattern overlay */}
      <div className="absolute inset-0 z-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]">
        <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-fuchsia-400 opacity-20 blur-[100px]"></div>
      </div>

      <div className="relative z-10 w-full max-w-3xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center"
        >
          <div className="inline-flex items-center justify-center space-x-2 bg-white/5 border border-white/10 rounded-full px-4 py-1.5 mb-8 backdrop-blur-sm">
            <Sparkles className="w-4 h-4 text-fuchsia-400" />
            <span className="text-sm font-medium tracking-wide text-gray-300">Multiverse AI Studio</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-display font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60">
            Design entire universes <br className="hidden md:block" /> with a single thought.
          </h1>
          <p className="text-lg text-gray-400 mb-12 max-w-xl mx-auto font-sans">
            Describe your vision. Our multimodal pipeline will generate the visuals, 
            depth geometry, ambient soundscape, and final cinematic video.
          </p>

          <form onSubmit={handleSubmit} className="relative max-w-2xl mx-auto group">
            <div className="absolute -inset-1 bg-gradient-to-r from-fuchsia-600 to-blue-600 rounded-2xl blur opacity-25 group-focus-within:opacity-50 transition duration-1000 group-focus-within:duration-200"></div>
            <div className="relative flex items-center bg-[#0f0f15] border border-white/10 rounded-xl overflow-hidden shadow-2xl">
              <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="A futuristic cyber-monastery in a nebula..."
                className="w-full bg-transparent px-6 py-5 text-lg outline-none placeholder:text-gray-600 text-white font-sans"
                disabled={isSubmitting}
              />
              <button
                type="submit"
                disabled={!prompt.trim() || isSubmitting}
                className="mr-3 px-6 py-3 bg-white text-black font-medium rounded-lg flex items-center space-x-2 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span>{isSubmitting ? 'Igniting...' : 'Create Universe'}</span>
                {!isSubmitting && <ArrowRight className="w-4 h-4" />}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
