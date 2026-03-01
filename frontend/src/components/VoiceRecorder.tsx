'use client';

import { useState, useRef } from 'react';
import { transcribeAudio, textToSpeech } from '@/lib/api';

interface VoiceRecorderProps {
  sessionId: string;
  language: 'en' | 'hi' | 'kn';
}

type AgentState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';

export default function VoiceRecorder({ sessionId, language }: VoiceRecorderProps) {
  const [agentState, setAgentState] = useState<AgentState>('idle');
  const [transcription, setTranscription] = useState<string>('');
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const getStateMessage = () => {
    switch (agentState) {
      case 'idle':
        return 'Ready to listen';
      case 'listening':
        return 'Listening... Speak now';
      case 'thinking':
        return 'Processing your speech...';
      case 'speaking':
        return 'Speaking response...';
      case 'error':
        return 'Error occurred';
      default:
        return '';
    }
  };

  const startRecording = async () => {
    try {
      setError(null);
      setTranscription('');
      setAgentState('listening');
      setStatusMessage('Listening... Speak now');
      
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
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      
      // Announce to screen readers
      announceToScreenReader('Listening. Please speak now.');
    } catch (err) {
      setError('Failed to access microphone. Please check permissions.');
      setAgentState('error');
      console.error('Recording error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && agentState === 'listening') {
      mediaRecorderRef.current.stop();
      setAgentState('thinking');
      setStatusMessage('Processing your speech...');
      announceToScreenReader('Processing your speech. Please wait.');
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    try {
      setError(null);

      // Convert blob to base64
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      
      reader.onloadend = async () => {
        const base64Audio = reader.result?.toString().split(',')[1];
        
        if (!base64Audio) {
          throw new Error('Failed to convert audio');
        }

        // Transcribe audio
        const result = await transcribeAudio(base64Audio, language);
        setTranscription(result.text);
        
        // Announce transcription
        announceToScreenReader(`I heard: ${result.text}`);
        
        // Speak the transcription back
        setAgentState('speaking');
        setStatusMessage('Speaking response...');
        await speakText(result.text);
        
        // Return to idle
        setAgentState('idle');
        setStatusMessage('Ready to listen');
      };
    } catch (err) {
      setError('Failed to process audio. Please try again.');
      setAgentState('error');
      setStatusMessage('Error occurred');
      console.error('Processing error:', err);
      
      // Return to idle after error
      setTimeout(() => {
        setAgentState('idle');
        setStatusMessage('Ready to listen');
      }, 3000);
    }
  };

  const speakText = async (text: string) => {
    try {
      const audioData = await textToSpeech(text, language);
      
      // Convert base64 to audio and play
      const audio = new Audio(`data:audio/mp3;base64,${audioData.audio}`);
      audioRef.current = audio;
      
      // Wait for audio to finish
      await new Promise((resolve, reject) => {
        audio.onended = resolve;
        audio.onerror = reject;
        audio.play();
      });
    } catch (err) {
      console.error('TTS error:', err);
    }
  };

  const announceToScreenReader = (message: string) => {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  };

  const isDisabled = agentState === 'thinking' || agentState === 'speaking';
  const isListening = agentState === 'listening';

  return (
    <div className="space-y-6">
      {/* Agent Status Indicator */}
      <div className="text-center">
        <div className="inline-flex items-center gap-3 bg-gray-100 px-6 py-3 rounded-full">
          {/* Status Icon */}
          <div className={`
            w-3 h-3 rounded-full
            ${agentState === 'idle' ? 'bg-gray-400' : ''}
            ${agentState === 'listening' ? 'bg-red-500 animate-pulse' : ''}
            ${agentState === 'thinking' ? 'bg-yellow-500 animate-pulse' : ''}
            ${agentState === 'speaking' ? 'bg-green-500 animate-pulse' : ''}
            ${agentState === 'error' ? 'bg-red-600' : ''}
          `}></div>
          
          {/* Status Text */}
          <span className="font-medium text-gray-700">
            {getStateMessage()}
          </span>
        </div>
      </div>

      {/* Main Voice Button */}
      <div className="flex flex-col items-center gap-4">
        <button
          onClick={isListening ? stopRecording : startRecording}
          disabled={isDisabled}
          className={`
            relative w-32 h-32 rounded-full text-white font-bold text-xl
            transition-all duration-300 transform
            focus:outline-none focus:ring-4 focus:ring-offset-4
            disabled:opacity-50 disabled:cursor-not-allowed
            ${!isDisabled && 'hover:scale-110'}
            ${isListening 
              ? 'bg-red-600 focus:ring-red-500 shadow-lg shadow-red-500/50' 
              : 'bg-blue-600 focus:ring-blue-500 shadow-lg shadow-blue-500/50'
            }
            ${agentState === 'thinking' && 'animate-pulse'}
          `}
          aria-label={isListening ? 'Stop speaking' : 'Start speaking'}
          aria-pressed={isListening}
          aria-disabled={isDisabled}
        >
          {/* Microphone Icon */}
          <div className="flex flex-col items-center justify-center">
            <span className="text-5xl mb-1">
              {isListening ? '⏸️' : '🎤'}
            </span>
            <span className="text-sm font-semibold">
              {isListening ? 'Stop' : 'Speak'}
            </span>
          </div>
          
          {/* Pulsing Ring for Listening State */}
          {isListening && (
            <div className="absolute inset-0 rounded-full border-4 border-red-400 animate-ping"></div>
          )}
        </button>

        {/* Action Text */}
        <p className="text-gray-600 text-center font-medium">
          {isListening ? 'Click to stop speaking' : 'Click to start speaking'}
        </p>
      </div>

      {/* Thinking Indicator */}
      {agentState === 'thinking' && (
        <div className="text-center py-4" role="status" aria-live="polite">
          <div className="flex justify-center items-center gap-2">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
          <p className="mt-3 text-gray-600 font-medium">Thinking...</p>
        </div>
      )}

      {/* Speaking Indicator */}
      {agentState === 'speaking' && (
        <div className="text-center py-4" role="status" aria-live="polite">
          <div className="flex justify-center items-center gap-1">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="w-1 bg-green-600 rounded-full animate-pulse"
                style={{
                  height: `${Math.random() * 20 + 10}px`,
                  animationDelay: `${i * 100}ms`,
                }}
              ></div>
            ))}
          </div>
          <p className="mt-3 text-gray-600 font-medium">Speaking...</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div 
          role="alert" 
          className="bg-red-100 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded"
        >
          <div className="flex items-center gap-2">
            <span className="text-xl">⚠️</span>
            <p className="font-medium">{error}</p>
          </div>
        </div>
      )}

      {/* Transcription Result */}
      {transcription && (
        <div 
          className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-lg p-4 shadow-sm"
          role="region"
          aria-label="What I heard"
        >
          <div className="flex items-start gap-3">
            <span className="text-2xl">💬</span>
            <div className="flex-1">
              <h3 className="font-semibold text-blue-900 mb-1">You said:</h3>
              <p className="text-gray-800 text-lg leading-relaxed">{transcription}</p>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="text-center text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
        <p>
          🎯 Speak in <strong>{language === 'hi' ? 'Hindi (हिंदी)' : language === 'kn' ? 'Kannada (ಕನ್ನಡ)' : 'English'}</strong>
        </p>
        <p className="mt-1">The assistant will listen, process, and respond to you</p>
      </div>
    </div>
  );
}
