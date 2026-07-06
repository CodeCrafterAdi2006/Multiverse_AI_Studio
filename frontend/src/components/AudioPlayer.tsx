import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX } from 'lucide-react';

interface AudioPlayerProps {
  src: string;
}

export default function AudioPlayer({ src }: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressBarRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setIsPlaying(false);
    setCurrentTime(0);
  }, [src]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    setCurrentTime(audioRef.current.currentTime);
  };

  const handleLoadedMetadata = () => {
    if (!audioRef.current) return;
    setDuration(audioRef.current.duration);
  };

  const handleProgressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!audioRef.current) return;
    const newTime = parseFloat(e.target.value);
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const toggleMute = () => {
    if (!audioRef.current) return;
    audioRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const formatTime = (time: number) => {
    if (isNaN(time)) return '0:00';
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  return (
    <div className="bg-[#12121a] border border-white/10 rounded-2xl p-6 shadow-2xl backdrop-blur-xl animate-in fade-in slide-in-from-bottom-4 duration-500">
      <audio
        ref={audioRef}
        src={src}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setIsPlaying(false)}
      />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        {/* Left Side: Playback Control & Waveform Mock */}
        <div className="flex items-center space-x-6">
          <button
            onClick={togglePlay}
            className="w-14 h-14 rounded-full bg-gradient-to-r from-fuchsia-600 to-pink-600 text-white flex items-center justify-center hover:scale-105 active:scale-95 transition-transform shadow-[0_0_15px_rgba(217,70,239,0.4)]"
          >
            {isPlaying ? <Pause className="w-6 h-6 fill-white" /> : <Play className="w-6 h-6 fill-white ml-1" />}
          </button>

          <div>
            <h4 className="font-semibold text-gray-200 text-sm">Ambient Soundscape</h4>
            <p className="text-xs text-gray-500 mt-0.5">Synthesized environment background track</p>
          </div>
        </div>

        {/* Center: Waveform Animation Visualizer */}
        <div className="flex-1 flex items-center justify-center space-x-1.5 h-10 px-4">
          {[...Array(18)].map((_, i) => {
            // Random heights for visual variance
            const height = [16, 28, 12, 34, 18, 40, 24, 30, 14, 38, 20, 32, 10, 26, 16, 36, 12, 22][i];
            return (
              <span
                key={i}
                className="w-[3px] rounded-full bg-gradient-to-t from-fuchsia-500 to-pink-500"
                style={{
                  height: isPlaying ? `${height}px` : '4px',
                  opacity: isPlaying ? 0.8 : 0.2,
                  transition: 'height 0.3s ease, opacity 0.3s ease',
                  animation: isPlaying ? `pulse-bar 1.2s ease-in-out infinite alternate` : 'none',
                  animationDelay: `${i * 0.08}s`
                }}
              />
            );
          })}
        </div>

        {/* Right Side: Timeline & Volume Mute */}
        <div className="flex items-center space-x-4 min-w-[200px] justify-between">
          <span className="text-xs font-mono text-gray-400 w-10 text-right">{formatTime(currentTime)}</span>
          
          <input
            ref={progressBarRef}
            type="range"
            min={0}
            max={duration || 100}
            value={currentTime}
            onChange={handleProgressChange}
            className="flex-1 h-1 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-fuchsia-500"
          />
          
          <span className="text-xs font-mono text-gray-400 w-10">{formatTime(duration)}</span>

          <button onClick={toggleMute} className="text-gray-400 hover:text-white transition-colors">
            {isMuted ? <VolumeX className="w-5 h-5 text-red-400" /> : <Volume2 className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Styled animation definition inside JSX */}
      <style>{`
        @keyframes pulse-bar {
          0% { transform: scaleY(0.4); }
          100% { transform: scaleY(1.1); }
        }
      `}</style>
    </div>
  );
}
