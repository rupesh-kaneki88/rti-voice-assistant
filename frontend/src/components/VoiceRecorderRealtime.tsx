'use client';

import { useState, useRef, useEffect } from 'react';
import { textToSpeech, haveConversation } from '@/lib/api';
import { FormData } from '@/app/page';
import { useTranslation } from '@/hooks/useTranslation';
import { Mic, Square, Bot, BrainCircuit, Loader, Volume2 } from 'lucide-react';
import SoundWaveIcon from './SoundWaveIcon'; // Import the new component

interface VoiceRecorderProps {
  sessionId: string;
  language: 'en' | 'hi' | 'kn';
  onFormUpdate: (updates: Partial<FormData> & { mode?: string }) => void;
  // conversationHistory: ConversationMessage[]; // Removed
  // setConversationHistory: React.Dispatch<React.SetStateAction<ConversationMessage[]>>; // Removed
  setMode: React.Dispatch<React.SetStateAction<string>>;
  onNewMessage: (message: { role: 'user' | 'agent'; content: string }) => void; // New prop for sending messages up
}

type AgentState = 'uninitialized' | 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export default function VoiceRecorderRealtime({ 
  sessionId, language, onFormUpdate, setMode, onNewMessage 
}: VoiceRecorderProps) {
  const [agentState, setAgentState] = useState<AgentState>('uninitialized');
  const [error, setError] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState(true);
  
  const { t } = useTranslation(language);
  const recognitionRef = useRef<any>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const agentStateRef = useRef<AgentState>(agentState); // For onend callback

  useEffect(() => {
    agentStateRef.current = agentState; // Keep ref updated
  }, [agentState]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
      setError('Speech recognition not supported. Please use Chrome or Edge.');
    }
  }, []);

  useEffect(() => {
    // Stop any ongoing processes if the session ID changes
    return () => {
      if (recognitionRef.current) recognitionRef.current.abort();
      if (audioRef.current) audioRef.current.pause();
    };
  }, [sessionId]);

  const handleWakeUp = async () => {
    if (!sessionId) return;
    try {
      setAgentState('thinking');
      setError(null);
      const response = await haveConversation(sessionId, '', language);
      const greeting = response.agent_response;
      onNewMessage({ role: 'agent', content: greeting }); // Send message up
      setMode('conversation');
      
      await speakText(greeting);
    } catch (err) {
      console.error('Wake up error:', err);
      setError('Could not start the session. Please try again.');
      setAgentState('error');
      setTimeout(() => setAgentState('uninitialized'), 3000);
    }
  };

  const startListening = () => {
    if (agentState !== 'idle') return; // Only listen if idle

    try {
      setError(null);
      setAgentState('listening');
      
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      const languageMap: { [key: string]: string } = { 'en': 'en-IN', 'hi': 'hi-IN', 'kn': 'kn-IN' };
      recognition.lang = languageMap[language] || 'hi-IN';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        processTranscription(transcript);
      };

      recognition.onerror = (event: any) => {
        let msg = 'Speech recognition failed. ';
        switch (event.error) {
          case 'no-speech': msg += 'No speech detected.'; break;
          case 'audio-capture': msg += 'Microphone not accessible.'; break;
          case 'not-allowed': msg += 'Microphone permission denied.'; break;
          default: msg += 'Please try again.';
        }
        setError(msg);
        setAgentState('error');
        setTimeout(() => setAgentState('idle'), 3000);
      };

      recognition.onend = () => {
        if (agentStateRef.current === 'listening') { // Use ref for up-to-date state
          setAgentState('idle');
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
      
    } catch (err) {
      console.error('Recognition start error:', err);
      setError('Failed to start speech recognition.');
      setAgentState('error');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    // setAgentState('idle'); // Removed to fix TypeScript error
  };

  const processTranscription = async (text: string) => {
    try {
      setAgentState('thinking');
      onNewMessage({ role: 'user', content: text }); // Send message up
      
      const response = await haveConversation(sessionId, text, language);
      const { agent_response, form_updates, mode } = response;
      
      onNewMessage({ role: 'agent', content: agent_response }); // Send message up
      onFormUpdate({ ...form_updates, mode });
      
      await speakText(agent_response);
      
    } catch (err) {
      console.error('Processing error:', err);
      setError('Failed to process speech. Please try again.');
      setAgentState('error');
      setTimeout(() => setAgentState('idle'), 3000);
    }
  };

  const speakText = async (text: string) => {
    setAgentState('speaking');
    try {
      const audioData = await textToSpeech(text, language);
      const audio = new Audio(`data:audio/mp3;base64,${audioData.audio}`);
      audioRef.current = audio;
      
      await new Promise<void>((resolve, reject) => {
        audio.onended = () => {
          setAgentState('idle');
          resolve();
        };
        audio.onerror = (e) => {
          setAgentState('idle');
          reject(e);
        };
        audio.play().catch(e => {
          setAgentState('idle');
          reject(e);
        });
      });
    } catch (err) {
      console.error('TTS error:', err);
      setAgentState('idle');
    }
  };

  const isDisabled = agentState === 'thinking' || agentState === 'speaking' || !isSupported;
  const isListening = agentState === 'listening';

  const getButtonContent = () => {
    switch (agentState) {
      case 'uninitialized': return <Bot size={48} />;
      case 'listening': return <SoundWaveIcon key="listening" state="listening" />;
      case 'speaking': return <SoundWaveIcon key="speaking" state="speaking" />;
      case 'thinking': return <SoundWaveIcon key="thinking" state="thinking" />;
      case 'error': return <Bot size={48} />;
      case 'idle': return <Mic size={48} />;
      default: return <Bot size={48} />;
    }
  };

  const getStatusText = () => {
    switch (agentState) {
      case 'uninitialized': return t('status.uninitialized');
      case 'idle': return t('status.idle');
      case 'listening': return t('status.listening');
      case 'thinking': return t('status.thinking');
      case 'speaking': return t('status.speaking');
      case 'error': return error || t('status.error');
      default: return '';
    }
  };

  const buttonClass = `
    flex items-center justify-center w-24 h-24 rounded-full text-white font-bold
    transition-all duration-300 ease-in-out transform focus:outline-none focus:ring-4 focus:ring-offset-2
    disabled:opacity-60 disabled:cursor-not-allowed
    ${!isDisabled && 'hover:scale-105'}
    ${isListening ? 'bg-red-600 focus:ring-red-400' : 'bg-blue-600 focus:ring-blue-400'}
    shadow-lg
  `;

  const handleClick = () => {
    if (agentState === 'uninitialized') handleWakeUp();
    else if (agentState === 'idle') startListening();
    else if (agentState === 'listening') stopListening();
  };

  if (!isSupported) {
    return (
      <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded">
        <p className="font-bold">Speech Recognition Not Supported</p>
        <p>Please use Google Chrome or Microsoft Edge for voice input.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full items-center justify-center">
      {/* Agent Status & Control */}
      <div className="flex-shrink-0 flex flex-col items-center justify-center gap-6">
        <button
          onClick={handleClick}
          disabled={isDisabled}
          className={buttonClass}
          aria-label={isListening ? 'Stop listening' : 'Start listening'}
        >
          {getButtonContent()}
        </button>
        <div className="text-center">
          <p className="font-semibold text-xl text-neutral-800">{getStatusText()}</p>
          <p className="text-neutral-500 text-md">
            {isListening ? 'Click the button to stop' : 'Click the button to speak'}
          </p>
        </div>
        {error && (
          <p role="alert" className="text-red-600 text-center text-sm mt-2">{error}</p>
        )}
      </div>
    </div>
  );
}
