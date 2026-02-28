"""
Language detection for audio input
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detect language from audio or text"""
    
    @staticmethod
    def detect_from_text(text: str) -> str:
        """
        Detect language from text using Unicode ranges
        
        Args:
            text: Input text
        
        Returns:
            Language code: 'en', 'hi', or 'kn'
        """
        if not text:
            return 'en'
        
        # Count characters in different Unicode ranges
        devanagari_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')  # Hindi
        kannada_count = sum(1 for c in text if '\u0C80' <= c <= '\u0CFF')     # Kannada
        latin_count = sum(1 for c in text if c.isalpha() and ord(c) < 128)    # English
        
        total_alpha = len([c for c in text if c.isalpha()])
        
        if total_alpha == 0:
            return 'en'
        
        # Calculate percentages
        devanagari_pct = devanagari_count / total_alpha
        kannada_pct = kannada_count / total_alpha
        latin_pct = latin_count / total_alpha
        
        # Determine dominant script
        if devanagari_pct > 0.5:
            logger.info(f"Detected Hindi (Devanagari: {devanagari_pct:.2%})")
            return 'hi'
        elif kannada_pct > 0.5:
            logger.info(f"Detected Kannada (Kannada: {kannada_pct:.2%})")
            return 'kn'
        else:
            logger.info(f"Detected English (Latin: {latin_pct:.2%})")
            return 'en'
    
    @staticmethod
    def is_supported_language(lang_code: str) -> bool:
        """Check if language is supported"""
        return lang_code in ['en', 'hi', 'kn']
    
    @staticmethod
    def get_language_name(lang_code: str) -> str:
        """Get full language name from code"""
        language_names = {
            'en': 'English',
            'hi': 'Hindi',
            'kn': 'Kannada'
        }
        return language_names.get(lang_code, 'Unknown')
