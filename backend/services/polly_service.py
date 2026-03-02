"""
AWS Polly service for text-to-speech with gTTS fallback for Kannada
"""
import logging
import sys
import os
from gtts import gTTS
import io

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.config import settings
from shared.aws_clients import AWSClients

logger = logging.getLogger(__name__)


class PollyService:
    """Service for text-to-speech using AWS Polly with gTTS fallback"""
    
    def __init__(self):
        self.polly_client = AWSClients.get_polly()
    
    def synthesize_speech(self, text: str, language: str = 'hi') -> bytes:
        """
        Convert text to speech using AWS Polly or gTTS
        
        Args:
            text: Text to convert
            language: Language code (en, hi, kn)
            
        Returns:
            Audio bytes (MP3 format)
        """
        try:
            # Use gTTS for Kannada (Polly doesn't support it well)
            if language == 'kn':
                return self._synthesize_with_gtts(text, 'kn')
            
            # Map language to voice for Polly
            voice_map = {
                'en': settings.polly_voice_english,  # Joanna
                'hi': settings.polly_voice_hindi,     # Aditi
            }
            
            voice_id = voice_map.get(language, settings.polly_voice_hindi)
            
            logger.info(f"Synthesizing speech with Polly: language={language}, voice={voice_id}")
            
            # Try neural engine first, fallback to standard
            try:
                response = self.polly_client.synthesize_speech(
                    Text=text,
                    OutputFormat=settings.polly_output_format,
                    VoiceId=voice_id,
                    Engine='neural'
                )
            except Exception as neural_error:
                logger.warning(f"Neural engine not supported for {voice_id}, using standard engine")
                response = self.polly_client.synthesize_speech(
                    Text=text,
                    OutputFormat=settings.polly_output_format,
                    VoiceId=voice_id,
                    Engine='standard'
                )
            
            # Read audio stream
            audio_bytes = response['AudioStream'].read()
            
            logger.info(f"Polly speech synthesis successful: {len(audio_bytes)} bytes")
            
            return audio_bytes
        
        except Exception as e:
            logger.error(f"Polly TTS error: {e}, falling back to gTTS")
            # Fallback to gTTS
            return self._synthesize_with_gtts(text, language)
    
    def _synthesize_with_gtts(self, text: str, language: str) -> bytes:
        """
        Fallback TTS using gTTS (Google Text-to-Speech)
        
        Args:
            text: Text to convert
            language: Language code
            
        Returns:
            Audio bytes (MP3 format)
        """
        try:
            # Map language codes for gTTS
            gtts_lang_map = {
                'en': 'en',
                'hi': 'hi',
                'kn': 'kn'  # Kannada
            }
            
            lang_code = gtts_lang_map.get(language, 'hi')
            
            logger.info(f"Synthesizing speech with gTTS: language={lang_code}")
            
            # Create gTTS object
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_bytes = audio_buffer.read()
            
            logger.info(f"gTTS speech synthesis successful: {len(audio_bytes)} bytes")
            
            return audio_bytes
        
        except Exception as e:
            logger.error(f"gTTS error: {e}", exc_info=True)
            raise
