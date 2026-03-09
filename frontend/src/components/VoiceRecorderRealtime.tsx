'use client';

import { useState, useRef, useEffect } from 'react';
import { textToSpeech, haveConversation } from '@/client-lib/api';
import { FormData } from '@/app/page';
import { useTranslation } from '@/hooks/useTranslation';
import { Mic, Bot, StopCircle, RefreshCw, Gauge } from 'lucide-react';
import SoundWaveIcon from './SoundWaveIcon';

interface VoiceRecorderProps {
  sessionId: string;
  language: 'en' | 'hi' | 'kn';
  onFormUpdate: (updates: Partial<FormData> & { mode?: string }) => void;
  setMode: React.Dispatch<React.SetStateAction<string>>;
  onNewMessage: (message: { role: 'user' | 'agent'; content: string }) => void;
}

type AgentState = 'uninitialized' | 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';
type PlaybackSpeed = 1 | 1.5 | 2;

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
  const [lastSpokenText, setLastSpokenText] = useState<string>('');
  const [playbackSpeed, setPlaybackSpeed] = useState<PlaybackSpeed>(1);
  
  const { t } = useTranslation(language);
  const recognitionRef = useRef<any>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const agentStateRef = useRef<AgentState>(agentState);

  useEffect(() => {
    agentStateRef.current = agentState;
  }, [agentState]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = playbackSpeed;
    }
  }, [playbackSpeed]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
      setError('Speech recognition not supported. Please use Chrome or Edge.');
    }
  }, []);

  useEffect(() => {
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
      onNewMessage({ role: 'agent', content: greeting });
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
        if (agentStateRef.current === 'listening') {
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
  };

  const processTranscription = async (text: string) => {
    try {
      setAgentState('thinking');
      onNewMessage({ role: 'user', content: text });
      const response = await haveConversation(sessionId, text, language);
      const { agent_response, form_updates, mode } = response;
      onNewMessage({ role: 'agent', content: agent_response });
      onFormUpdate({ ...form_updates, mode });
      await speakText(agent_response);
    } catch (err) {
      console.error('Processing error:', err);
      setError('Failed to process speech. Please try again.');
      setAgentState('error');
      setTimeout(() => setAgentState('idle'), 3000);
    }
  };

  const stopSpeaking = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setAgentState('idle');
  };

  const speakText = async (textToSpeak: string) => {
    if (audioRef.current) {
      stopSpeaking();
    }
    if (!textToSpeak) return;
    setLastSpokenText(textToSpeak);
    setAgentState('speaking');
    try {
      const audioData = await textToSpeech(textToSpeak, language);
      const audio = new Audio(`data:audio/mp3;base64,${audioData.audio}`);
      audio.playbackRate = playbackSpeed;
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

  const handleRepeat = () => {
    if (lastSpokenText) {
      speakText(lastSpokenText);
    }
  };

  const toggleSpeed = () => {
    const speeds: PlaybackSpeed[] = [1, 1.5, 2];
    const currentIndex = speeds.indexOf(playbackSpeed);
    const nextIndex = (currentIndex + 1) % speeds.length;
    setPlaybackSpeed(speeds[nextIndex]);
  };

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

  const handleClick = () => {
    if (agentState === 'uninitialized') handleWakeUp();
    else if (agentState === 'idle') startListening();
    else if (agentState === 'listening') stopListening();
    else if (agentState === 'speaking') stopSpeaking();
  };

  const buttonClass = `
    flex items-center justify-center w-24 h-24 rounded-full text-white font-bold
    transition-all duration-300 ease-in-out transform focus:outline-none focus:ring-4 focus:ring-offset-2
    disabled:opacity-60 disabled:cursor-not-allowed
    ${agentState !== 'thinking' && 'hover:scale-105'}
    ${agentState === 'listening' || agentState === 'speaking' ? 'bg-red-600 focus:ring-red-400' : 'bg-blue-600 focus:ring-blue-400'}
    shadow-lg
  `;

  const getInstructionText = () => {
    switch (agentState) {
      case 'listening':
        return t('status.instruction_stop_listening');
      case 'speaking':
        return t('status.instruction_stop_speaking');
      default:
        return t('status.instruction_speak');
    }
  };

  return (
    <div className="flex flex-col h-full items-center justify-center">
      <div className="flex-shrink-0 flex flex-col items-center justify-center gap-6">
        <div className="relative">
          <button
            onClick={handleClick}
            disabled={agentState === 'thinking'}
            className={buttonClass}
            aria-label={agentState === 'listening' ? 'Stop listening' : agentState === 'speaking' ? 'Stop speaking' : 'Start listening'}
          >
            {getButtonContent()}
            {agentState === 'speaking' && <StopCircle size={38} className="absolute opacity-90" />}
          </button>
        </div>
        <div className="text-center">
          <p className="font-semibold text-xl text-neutral-800">{getStatusText()}</p>
          <p className="text-neutral-500 text-md">
            {getInstructionText()}
          </p>
        </div>
        
        {/* Audio Controls */}
        <div className="flex items-center justify-center gap-4 h-10">
          {(agentState === 'speaking' || (agentState === 'idle' && lastSpokenText)) && (
            <>
              <button onClick={handleRepeat} className="p-2 rounded-full bg-neutral-200 hover:bg-neutral-300 transition-colors" title="Repeat">
                <RefreshCw size={20} />
              </button>
              <button onClick={toggleSpeed} className="p-2 rounded-full bg-neutral-200 hover:bg-neutral-300 transition-colors flex items-center gap-1" title="Toggle speed">
                <Gauge size={20} />
                <span className="text-xs font-semibold">{playbackSpeed}x</span>
              </button>
            </>
          )}
        </div>

        {error && (
          <p role="alert" className="text-red-600 text-center text-sm mt-2">{error}</p>
        )}
      </div>
    </div>
  );
}
