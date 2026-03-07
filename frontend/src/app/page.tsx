'use client';

import { useState, useEffect } from 'react';
import VoiceRecorderRealtime from '@/components/VoiceRecorderRealtime';
import RTIForm from '@/components/RTIForm';
import LanguageSelector from '@/components/LanguageSelector';
import { createSession, getForm } from '@/lib/api';

// Define FormData type to be shared
export interface FormData {
  applicant_name?: string;
  address?: string;
  information_sought?: string;
  department?: string;
  reason?: string;
}

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [language, setLanguage] = useState<'en' | 'hi' | 'kn'>('hi');
  const [formData, setFormData] = useState<FormData>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    initSession();
  }, [language]);

  const initSession = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const session = await createSession(language);
      setSessionId(session.session_id);
      // Also fetch initial form data for the new session
      const initialForm = await getForm(session.session_id);
      setFormData(initialForm.form_data || {});
    } catch (err) {
      setError('Failed to create session. Please refresh the page to try again.');
      console.error('Session creation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // This function will be passed to the voice component to update the state
  const handleFormUpdate = (updates: Partial<FormData>) => {
    setFormData(prevData => ({ ...prevData, ...updates }));
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="rti-header shadow-lg">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight">
            RTI Voice Assistant
          </h1>
          <p className="mt-4 text-lg md:text-xl text-neutral-200">
            Your voice-powered guide to the Right to Information Act.
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8" role="main">
        <div className="px-4 py-6 sm:px-0">
          {/* Language Selector */}
          <div className="max-w-md mx-auto mb-8">
            <LanguageSelector
              currentLanguage={language}
              onLanguageChange={(lang) => {
                setLanguage(lang);
              }}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div
              role="alert"
              className="max-w-2xl mx-auto bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md shadow-md"
            >
              <p className="font-bold">Error</p>
              <p>{error}</p>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-brand-blue-light"></div>
              <p className="mt-6 text-lg font-semibold text-neutral-600">
                Initializing your secure session...
              </p>
            </div>
          )}

          {/* Main Content */}
          {sessionId && !isLoading && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Voice Recorder */}
              <section aria-labelledby="voice-section-title" className="card">
                <div className="p-6">
                  <h2 id="voice-section-title" className="text-2xl font-bold text-neutral-900 mb-4">
                    Voice Interaction
                  </h2>
                  <VoiceRecorderRealtime 
                    sessionId={sessionId} 
                    language={language}
                    onFormUpdate={handleFormUpdate} // Pass the update function
                  />
                </div>
              </section>

              {/* RTI Form */}
              <section aria-labelledby="form-section-title" className="card">
                <div className="p-6">
                  <h2 id="form-section-title" className="text-2xl font-bold text-neutral-900 mb-4">
                    RTI Application
                  </h2>
                  <RTIForm 
                    sessionId={sessionId} 
                    language={language}
                    initialData={formData} // Pass the form data down
                    onLocalUpdate={handleFormUpdate} // Allow form to update state too
                  />
                </div>
              </section>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-neutral-800 text-neutral-300 mt-12">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 text-center text-sm">
          <p>&copy; {new Date().getFullYear()} RTI Voice Assistant. An initiative for a more accessible India.</p>
          <p className="mt-2">Powered by AI for Bharat</p>
        </div>
      </footer>
    </div>
  );
}
