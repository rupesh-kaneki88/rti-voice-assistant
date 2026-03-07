'use client';

import { useState, useRef, useEffect } from 'react';
import { textToSpeech, haveConversation } from '@/lib/api';
import { FormData } from '@/app/page'; // Import the shared FormData type

interface VoiceRecorderProps {
  sessionId: string;
  language: 'en' | 'hi' | 'kn';
  onFormUpdate: (updates: Partial<FormData>) => void;
}

type AgentState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';


// Declare Web Speech API types
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export default function VoiceRecorderRealtime({ sessionId, language, onFormUpdate }: VoiceRecorderProps) {
  const [agentState, setAgentState] = useState<AgentState>('idle');
  const [error, setError] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState(true);
  
  interface ConversationMessage {
    role: 'user' | 'agent';
    content: string;
  }
  const [conversationHistory, setConversationHistory] = useState<ConversationMessage[]>([]);
  
  const recognitionRef = useRef<any>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const conversationEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // Scroll to the bottom of the conversation history
    conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversationHistory]);

  useEffect(() => {
    // Check if Web Speech API is supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
      setError('Speech recognition not supported in this browser. Please use Chrome or Edge.');
    }
  }, []);

  useEffect(() => {
    // On language change, if we have already greeted, fetch the new guidance message to display
    const updateGuidanceOnLanguageChange = async () => {
      if (conversationHistory.length > 0 && sessionId) {
        try {
          const response = await haveConversation(sessionId, '', language);
          setConversationHistory(prev => [...prev, { role: 'agent', content: response.agent_response }]);
        } catch (err) {
          console.error('Guidance update error:', err);
        }
      }
    };
    updateGuidanceOnLanguageChange();
  }, [language]);

  const getStateMessage = () => {
    switch (agentState) {
      case 'idle':
        return conversationHistory.length > 0 ? 'Ready to listen' : 'Click Speak to start';
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

  const startListening = async () => {
    // First interaction: Greet the user, then start listening
    if (conversationHistory.length === 0 && sessionId) {
      try {
        setAgentState('thinking');
        const response = await haveConversation(sessionId, '', language);
        const greeting = response.agent_response;
        setConversationHistory([{ role: 'agent', content: greeting }]);
        
        setAgentState('speaking');
        await speakText(greeting);

      } catch (err) {
        console.error('Greeting error:', err);
        setError('Could not start the session. Please try again.');
        setAgentState('error');
        setTimeout(() => setAgentState('idle'), 3000);
        return;
      }
    }

    // --- Regular listening logic ---
    try {
      setError(null);
      setAgentState('listening');
      
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      const languageMap: { [key: string]: string } = { 'en': 'en-IN', 'hi': 'hi-IN', 'kn': 'kn-IN' };
      recognition.lang = languageMap[language] || 'hi-IN';
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onresult = async (event: any) => {
        const transcript = event.results[0][0].transcript;
        await processTranscription(transcript);
      };

      recognition.onerror = (event: any) => {
        let errorMessage = 'Speech recognition failed. ';
        switch (event.error) {
          case 'no-speech': errorMessage += 'No speech detected.'; break;
          case 'audio-capture': errorMessage += 'Microphone not accessible.'; break;
          case 'not-allowed': errorMessage += 'Microphone permission denied.'; break;
          default: errorMessage += 'Please try again.';
        }
        setError(errorMessage);
        setAgentState('error');
        setTimeout(() => setAgentState('idle'), 3000);
      };

      recognition.onend = () => {
        if (agentState === 'listening') setAgentState('idle');
      };

      recognitionRef.current = recognition;
      recognition.start();
      
    } catch (err) {
      console.error('Failed to start recognition:', err);
      setError('Failed to start speech recognition.');
      setAgentState('error');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setAgentState('thinking');
    }
  };

  const processTranscription = async (text: string) => {
    try {
      setAgentState('thinking');
      setError(null);
      
      setConversationHistory(prev => [...prev, { role: 'user', content: text }]);
      
      const conversationResponse = await haveConversation(sessionId, text, language);
      const { agent_response, form_updates, is_complete } = conversationResponse;
      
      setConversationHistory(prev => [...prev, { role: 'agent', content: agent_response }]);
      
      if (form_updates && Object.keys(form_updates).length > 0) {
        onFormUpdate(form_updates);
      }
      
      setAgentState('speaking');
      await speakText(agent_response);
      
      if (is_complete) {
        announceToScreenReader('Your RTI application is complete!');
      }
      
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
        const timeout = setTimeout(() => { console.warn("Audio playback timed out."); resolve(); }, 15000);
        audio.onended = () => { clearTimeout(timeout); resolve(); };
        audio.onerror = (e) => { clearTimeout(timeout); reject(e); };
        audio.play().catch(e => { clearTimeout(timeout); reject(e); });
      });
    } catch (err) {
      console.error('TTS or playback error:', err);
    }
  };

  const announceToScreenReader = (message: string) => {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    setTimeout(() => document.body.removeChild(announcement), 1000);
  };

  const isDisabled = agentState === 'thinking' || agentState === 'speaking' || !isSupported;
  const isListening = agentState === 'listening';

  if (!isSupported) {
    return (
      <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded">
        <p className="font-bold">Speech Recognition Not Supported</p>
        <p>Please use Google Chrome or Microsoft Edge for voice input.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Conversation History */}
      <div className="flex-grow h-96 overflow-y-auto p-4 bg-white border border-neutral-200 rounded-lg space-y-4 mb-4">
        {conversationHistory.map((msg, index) => (
          <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs md:max-w-md p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-neutral-200 text-neutral-800'}`}>
              <p className="text-sm">{msg.content}</p>
            </div>
          </div>
        ))}
        <div ref={conversationEndRef} />
      </div>

      {/* Agent Status & Control */}
      <div className="flex-shrink-0">
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={isListening ? stopListening : startListening}
            disabled={isDisabled}
            className={`
              flex items-center justify-center w-20 h-20 rounded-full text-white font-bold
              transition-transform transform focus:outline-none focus:ring-2 focus:ring-offset-2
              disabled:opacity-60 disabled:cursor-not-allowed
              ${!isDisabled && 'hover:scale-105'}
              ${isListening ? 'bg-red-600 focus:ring-red-500' : 'bg-blue-600 focus:ring-blue-500'}
            `}
            aria-label={isListening ? 'Stop listening' : 'Start listening'}
          >
            <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
              {isListening ? (
                <path d="M5 3a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2H5z" />
              ) : (
                <path d="M7 4a3 3 0 0 1 6 0v6a3 3 0 0 1-6 0V4zm1 0a2 2 0 0 1 4 0v6a2 2 0 0 1-4 0V4zm-3 6a1 1 0 0 1 1 1v1a4 4 0 0 0 8 0v-1a1 1 0 1 1 2 0v1a6 6 0 1 1-12 0v-1a1 1 0 0 1 1-1z" />
              )}
            </svg>
          </button>
          <div className="text-left">
            <p className="font-semibold text-lg text-neutral-800">{getStateMessage()}</p>
            <p className="text-neutral-500 text-sm">
              {isListening ? 'Click the square to stop' : 'Click the mic to speak'}
            </p>
          </div>
        </div>
        {error && (
          <p role="alert" className="text-red-600 text-center text-sm mt-2">{error}</p>
        )}
      </div>
    </div>
  );
}
