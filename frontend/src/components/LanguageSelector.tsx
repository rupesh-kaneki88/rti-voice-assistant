'use client';

interface LanguageSelectorProps {
  currentLanguage: 'en' | 'hi' | 'kn';
  onLanguageChange: (language: 'en' | 'hi' | 'kn') => void;
}

export default function LanguageSelector({ currentLanguage, onLanguageChange }: LanguageSelectorProps) {
  const languages = [
    { code: 'en' as const, name: 'English', native: 'English' },
    { code: 'hi' as const, name: 'Hindi', native: 'हिंदी' },
    { code: 'kn' as const, name: 'Kannada', native: 'ಕನ್ನಡ' },
  ];

  return (
    <div className="card p-4">
      <label htmlFor="language-select" className="block text-sm font-bold text-neutral-700 mb-3 text-center">
        Select Your Language
      </label>
      
      <div id="language-select" className="grid grid-cols-3 gap-2">
        {languages.map((lang) => (
          <button
            key={lang.code}
            onClick={() => onLanguageChange(lang.code)}
            className={`
              p-3 rounded-lg font-semibold text-center
              transition-all duration-200 transform
              focus:outline-none focus:ring-4 focus:ring-offset-2
              ${currentLanguage === lang.code
                ? 'bg-brand-blue text-white shadow-lg scale-105 focus:ring-brand-blue-light'
                : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200 focus:ring-neutral-400'
              }
            `}
            aria-pressed={currentLanguage === lang.code}
            aria-label={`Select ${lang.name}`}
          >
            <span className="block text-xs md:text-sm">{lang.name}</span>
            <span className="block text-md md:text-lg">{lang.native}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
