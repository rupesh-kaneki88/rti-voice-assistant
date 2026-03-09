'use client';

import React from 'react';

interface SoundWaveIconProps {
  state: 'listening' | 'speaking' | 'thinking';
}

const SoundWaveIcon: React.FC<SoundWaveIconProps> = ({ state }) => {
  if (state === 'listening') {
    return (
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="absolute w-24 h-24 rounded-full border-4 border-blue-500/60 animate-listening-pulse"></div>
        <div className="absolute w-24 h-24 rounded-full border-4 border-blue-500/60 animate-listening-pulse [animation-delay:0.7s]"></div>
        <div className="absolute w-24 h-24 rounded-full border-4 border-blue-500/60 animate-listening-pulse [animation-delay:1.4s]"></div>
      </div>
    );
  }

  if (state === 'speaking') {
    return (
      <div className="flex items-center opacity-30 justify-center space-x-1">
        <div className="w-1 h-10 bg-gray-100 animate-wave [animation-delay:0.1s]"></div>
        <div className="w-1 h-10 bg-gray-100 animate-wave [animation-delay:0.2s]"></div>
        <div className="w-1 h-10 bg-gray-100 animate-wave [animation-delay:0.3s]"></div>
        <div className="w-1 h-10 bg-gray-100 animate-wave [animation-delay:0.4s]"></div>
        <div className="w-1 h-10 bg-gray-100 animate-wave [animation-delay:0.5s]"></div>
        <div className="w-1 h-10 bg-gray-100 animate-wave [animation-delay:0.6s]"></div>
        <div className="w-1 h-10 bg-gray-100 animate-wave [animation-delay:0.7s]"></div>
        <div className="w-1 h-10 bg-gray-100 animate-wave [animation-delay:0.8s]"></div>
        <div className="w-1 h-10 bg-gray-100 animate-wave [animation-delay:0.9s]"></div>
      </div>
    );
  }

  if (state === 'thinking') {
    return (
      <div className="flex items-center justify-center h-24 w-24">
        <div className="flex space-x-2">
          <div className="w-3 h-3 bg-blue-600 rounded-full animate-thinking-dot"></div>
          <div className="w-3 h-3 bg-blue-600 rounded-full animate-thinking-dot [animation-delay:0.2s]"></div>
          <div className="w-3 h-3 bg-blue-600 rounded-full animate-thinking-dot [animation-delay:0.4s]"></div>
        </div>
      </div>
    );
  }

  return null;
};

export default SoundWaveIcon;
