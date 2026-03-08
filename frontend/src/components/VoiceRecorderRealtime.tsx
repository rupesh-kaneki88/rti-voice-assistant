'use client';

import { useState, useRef, useEffect } from 'react';
import { textToSpeech, haveConversation } from '@/lib/api';
import { FormData } from '@/app/page';
import { ConversationMessage } from './ConversationView';
import { useTranslation } from '@/hooks/useTranslation';
import { Mic, Square, Bot, BrainCircuit, Loader, Volume2 } from 'lucide-react';

interface VoiceRecorderProps {
  sessionId: string;
  language: 'en' | 'hi' | 'kn';
  onFormUpdate: (updates: Partial<FormData> & { mode?: string }) => void;
  conversationHistory: ConversationMessage[];
  setConversationHistory: React.Dispatch<React.SetStateAction<ConversationMessage[]>>;
  setMode: React.Dispatch<React.SetStateAction<string>>;
}

type AgentState = 'uninitialized' | 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export default function VoiceRecorderRealtime({ 
  sessionId, language, onFormUpdate, conversationHistory, setConversationHistory, setMode 
}: VoiceRecorderProps) {
  const [agentState, setAgentState] = useState<AgentState>('uninitialized');
  const [error, setError] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState(true);
  
  const { t } = useTranslation(language);
  const recognitionRef = useRef<any>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

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
    if (sessionId) {
      try {
        setAgentState('thinking');
        setError(null);
        const response = await haveConversation(sessionId, '', language);
        const greeting = response.agent_response;
        setConversationHistory([{ role: 'agent', content: greeting }]);
        setMode('conversation');
        
        setAgentState('speaking');
        await speakText(greeting);
        setAgentState('idle');
      } catch (err) {
        console.error('Wake up error:', err);
        setError('Could not start the session. Please try again.');
        setAgentState('error');
        setTimeout(() => setAgentState('uninitialized'), 3000);
      }
    }
  };

  const startListening = () => {
    if (agentState !== 'idle') return;

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
        if (event.error === 'not-allowed') msg = 'Microphone permission denied.';
        else if (event.error === 'no-speech') msg = 'No speech was detected.';
        setError(msg);
        setAgentState('error');
        setTimeout(() => setAgentState('idle'), 3000);
      };

      recognition.onend = () => {
        if (agentState === 'listening') setAgentState('idle');
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
    setAgentState('idle');
  };

  const processTranscription = async (text: string) => {
    try {
      setAgentState('thinking');
      setConversationHistory(prev => [...prev, { role: 'user', content: text }]);
      
      const response = await haveConversation(sessionId, text, language);
      const { agent_response, form_updates, mode } = response;
      
      setConversationHistory(prev => [...prev, { role: 'agent', content: agent_response }]);
      onFormUpdate({ ...form_updates, mode });
      
      setAgentState('speaking');
      await speakText(agent_response);
      setAgentState('idle');
      
    } catch (err) {
      console.error('Processing error:', err);
      setError('Failed to process speech. Please try again.');
      setAgentState('error');
      setTimeout(() => setAgentState('idle'), 3000);
    }
  };

  const speakText = async (text: string) => {
    try {
      const audioData = await textToSpeech(text, language);
      const audio = new Audio(`data:audio/mp3;base64,${audioData.audio}`);
      audioRef.current = audio;
      
      await new Promise<void>((resolve, reject) => {
        audio.onended = resolve;
        audio.onerror = reject;
        audio.play().catch(reject);
      });
    } catch (err) {
      console.error('TTS error:', err);
    }
  };

  const getButtonContent = () => {
    switch (agentState) {
      case 'uninitialized': return <><Bot size={32} /><span className="mt-2 text-sm font-semibold">{t('button.wakeUp')}</span></>;
      case 'listening': return <Mic size={48} />;
      case 'speaking': return <Volume2 size={48} />;
      case 'thinking': return <Loader size={48} className="animate-spin-slow" />;
      case 'error': return <Bot size={32} />;
      case 'idle': return <Mic size={48} />;
      default: return <Bot size={32} />;
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
    w-48 h-48 rounded-full flex flex-col items-center justify-center 
    text-white font-bold shadow-2xl transition-all duration-300 ease-in-out 
    transform hover:scale-105 focus:outline-none focus:ring-4
    disabled:opacity-70 disabled:cursor-not-allowed disabled:scale-100
  `;

  const getButtonStateClass = () => {
    switch (agentState) {
      case 'uninitialized': return 'bg-gradient-to-br from-neutral-700 to-neutral-900 focus:ring-neutral-500';
      case 'idle': return 'bg-gradient-to-br from-blue-500 to-blue-700 focus:ring-blue-400';
      case 'listening': return 'bg-gradient-to-br from-green-500 to-green-700 focus:ring-green-400 scale-110';
      case 'speaking': return 'bg-gradient-to-br from-indigo-500 to-indigo-700 focus:ring-indigo-400 animate-pulse';
      case 'thinking': return 'bg-gradient-to-br from-yellow-500 to-yellow-700 focus:ring-yellow-400';
      case 'error': return 'bg-gradient-to-br from-red-500 to-red-700 focus:ring-red-400';
      default: return 'bg-neutral-500';
    }
  };

  const handleClick = () => {
    if (agentState === 'uninitialized') handleWakeUp();
    else if (agentState === 'idle') startListening();
    else if (agentState === 'listening') stopListening();
  };

  if (!isSupported) {
    return (
      <div className="text-center p-4 bg-yellow-100 border-yellow-500 text-yellow-800 rounded-lg">
        <p className="font-bold">Voice input not supported.</p>
        <p>Please use Chrome or Edge on a desktop computer.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center gap-6 text-center" role="region" aria-label="Voice Agent Controls">
      <button
        onClick={handleClick}
        disabled={agentState === 'thinking' || agentState === 'speaking'}
        className={`${buttonClass} ${getButtonStateClass()}`}
        aria-label={agentState === 'listening' ? 'Stop listening' : 'Start listening'}
      >
        {getButtonContent()}
      </button>
      <div className="h-10">
        <p className={`text-lg font-semibold transition-opacity duration-300 ${agentState === 'error' ? 'text-red-600' : 'text-neutral-700'}`}>
          {getStatusText()}
        </p>
      </div>
    </div>
  );
}