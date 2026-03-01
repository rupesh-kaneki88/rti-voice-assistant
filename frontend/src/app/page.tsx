'use client';

import { useState, useEffect } from 'react';
import VoiceRecorder from '@/components/VoiceRecorder';
import RTIForm from '@/components/RTIForm';
import LanguageSelector from '@/components/LanguageSelector';
import { createSession } from '@/lib/api';

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [language, setLanguage] = useState<'en' | 'hi' | 'kn'>('hi');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Create session on mount
    initSession();
  }, [language]);

  const initSession = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const session = await createSession(language);
      setSessionId(session.session_id);
    } catch (err) {
      setError('Failed to create session. Please refresh the page.');
      console.error('Session creation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main 
      className="min-h-screen bg-gray-50 p-4"
      role="main"
      aria-label="RTI Voice Assistant"
    >
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            RTI Voice Assistant
          </h1>
          <p className="text-lg text-gray-600">
            File RTI applications using your voice
          </p>
        </header>

        {/* Language Selector */}
        <div className="mb-6">
          <LanguageSelector
            currentLanguage={language}
            onLanguageChange={setLanguage}
          />
        </div>

        {/* Error Message */}
        {error && (
          <div 
            role="alert" 
            className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6"
          >
            <p>{error}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Initializing session...</p>
          </div>
        )}

        {/* Main Content */}
        {sessionId && !isLoading && (
          <div className="space-y-6">
            {/* Voice Recorder */}
            <section 
              className="bg-white rounded-lg shadow-md p-6"
              aria-labelledby="voice-section-title"
            >
              <h2 id="voice-section-title" className="text-2xl font-semibold mb-4">
                Voice Input
              </h2>
              <VoiceRecorder 
                sessionId={sessionId} 
                language={language}
              />
            </section>

            {/* RTI Form */}
            <section 
              className="bg-white rounded-lg shadow-md p-6"
              aria-labelledby="form-section-title"
            >
              <h2 id="form-section-title" className="text-2xl font-semibold mb-4">
                RTI Application Form
              </h2>
              <RTIForm 
                sessionId={sessionId}
                language={language}
              />
            </section>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>Accessible RTI filing for visually impaired users</p>
          <p className="mt-2">Powered by AWS AI Services</p>
        </footer>
      </div>
    </main>
  );
}
