'use client';

import { useState, useEffect } from 'react';
import VoiceRecorderRealtime from '@/components/VoiceRecorderRealtime';
import RTIForm from '@/components/RTIForm';
import LanguageSelector from '@/components/LanguageSelector';
import ConversationView, { ConversationMessage } from '@/components/ConversationView';
import { createSession, getForm } from '@/lib/api';
import { useTranslation } from '@/hooks/useTranslation';

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
  const [language, setLanguage] = useState<'en' | 'hi' | 'kn'>('en');
  const [formData, setFormData] = useState<FormData>({});
  const [conversationHistory, setConversationHistory] = useState<ConversationMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState('initial'); // 'initial', 'conversation', 'form-filling'
  const [showConversationInFormMode, setShowConversationInFormMode] = useState(false);

  const { t } = useTranslation(language);

  useEffect(() => {
    initSession();
  }, [language]);

  const initSession = async () => {
    try {
      setIsLoading(true);
      setError(null);
      setMode('initial');
      setConversationHistory([]); // Clear history on new session
      const session = await createSession(language);
      setSessionId(session.session_id);
      const initialForm = await getForm(session.session_id);
      setFormData(initialForm.form_data || {});
    } catch (err) {
      setError('Failed to create session. Please refresh the page to try again.');
      console.error('Session creation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormUpdate = (updates: Partial<FormData> & { mode?: string }) => {
    if (updates.mode && updates.mode !== mode) {
      setMode(updates.mode);
      if (updates.mode === 'form-filling') {
        setShowConversationInFormMode(false); // Reset when entering form mode
      }
    }
    const formUpdates = { ...updates };
    delete formUpdates.mode;
    
    setFormData(prevData => ({ ...prevData, ...formUpdates }));
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-neutral-800 font-sans">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-neutral-900">
              {t('header.title')}
            </h1>
            <p className="mt-1 text-neutral-600">
              {t('header.subtitle')}
            </p>
          </div>
          <div className="w-48">
            <LanguageSelector
              currentLanguage={language}
              onLanguageChange={(lang) => setLanguage(lang)}
              language={language}
            />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8" role="main">
        {/* Error and Loading States */}
        {error && (
          <div role="alert" className="max-w-4xl mx-auto bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md shadow-md mb-6">
            <p className="font-bold">Error</p>
            <p>{error}</p>
          </div>
        )}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-600"></div>
            <p className="mt-6 text-lg font-semibold text-neutral-600">
              {t('loading.message')}
            </p>
          </div>
        )}

        {/* Main Content Area */}
        {sessionId && !isLoading && (
          <div className="flex flex-col lg:flex-row gap-8">
            
            {/* Left Panel: Voice Controller */}
            <div className="lg:w-1/3 flex items-center justify-center">
              <VoiceRecorderRealtime 
                sessionId={sessionId} 
                language={language}
                onFormUpdate={handleFormUpdate}
                setMode={setMode}
                onNewMessage={(message) => setConversationHistory(prev => [...prev, message])}
              />
            </div>

            {/* Right Panel: Conversation or Form */}
            <div className="lg:w-2/3 flex flex-col gap-4">
              <div className="relative bg-white rounded-2xl shadow-lg border border-neutral-200">
                {mode === 'form-filling' ? (
                  <div>
                    <div className="p-6 pb-16"> {/* Add padding to the bottom */}
                      <h2 id="form-section-title" className="text-2xl font-bold text-neutral-900 mb-4">
                        {t('form.title')}
                      </h2>
                      <RTIForm 
                        sessionId={sessionId} 
                        language={language}
                        initialData={formData}
                        onLocalUpdate={handleFormUpdate}
                      />
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 p-4 bg-white/80 backdrop-blur-sm border-t border-neutral-200 rounded-b-2xl">
                      <div className="text-center">
                        <button 
                          onClick={() => setShowConversationInFormMode(!showConversationInFormMode)}
                          className="text-blue-600 hover:underline font-semibold"
                        >
                          {showConversationInFormMode ? 'Hide Conversation' : 'Show Conversation'}
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-[65vh] overflow-y-auto">
                    <ConversationView history={conversationHistory} language={language} />
                  </div>
                )}
              </div>
              {mode === 'form-filling' && showConversationInFormMode && (
                <div className="bg-white rounded-2xl shadow-lg border border-neutral-200 p-4 h-96 overflow-y-auto">
                  <h3 className="text-xl font-bold text-neutral-800 mb-2">Conversation History</h3>
                  <ConversationView history={conversationHistory} language={language} />
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-neutral-800 text-neutral-300 mt-12">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 text-center text-sm">
          <p>{t('footer.copyright', { year: new Date().getFullYear() })}</p>
        </div>
      </footer>
    </div>
  );
}
