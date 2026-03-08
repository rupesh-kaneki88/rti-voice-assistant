'use client';

import { useId } from 'react';
import { useTranslation } from '@/hooks/useTranslation';

interface LanguageSelectorProps {
  currentLanguage: 'en' | 'hi' | 'kn';
  onLanguageChange: (language: 'en' | 'hi' | 'kn') => void;
  language: 'en' | 'hi' | 'kn';
}

export default function LanguageSelector({ currentLanguage, onLanguageChange, language }: LanguageSelectorProps) {
  const languages = [
    { code: 'en' as const, name: 'English', native: 'English' },
    { code: 'hi' as const, name: 'Hindi', native: 'हिंदी' },
    { code: 'kn' as const, name: 'Kannada', native: 'ಕನ್ನಡ' },
  ];

  const id = useId();
  const { t } = useTranslation(language);
  const selectedIndex = languages.findIndex(l => l.code === currentLanguage);

  return (
    <div>
      <div
        className="relative flex w-full items-center rounded-full bg-neutral-200/80 p-1"
        role="radiogroup"
        aria-label={t('language.label')}
      >
        {/* Sliding background pill */}
        <div
          className="absolute top-1/2 h-full -translate-y-1/2 rounded-full bg-white shadow-md transition-transform duration-300 ease-in-out"
          style={{
            width: `calc((100% - 0.5rem) / 3)`, // (100% - gap) / num_items
            transform: `translateX(calc(${selectedIndex} * 100% + ${selectedIndex * 0.25}rem)) translateY(-50%)`,
          }}
        />

        {languages.map((lang) => (
          <button
            key={lang.code}
            onClick={() => onLanguageChange(lang.code)}
            className={`
              relative z-10 flex-1 cursor-pointer rounded-full px-2 py-2 text-center text-sm font-bold
              transition-colors duration-300 ease-in-out
              focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
              ${currentLanguage === lang.code ? 'text-blue-600' : 'text-neutral-600 hover:text-neutral-800'}
            `}
            role="radio"
            aria-checked={currentLanguage === lang.code}
            aria-labelledby={`${id}-${lang.code}`}
          >
            <span id={`${id}-${lang.code}`} className="block truncate">{lang.native}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
