'use client';

export default function SpeakingAnimation() {
  return (
    <div className="flex items-center justify-center space-x-2">
      <div className="w-2 h-8 bg-green-500 animate-wave"></div>
      <div className="w-2 h-8 bg-green-500 animate-wave [animation-delay:0.2s]"></div>
      <div className="w-2 h-8 bg-green-500 animate-wave [animation-delay:0.4s]"></div>
      <div className="w-2 h-8 bg-green-500 animate-wave [animation-delay:0.6s]"></div>
      <div className="w-2 h-8 bg-green-500 animate-wave [animation-delay:0.8s]"></div>
    </div>
  );
}
