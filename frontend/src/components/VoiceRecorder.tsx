'use client';

import { useState, useRef, useEffect } from 'react';
import { transcribeAudio, textToSpeech } from '@/lib/api';

// SVG Icon Components
const MicIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm5 10.5a.5.5 0 01.5.5v.5a.5.5 0 01-1 0v-.5a.5.5 0 01.5-.5zM5 10a.5.5 0 00-1 0v1a.5.5 0 001 0v-1zm1 2.5a.5.5 0 01.5.5v.5a.5.5 0 01-1 0v-.5a.5.5 0 01.5-.5zM10 18a5 5 0 005-5h-1a4 4 0 01-8 0H5a5 5 0 005 5zm-2.5-4.5a.5.5 0 00-1 0v.5a.5.5 0 001 0v-.5z" clipRule="evenodd" />
  </svg>
);

const StopIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1zm4 0a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
  </svg>
);

const AlertIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM10 13a1 1 0 110-2 1 1 0 010 2zm-1-8a1 1 0 00-1 1v3a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
  </svg>
);

const ChatIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-brand-blue" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M18 5v8a2 2 0 01-2 2h-5l-5 4v-4H4a2 2 0 01-2-2V5a2 2 0 012-2h12a2 2 0 012 2zM7 8H5v2h2V8zm2 0h2v2H9V8zm6 0h-2v2h2V8z" clipRule="evenodd" />
  </svg>
);


interface VoiceRecorderProps {
  sessionId: string;
  language: 'en' | 'hi' | 'kn';
}

type AgentState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';

export default function VoiceRecorder({ sessionId, language, onFormDataExtracted }: VoiceRecorderProps) {
  const [agentState, setAgentState] = useState<AgentState>('idle');
  const [transcription, setTranscription] = useState<string>('');
  const [statusMessage, setStatusMessage] = useState<string>('Ready to assist');
  const [error, setError] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Reset state when language changes
    setAgentState('idle');
    setTranscription('');
    setError(null);
    setStatusMessage('Ready to assist');
  }, [language]);

  const startRecording = async () => {
    if (agentState === 'speaking') {
      audioRef.current?.pause();
      audioRef.current = null;
    }
    try {
      setError(null);
      setTranscription('');
      setAgentState('listening');
      setStatusMessage('Listening...');
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await processAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
    } catch (err) {
      setError('Microphone access denied. Please enable it in your browser settings.');
      setAgentState('error');
      console.error('Recording error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && agentState === 'listening') {
      mediaRecorderRef.current.stop();
      setAgentState('thinking');
      setStatusMessage('Thinking...');
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    try {
      setError(null);
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      
      reader.onloadend = async () => {
        const base64Audio = reader.result?.toString().split(',')[1];
        if (!base64Audio) throw new Error('Failed to convert audio');

        const result = await transcribeAudio(base64Audio, language);
        setTranscription(result.text);
        
        setAgentState('speaking');
        setStatusMessage('Responding...');
        await speakText(result.text);
        
        setAgentState('idle');
        setStatusMessage('Ready to assist');
      };
    } catch (err) {
      setError('Could not process audio. Please try again.');
      setAgentState('error');
      console.error('Processing error:', err);
    }
  };

  const speakText = async (text: string) => {
    try {
      const audioData = await textToSpeech(text, language);
      const audio = new Audio(`data:audio/mp3;base64,${audioData.audio}`);
      audioRef.current = audio;
      
      await new Promise((resolve, reject) => {
        audio.onended = resolve;
        audio.onerror = reject;
        audio.play();
      });
    } catch (err) {
      console.error('TTS error:', err);
      setError('Could not play audio response.');
      setAgentState('error');
    }
  };

  const isDisabled = agentState === 'thinking';
  const isListening = agentState === 'listening';

  const getAgentStateIndicator = () => {
    switch (agentState) {
      case 'listening':
        return (
          <div className="flex flex-col items-center">
            <div className="relative w-24 h-24">
              <div className="absolute inset-0 rounded-full bg-red-500 animate-pulse-ring"></div>
              <div className="absolute inset-0 rounded-full bg-red-500 opacity-75"></div>
            </div>
            <p className="mt-4 text-red-500 font-semibold">Listening</p>
          </div>
        );
      case 'thinking':
        return (
          <div className="flex flex-col items-center">
            <div className="flex items-center justify-center h-24 w-24">
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-brand-blue rounded-full animate-thinking-dot" style={{ animationDelay: '0s' }}></div>
                <div className="w-3 h-3 bg-brand-blue rounded-full animate-thinking-dot" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-3 h-3 bg-brand-blue rounded-full animate-thinking-dot" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
            <p className="mt-4 text-brand-blue font-semibold">Thinking...</p>
          </div>
        );
      case 'speaking':
        return (
          <div className="flex flex-col items-center">
            <div className="flex items-end justify-center h-24 w-24 space-x-1">
              <div className="w-2 h-8 bg-brand-green rounded-full animate-wave" style={{ animationDelay: '0s' }}></div>
              <div className="w-2 h-12 bg-brand-green rounded-full animate-wave" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-8 bg-brand-green rounded-full animate-wave" style={{ animationDelay: '0.4s' }}></div>
              <div className="w-2 h-10 bg-brand-green rounded-full animate-wave" style={{ animationDelay: '0.6s' }}></div>
            </div>
            <p className="mt-4 text-brand-green font-semibold">Speaking...</p>
          </div>
        );
      default: // idle or error
        return (
          <div className="flex flex-col items-center">
            <div className="w-24 h-24 rounded-full bg-neutral-200 flex items-center justify-center">
              <div className="w-4 h-4 rounded-full bg-neutral-400"></div>
            </div>
            <p className="mt-4 text-neutral-500 font-semibold">{agentState === 'error' ? 'Error' : 'Idle'}</p>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Agent Status Visualizer */}
      <div className="flex justify-center items-center h-40 bg-neutral-100 rounded-lg">
        {getAgentStateIndicator()}
      </div>

      {/* Main Voice Button */}
      <div className="flex flex-col items-center gap-2">
        <button
          onClick={isListening ? stopRecording : startRecording}
          disabled={isDisabled}
          className={`
            w-24 h-24 rounded-full text-white font-bold
            flex items-center justify-center
            transition-all duration-300 transform
            focus:outline-none focus:ring-4 focus:ring-offset-2
            disabled:opacity-60 disabled:cursor-not-allowed
            ${isListening
              ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
              : 'bg-brand-blue hover:bg-brand-blue-light focus:ring-brand-blue'
            }
            ${!isDisabled && 'hover:scale-105'}
          `}
          aria-label={isListening ? 'Stop recording' : 'Start recording'}
        >
          {isListening ? <StopIcon /> : <MicIcon />}
        </button>
        <p className="text-neutral-600 text-sm font-medium">
          {isListening ? 'Tap to stop' : 'Tap to speak'}
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div role="alert" className="bg-red-100 border-l-4 border-red-500 text-red-800 p-4 rounded-md flex items-center gap-3">
          <AlertIcon />
          <p className="font-semibold">{error}</p>
        </div>
      )}

      {/* Transcription Result */}
      {transcription && (
        <div className="bg-neutral-100 border-l-4 border-brand-blue p-4 rounded-md" role="region" aria-label="Transcription">
          <div className="flex items-start gap-3">
            <ChatIcon />
            <div>
              <h3 className="font-bold text-neutral-800 mb-1">You said:</h3>
              <p className="text-neutral-700">{transcription}</p>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="text-center text-sm text-neutral-500 bg-neutral-100 rounded-lg p-3">
        <p>
          Speak in <strong>{language === 'hi' ? 'Hindi (हिंदी)' : language === 'kn' ? 'Kannada (ಕನ್ನಡ)' : 'English'}</strong>.
        </p>
        <p className="mt-1">The assistant will guide you through the RTI filing process.</p>
      </div>
    </div>
  );
}
