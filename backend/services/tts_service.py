"""
Unified Text-to-Speech service using the best available provider for each language.
- English (en): edge-tts -> gTTS -> Polly
- Hindi (hi): edge-tts -> gTTS -> Polly
- Kannada (kn): gTTS
"""
import logging
import sys
import os
import asyncio
import io
from gtts import gTTS
import edge_tts

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.config import settings
from shared.aws_clients import AWSClients

logger = logging.getLogger(__name__)

class TTSService:
    """Service for text-to-speech using the best provider based on language."""
    
    def __init__(self):
        self.polly_client = AWSClients.get_polly()
    
    async def synthesize_speech(self, text: str, language: str = 'en') -> bytes:
        """
        Convert text to speech using the optimal provider chain.
        
        Args:
            text: Text to convert.
            language: Language code (en, hi, kn).
            
        Returns:
            Audio bytes (MP3 format).
        """
        if language in ['en', 'hi']:
            try:
                logger.info(f"Attempting TTS with edge-tts for '{language}'")
                return await self._synthesize_with_edge_tts(text, language)
            except Exception as edge_error:
                logger.warning(f"edge-tts failed: {edge_error}. Falling back to gTTS.")
                try:
                    return self._synthesize_with_gtts(text, language)
                except Exception as gtts_error:
                    logger.warning(f"gTTS also failed: {gtts_error}. Falling back to AWS Polly.")
                    if self.polly_client:
                        return self._synthesize_with_polly(text, language)
                    else:
                        logger.error("All TTS providers failed for language '{}'".format(language))
                        raise gtts_error # Re-raise the last error

        elif language == 'kn':
            try:
                logger.info(f"Attempting TTS with gTTS for 'kn'")
                return self._synthesize_with_gtts(text, language)
            except Exception as gtts_error:
                logger.error(f"gTTS failed for Kannada, no fallback available: {gtts_error}")
                raise gtts_error
        
        else:
            raise ValueError(f"Unsupported language for TTS: {language}")

    async def _synthesize_with_edge_tts(self, text: str, language: str) -> bytes:
        """Synthesizes text to speech using edge-tts."""
        voice_map = {
            'en': 'en-US-AriaNeural',
            'hi': 'hi-IN-SwaraNeural'
        }
        voice = voice_map.get(language)
        if not voice:
            raise ValueError(f"No edge-tts voice found for language '{language}'")

        logger.info(f"Synthesizing with edge-tts voice: '{voice}'")
        communicate = edge_tts.Communicate(text, voice)
        
        # Collect audio chunks into a single byte buffer
        audio_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
        
        audio_buffer.seek(0)
        audio_bytes = audio_buffer.read()

        if not audio_bytes:
            raise ConnectionError("edge-tts returned no audio data.")
            
        logger.info(f"edge-tts synthesis successful: {len(audio_bytes)} bytes")
        return audio_bytes

    def _synthesize_with_gtts(self, text: str, language: str) -> bytes:
        """Synthesizes text to speech using gTTS."""
        logger.info(f"Synthesizing with gTTS for lang_code='{language}'")
        tts = gTTS(text=text, lang=language, slow=False)
        
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_bytes = audio_buffer.read()
        
        logger.info(f"gTTS synthesis successful: {len(audio_bytes)} bytes")
        return audio_bytes

    def _synthesize_with_polly(self, text: str, language: str) -> bytes:
        """Fallback TTS using AWS Polly."""
        if language == 'kn':
            raise ValueError("AWS Polly fallback is not supported for Kannada (kn).")

        voice_map = {
            'en': settings.polly_voice_english,
            'hi': settings.polly_voice_hindi,
        }
        voice_id = voice_map.get(language)
        if not voice_id:
            raise ValueError(f"No Polly voice configured for language '{language}'.")

        logger.info(f"Synthesizing with Polly voice: '{voice_id}'")
        
        try:
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat=settings.polly_output_format,
                VoiceId=voice_id,
                Engine='neural'
            )
        except Exception:
            logger.warning(f"Neural engine failed for {voice_id}, trying standard.")
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat=settings.polly_output_format,
                VoiceId=voice_id,
                Engine='standard'
            )
        
        audio_bytes = response['AudioStream'].read()
        logger.info(f"Polly synthesis successful: {len(audio_bytes)} bytes")
        return audio_bytes
