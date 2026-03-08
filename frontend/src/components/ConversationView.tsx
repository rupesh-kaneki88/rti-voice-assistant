'use client';

import { useEffect, useRef } from 'react';
import { useTranslation } from '@/hooks/useTranslation';

export interface ConversationMessage {
  role: 'user' | 'agent';
  content: string;
}

interface ConversationViewProps {
  history: ConversationMessage[];
  language: 'en' | 'hi' | 'kn';
}

export default function ConversationView({ history, language }: ConversationViewProps) {
  const conversationEndRef = useRef<HTMLDivElement | null>(null);
  const { t } = useTranslation(language);

  useEffect(() => {
    // Scroll to the bottom of the conversation history
    conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  if (history.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center text-neutral-500 p-4">
        <div className="max-w-md">
          <h2 className="text-2xl font-semibold text-neutral-700">{t('welcome.title')}</h2>
          <p className="mt-2">
            {t('welcome.subtitle')}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-4 md:p-6 space-y-4">
      {history.map((msg, index) => (
        <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div 
            className={`
              max-w-sm md:max-w-md lg:max-w-lg p-3 rounded-2xl shadow-sm
              ${msg.role === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-white text-neutral-800 border border-neutral-200'
              }
            `}
          >
            <p className="text-sm md:text-base">{msg.content}</p>
          </div>
        </div>
      ))}
      <div ref={conversationEndRef} />
    </div>
  );
}
