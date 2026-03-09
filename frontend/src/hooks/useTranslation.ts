'use client';

import { useMemo } from 'react';
import en from '../locales/en.json';
import hi from '../locales/hi.json';
import kn from '../locales/kn.json';

const translations = { en, hi, kn };

type Language = 'en' | 'hi' | 'kn';

// Helper function to get a nested property from an object
function getNested(obj: any, path: string): string | undefined {
  return path.split('.').reduce((acc, key) => acc && acc[key], obj);
}

export function useTranslation(language: Language) {
  const t = useMemo(() => {
    return (key: string, replacements?: { [key: string]: string | number }): string => {
      const langFile = translations[language] || en;
      let text = getNested(langFile, key) || getNested(en, key) || key;

      if (replacements) {
        Object.entries(replacements).forEach(([rKey, value]) => {
          text = text.replace(`{${rKey}}`, String(value));
        });
      }

      return text;
    };
  }, [language]);

  return { t };
}
