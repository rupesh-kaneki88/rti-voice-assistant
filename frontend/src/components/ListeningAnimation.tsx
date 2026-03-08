'use client';

export default function ListeningAnimation() {
  return (
    <div className="absolute inset-0 flex items-center justify-center">
      {/* Create 3 expanding rings with different delays */}
      <div className="absolute w-48 h-48 rounded-full border-4 border-green-500/60 animate-listening-pulse"></div>
      <div className="absolute w-48 h-48 rounded-full border-4 border-green-500/60 animate-listening-pulse [animation-delay:0.7s]"></div>
      <div className="absolute w-48 h-48 rounded-full border-4 border-green-500/60 animate-listening-pulse [animation-delay:1.4s]"></div>
    </div>
  );
}
