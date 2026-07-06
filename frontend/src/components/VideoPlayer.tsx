import React, { useRef, useState, useEffect } from 'react';
import { Play, Pause, RefreshCw, Volume2, VolumeX, Maximize } from 'lucide-react';

interface VideoPlayerProps {
  src: string;
}

export default function VideoPlayer({ src }: VideoPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    setIsPlaying(false);
    setProgress(0);
  }, [src]);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    const percentage = (videoRef.current.currentTime / videoRef.current.duration) * 100;
    setProgress(percentage);
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleFullscreen = () => {
    if (!videoRef.current) return;
    if (videoRef.current.requestFullscreen) {
      videoRef.current.requestFullscreen();
    }
  };

  return (
    <div className="relative aspect-video w-full rounded-2xl overflow-hidden border border-white/10 bg-black group shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-700">
      <video
        ref={videoRef}
        src={src}
        onTimeUpdate={handleTimeUpdate}
        onClick={togglePlay}
        onEnded={() => setIsPlaying(false)}
        loop
        className="w-full h-full object-cover cursor-pointer"
      />

      {/* Dark Overlay gradient at bottom */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

      {/* Floating Center Play Button when paused */}
      {!isPlaying && (
        <button
          onClick={togglePlay}
          className="absolute inset-0 m-auto w-16 h-16 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center backdrop-blur-md border border-white/20 transition-transform scale-95 hover:scale-105 active:scale-95 shadow-[0_0_30px_rgba(0,0,0,0.5)]"
        >
          <Play className="w-8 h-8 fill-white ml-1" />
        </button>
      )}

      {/* Floating Control Bar */}
      <div className="absolute bottom-4 left-4 right-4 bg-black/60 backdrop-blur-md border border-white/10 px-4 py-3 rounded-xl flex items-center justify-between gap-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300 shadow-lg">
        {/* Play / Pause Toggle */}
        <button onClick={togglePlay} className="text-gray-300 hover:text-white transition-colors">
          {isPlaying ? <Pause className="w-5 h-5 fill-white" /> : <Play className="w-5 h-5 fill-white" />}
        </button>

        {/* Progress track */}
        <div className="flex-1 h-1 bg-gray-800 rounded-full overflow-hidden relative">
          <div 
            className="absolute top-0 bottom-0 left-0 bg-gradient-to-r from-fuchsia-500 to-pink-500 rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Control buttons */}
        <div className="flex items-center space-x-4">
          <button onClick={toggleMute} className="text-gray-300 hover:text-white transition-colors">
            {isMuted ? <VolumeX className="w-5 h-5 text-red-400" /> : <Volume2 className="w-5 h-5" />}
          </button>
          
          <button onClick={handleFullscreen} className="text-gray-300 hover:text-white transition-colors">
            <Maximize className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
