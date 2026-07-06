import React, { useState, useRef } from 'react';

interface DepthSliderProps {
  image: string;
  depth: string;
}

export default function DepthSlider({ image, depth }: DepthSliderProps) {
  const [sliderPosition, setSliderPosition] = useState(50); // percentage (0 - 100)
  const containerRef = useRef<HTMLDivElement>(null);
  const isDragging = useRef(false);

  const handleMove = (clientX: number) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPosition(percentage);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    // We update on hover or active dragging
    if (e.buttons === 1 || isDragging.current) {
      handleMove(e.clientX);
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    isDragging.current = true;
    handleMove(e.clientX);
  };

  const handleMouseUp = () => {
    isDragging.current = false;
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (e.touches[0]) {
      handleMove(e.touches[0].clientX);
    }
  };

  return (
    <div 
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onTouchMove={handleTouchMove}
      onTouchStart={() => { isDragging.current = true; }}
      onTouchEnd={() => { isDragging.current = false; }}
      className="relative w-full aspect-square rounded-2xl overflow-hidden border border-white/10 select-none cursor-ew-resize bg-gray-950 shadow-inner group animate-in fade-in zoom-in-95 duration-500"
    >
      {/* Base Image (Underneath) */}
      <img 
        src={image} 
        alt="Base visual" 
        className="absolute inset-0 w-full h-full object-cover pointer-events-none"
      />

      {/* Depth Map (On Top, clipped to reveal right side) */}
      <div 
        className="absolute inset-0 w-full h-full pointer-events-none"
        style={{
          clipPath: `polygon(${sliderPosition}% 0, 100% 0, 100% 100%, ${sliderPosition}% 100%)`
        }}
      >
        <img 
          src={depth} 
          alt="Depth map visual" 
          className="w-full h-full object-cover pointer-events-none grayscale border-l border-white/20"
        />
      </div>

      {/* Divider Line */}
      <div 
        className="absolute top-0 bottom-0 w-[2px] bg-gradient-to-b from-fuchsia-500 via-pink-500 to-fuchsia-600 shadow-[0_0_15px_rgba(217,70,239,0.8)] pointer-events-none"
        style={{ left: `${sliderPosition}%` }}
      >
        {/* Slider Handle Knob */}
        <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-9 h-9 rounded-full bg-white border-2 border-fuchsia-500 flex items-center justify-center shadow-[0_0_10px_rgba(0,0,0,0.5)] pointer-events-none transition-transform group-hover:scale-110">
          <div className="flex space-x-0.5">
            <span className="w-[3px] h-3.5 rounded-full bg-fuchsia-500" />
            <span className="w-[3px] h-3.5 rounded-full bg-fuchsia-500" />
          </div>
        </div>
      </div>
      
      {/* Floating Labels */}
      <div className="absolute bottom-4 left-4 bg-black/60 backdrop-blur-md border border-white/10 px-3 py-1 rounded-lg text-xs font-medium tracking-wide text-gray-300 pointer-events-none shadow-md">
        Original Image
      </div>
      <div className="absolute bottom-4 right-4 bg-black/60 backdrop-blur-md border border-white/10 px-3 py-1 rounded-lg text-xs font-medium tracking-wide text-gray-300 pointer-events-none shadow-md">
        Depth Geometry
      </div>
    </div>
  );
}
