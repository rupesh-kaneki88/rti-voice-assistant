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
    <div className="bg-white rounded-lg shadow-md p-4">
      <label htmlFor="language-select" className="block text-sm font-medium text-gray-700 mb-2">
        Select Language / भाषा चुनें / ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ
      </label>
      
      <div className="flex gap-2 flex-wrap">
        {languages.map((lang) => (
          <button
            key={lang.code}
            onClick={() => onLanguageChange(lang.code)}
            className={`
              px-6 py-3 rounded-lg font-medium transition-all duration-200
              focus:outline-none focus:ring-4 focus:ring-offset-2
              ${currentLanguage === lang.code
                ? 'bg-blue-600 text-white focus:ring-blue-500'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-gray-400'
              }
            `}
            aria-pressed={currentLanguage === lang.code}
            aria-label={`Select ${lang.name} language`}
          >
            <span className="block text-sm">{lang.name}</span>
            <span className="block text-lg">{lang.native}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
