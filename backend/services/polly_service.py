"""
AWS Polly service for text-to-speech
"""
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.config import settings
from shared.aws_clients import AWSClients

logger = logging.getLogger(__name__)


class PollyService:
    """Service for text-to-speech using AWS Polly"""
    
    def __init__(self):
        self.polly_client = AWSClients.get_polly()
    
    def synthesize_speech(self, text: str, language: str = 'hi') -> bytes:
        """
        Convert text to speech using AWS Polly
        
        Args:
            text: Text to convert
            language: Language code (en, hi, kn)
            
        Returns:
            Audio bytes (MP3 format)
        """
        try:
            # Map language to voice
            voice_map = {
                'en': settings.polly_voice_english,  # Joanna
                'hi': settings.polly_voice_hindi,     # Aditi
                'kn': settings.polly_voice_hindi      # Use Hindi voice for Kannada (Polly doesn't have Kannada)
            }
            
            voice_id = voice_map.get(language, settings.polly_voice_hindi)
            
            logger.info(f"Synthesizing speech: language={language}, voice={voice_id}")
            
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat=settings.polly_output_format,
                VoiceId=voice_id,
                Engine='neural'  # Use neural engine for better quality
            )
            
            # Read audio stream
            audio_bytes = response['AudioStream'].read()
            
            logger.info(f"Speech synthesis successful: {len(audio_bytes)} bytes")
            
            return audio_bytes
        
        except Exception as e:
            logger.error(f"TTS error: {e}", exc_info=True)
            raise
