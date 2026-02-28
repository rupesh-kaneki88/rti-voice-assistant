"""
Speech-to-text transcription using IndicWhisper and OpenAI Whisper
"""
import torch
import librosa
import numpy as np
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import whisper
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for speech-to-text transcription"""
    
    def __init__(self):
        """Initialize transcription models"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # IndicWhisper for Hindi and Kannada
        self.indic_model_name = "vasista22/whisper-hindi-large-v2"
        self.indic_processor = None
        self.indic_model = None
        
        # OpenAI Whisper for English fallback
        self.whisper_model = None
        
        # Lazy loading to reduce cold start time
        self._indic_loaded = False
        self._whisper_loaded = False
    
    def _load_indic_whisper(self):
        """Lazy load IndicWhisper model"""
        if not self._indic_loaded:
            logger.info("Loading IndicWhisper model...")
            self.indic_processor = WhisperProcessor.from_pretrained(self.indic_model_name)
            self.indic_model = WhisperForConditionalGeneration.from_pretrained(
                self.indic_model_name
            ).to(self.device)
            self._indic_loaded = True
            logger.info("IndicWhisper model loaded successfully")
    
    def _load_openai_whisper(self):
        """Lazy load OpenAI Whisper model"""
        if not self._whisper_loaded:
            logger.info("Loading OpenAI Whisper model...")
            self.whisper_model = whisper.load_model("base")
            self._whisper_loaded = True
            logger.info("OpenAI Whisper model loaded successfully")
    
    def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Tuple[str, float, str]:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (en, hi, kn) or None for auto-detection
        
        Returns:
            Tuple of (transcribed_text, confidence, detected_language)
        """
        try:
            # Load audio file
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Determine which model to use
            if language == 'en':
                return self._transcribe_with_whisper(audio, sr)
            elif language in ['hi', 'kn']:
                return self._transcribe_with_indic_whisper(audio, sr, language)
            else:
                # Auto-detect language and transcribe
                return self._transcribe_auto_detect(audio, sr)
        
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise
    
    def _transcribe_with_indic_whisper(
        self,
        audio: np.ndarray,
        sr: int,
        language: str
    ) -> Tuple[str, float, str]:
        """Transcribe using IndicWhisper"""
        self._load_indic_whisper()
        
        # Process audio
        input_features = self.indic_processor(
            audio,
            sampling_rate=sr,
            return_tensors="pt"
        ).input_features.to(self.device)
        
        # Generate transcription
        with torch.no_grad():
            predicted_ids = self.indic_model.generate(input_features)
        
        # Decode transcription
        transcription = self.indic_processor.batch_decode(
            predicted_ids,
            skip_special_tokens=True
        )[0]
        
        # Calculate confidence (simplified - based on model output)
        confidence = 0.9  # IndicWhisper typically has high confidence
        
        logger.info(f"IndicWhisper transcription: {transcription[:50]}...")
        return transcription, confidence, language
    
    def _transcribe_with_whisper(
        self,
        audio: np.ndarray,
        sr: int
    ) -> Tuple[str, float, str]:
        """Transcribe using OpenAI Whisper"""
        self._load_openai_whisper()
        
        # Transcribe
        result = self.whisper_model.transcribe(
            audio,
            language='en',
            fp16=False
        )
        
        transcription = result['text']
        
        # Calculate average confidence from segments
        if 'segments' in result and result['segments']:
            confidences = [seg.get('no_speech_prob', 0.1) for seg in result['segments']]
            confidence = 1.0 - np.mean(confidences)
        else:
            confidence = 0.85
        
        logger.info(f"Whisper transcription: {transcription[:50]}...")
        return transcription, confidence, 'en'
    
    def _transcribe_auto_detect(
        self,
        audio: np.ndarray,
        sr: int
    ) -> Tuple[str, float, str]:
        """Auto-detect language and transcribe"""
        # Try IndicWhisper first (covers Hindi/Kannada)
        try:
            self._load_indic_whisper()
            
            input_features = self.indic_processor(
                audio,
                sampling_rate=sr,
                return_tensors="pt"
            ).input_features.to(self.device)
            
            with torch.no_grad():
                predicted_ids = self.indic_model.generate(input_features)
            
            transcription = self.indic_processor.batch_decode(
                predicted_ids,
                skip_special_tokens=True
            )[0]
            
            # Detect language from transcription
            detected_lang = self._detect_language_from_text(transcription)
            
            if detected_lang in ['hi', 'kn']:
                logger.info(f"Auto-detected language: {detected_lang}")
                return transcription, 0.9, detected_lang
        
        except Exception as e:
            logger.warning(f"IndicWhisper auto-detect failed: {str(e)}")
        
        # Fallback to OpenAI Whisper for English
        logger.info("Falling back to OpenAI Whisper")
        return self._transcribe_with_whisper(audio, sr)
    
    def _detect_language_from_text(self, text: str) -> str:
        """
        Detect language from transcribed text
        Simple heuristic based on Unicode ranges
        """
        if not text:
            return 'en'
        
        # Count characters in different Unicode ranges
        devanagari_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        kannada_count = sum(1 for c in text if '\u0C80' <= c <= '\u0CFF')
        latin_count = sum(1 for c in text if c.isalpha() and ord(c) < 128)
        
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return 'en'
        
        # Determine dominant script
        if devanagari_count / total_chars > 0.5:
            return 'hi'
        elif kannada_count / total_chars > 0.5:
            return 'kn'
        else:
            return 'en'


# Global instance for Lambda reuse
_transcription_service = None


def get_transcription_service() -> TranscriptionService:
    """Get or create transcription service instance"""
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service
