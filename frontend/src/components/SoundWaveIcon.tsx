'use client';

import React from 'react';

interface SoundWaveIconProps {
  color?: string;
  width?: string;
  height?: string;
  state: 'listening' | 'speaking' | 'thinking';
}

const SoundWaveIcon: React.FC<SoundWaveIconProps> = ({ color = 'currentColor', width = '24', height = '24', state }) => {
  const barClass = `absolute bottom-0 w-1.5 rounded-full ${color}`;

  const getAnimationClass = (index: number) => {
    if (state === 'listening') {
      return `animate-wave-listening animation-delay-${index}`;
    } else if (state === 'speaking') {
      return `animate-wave-speaking animation-delay-${index}`;
    } else if (state === 'thinking') {
      return `animate-wave-thinking animation-delay-${index}`;
    }
    return '';
  };

  return (
    <div className="relative flex items-end justify-between overflow-hidden" style={{ width, height }}>
      <div className={`${barClass} h-1/4 left-0 ${getAnimationClass(1)}`}></div>
      <div className={`${barClass} h-1/2 left-1/4 ${getAnimationClass(2)}`}></div>
      <div className={`${barClass} h-full left-1/2 ${getAnimationClass(3)}`}></div>
      <div className={`${barClass} h-1/2 left-3/4 ${getAnimationClass(4)}`}></div>
      <div className={`${barClass} h-1/4 right-0 ${getAnimationClass(5)}`}></div>
    </div>
  );
};

export default SoundWaveIcon;