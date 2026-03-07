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
  const [transcription, setTranscription] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState(true);
  const [agentMessage, setAgentMessage] = useState<string>('');
  
  const recognitionRef = useRef<any>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const hasGreetedRef = useRef(false);

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
      if (hasGreetedRef.current && sessionId) {
        try {
          const response = await haveConversation(sessionId, '', language);
          setAgentMessage(response.agent_response);
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
        return hasGreetedRef.current ? 'Ready to listen' : 'Click Speak to start';
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
    if (!hasGreetedRef.current && sessionId) {
      hasGreetedRef.current = true;
      try {
        setAgentState('thinking');
        const response = await haveConversation(sessionId, '', language);
        const greeting = response.agent_response;
        setAgentMessage(greeting);
        
        // Speak the greeting (now safely inside a user-initiated event)
        setAgentState('speaking');
        await speakText(greeting);

        // Fall through to listening state after speaking
      } catch (err) {
        console.error('Greeting error:', err);
        setError('Could not start the session. Please try again.');
        setAgentState('error');
        setTimeout(() => setAgentState('idle'), 3000);
        return; // Stop if greeting fails
      }
    }

    // --- Regular listening logic ---
    try {
      setError(null);
      setTranscription('');
      setAgentState('listening');
      
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      // Configure recognition
      const languageMap: { [key: string]: string } = {
        'en': 'en-IN',
        'hi': 'hi-IN',
        'kn': 'kn-IN'
      };
      
      recognition.lang = languageMap[language] || 'hi-IN';
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        console.log('Speech recognition started');
        announceToScreenReader('Listening. Please speak now.');
      };

      recognition.onresult = async (event: any) => {
        const transcript = event.results[0][0].transcript;
        const confidence = event.results[0][0].confidence;
        
        console.log('Transcript:', transcript, 'Confidence:', confidence);
        setTranscription(transcript);
        
        // Process the transcription
        await processTranscription(transcript);
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        
        let errorMessage = 'Speech recognition failed. ';
        switch (event.error) {
          case 'no-speech':
            errorMessage += 'No speech detected. Please try again.';
            break;
          case 'audio-capture':
            errorMessage += 'Microphone not accessible.';
            break;
          case 'not-allowed':
            errorMessage += 'Microphone permission denied.';
            break;
          default:
            errorMessage += 'Please try again.';
        }
        
        setError(errorMessage);
        setAgentState('error');
        
        setTimeout(() => {
          setAgentState('idle');
        }, 3000);
      };

      recognition.onend = () => {
        console.log('Speech recognition ended');
        if (agentState === 'listening') {
          setAgentState('idle');
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
      
    } catch (err) {
      console.error('Failed to start recognition:', err);
      setError('Failed to start speech recognition. Please try again.');
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
      
      announceToScreenReader(`I heard: ${text}`);
      
      // Have conversation with agent
      const conversationResponse = await haveConversation(sessionId, text, language);
      
      const agentResponse = conversationResponse.agent_response;
      const formUpdates = conversationResponse.form_updates;
      const isComplete = conversationResponse.is_complete;
      
      // Update agent message display
      setAgentMessage(agentResponse);
      
      // Notify parent if form was updated
      if (formUpdates && Object.keys(formUpdates).length > 0) {
        announceToScreenReader('Form fields updated automatically');
        onFormUpdate(formUpdates);
      }
      
      // Speak the agent's response
      setAgentState('speaking');
      await speakText(agentResponse);
      
      // If form is complete, notify user
      if (isComplete) {
        announceToScreenReader('Your RTI application is complete! You can now download it.');
      }
      
      // Return to idle
      setAgentState('idle');
      
    } catch (err) {
      console.error('Processing error:', err);
      setError('Failed to process speech. Please try again.');
      setAgentState('error');
      
      setTimeout(() => {
        setAgentState('idle');
      }, 3000);
    }
  };

  const speakText = async (text: string) => {
    try {
      const audioData = await textToSpeech(text, language);
      const audio = new Audio(`data:audio/mp3;base64,${audioData.audio}`);
      audioRef.current = audio;
      
      // Play audio and add a timeout to prevent getting stuck
      await new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          console.warn("Audio playback timed out. Resolving to continue flow.");
          resolve();
        }, 15000); // 15-second timeout

        audio.onended = () => {
          clearTimeout(timeout);
          resolve();
        };
        audio.onerror = (e) => {
          clearTimeout(timeout);
          console.error("Audio playback error", e);
          reject(e); // Reject on error
        };
        
        audio.play().catch(e => {
          clearTimeout(timeout);
          console.error("Audio play() failed", e);
          reject(e); // Reject if play itself fails
        });
      });
    } catch (err) {
      console.error('TTS or playback error:', err);
      // We don't re-throw here. If speaking fails, the agent should still
      // be able to listen for the next command.
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

  const isDisabled = agentState === 'thinking' || agentState === 'speaking' || !isSupported;
  const isListening = agentState === 'listening';

  if (!isSupported) {
    return (
      <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
        <div className="flex items-center gap-2">
          <span className="text-2xl">⚠️</span>
          <div>
            <p className="font-semibold text-yellow-800">Speech Recognition Not Supported</p>
            <p className="text-yellow-700 text-sm mt-1">
              Please use Google Chrome or Microsoft Edge browser for voice input.
            </p>
          </div>
        </div>
      </div>
    );
  }

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
          onClick={isListening ? stopListening : startListening}
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
          {isListening ? 'Speak now, click to stop' : 'Click to start speaking'}
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
          <p className="mt-3 text-gray-600 font-medium">Processing and filling form...</p>
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

      {/* Agent Response */}
      {agentMessage && (
        <div 
          className="bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500 rounded-lg p-4 shadow-sm"
          role="region"
          aria-label="Agent response"
        >
          <div className="flex items-start gap-3">
            <span className="text-2xl">🤖</span>
            <div className="flex-1">
              <h3 className="font-semibold text-green-900 mb-1">RTI Assistant:</h3>
              <p className="text-gray-800 text-lg leading-relaxed">{agentMessage}</p>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="text-center text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
        <p>
          🎯 Speak in <strong>{language === 'hi' ? 'Hindi (हिंदी)' : language === 'kn' ? 'Kannada (ಕನ್ನಡ)' : 'English'}</strong>
        </p>
        <p className="mt-1">Real-time speech recognition • Auto-fills form • Speaks back to you</p>
      </div>
    </div>
  );
}
