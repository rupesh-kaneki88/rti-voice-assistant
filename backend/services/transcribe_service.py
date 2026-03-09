"""
Real-time speech-to-text service with AWS Transcribe Streaming and faster-whisper fallback.
"""
import asyncio
import logging
import sys
import os
import io
# from faster_whisper import WhisperModel # Commented out
# from pydub import AudioSegment # Commented out

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.config import settings

# AWS Transcribe Streaming SDK
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

logger = logging.getLogger(__name__)

# class WhisperManager: # Commented out
#     """Singleton to manage loading the faster-whisper model."""
#     _model = None

#     @classmethod
#     def get_model(cls):
#         if cls._model is None:
#             logger.info("Loading faster-whisper model (base.en)...")
#             # Using 'base.en' model with int8 quantization for CPU performance
#             cls._model = WhisperModel("base.en", device="cpu", compute_type="int8")
#             logger.info("✓ faster-whisper model loaded.")
#         return cls._model

class AWSTranscriptHandler(TranscriptResultStreamHandler):
    """Handles the transcript events from the AWS stream."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.full_transcript = ""

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        if results and not results[0].is_partial:
            for result in results:
                for alt in result.alternatives:
                    self.full_transcript += alt.transcript + " "

class TranscribeService:
    """
    Service for real-time transcription using AWS Transcribe Streaming
    with a fallback to a local faster-whisper model.
    """
    def __init__(self):
        self.aws_region = settings.aws_region
        # Initialize Whisper model on startup if needed (Commented out)
        # if not settings.use_mock_services:
        #     WhisperManager.get_model()

    async def transcribe_audio(self, audio_bytes: bytes, language: str = 'en') -> str:
        """
        Transcribes audio. Tries AWS Streaming first, then falls back to faster-whisper.
        """
        try:
            logger.info(f"Attempting transcription with AWS Transcribe Streaming for '{language}'")
            transcript = await self._transcribe_with_aws(audio_bytes, language)
            if transcript:
                logger.info("✓ AWS Transcription successful.")
                return transcript
            # logger.warning("AWS returned empty transcript, no fallback will be attempted.") # Modified
        except Exception as e:
            logger.error(f"AWS Transcribe Streaming failed: {e}. No fallback will be attempted.", exc_info=True) # Modified error message
            raise # Re-raise the exception if AWS fails

        # Fallback to faster-whisper (Commented out)
        # try:
        #     logger.info("Attempting transcription with faster-whisper...")
        #     transcript = await self._transcribe_with_whisper(audio_bytes)
        #     logger.info("✓ faster-whisper transcription successful.")
        #     return transcript
        # except Exception as e:
        #     logger.error(f"faster-whisper transcription also failed: {e}", exc_info=True)
        #     raise
        
        # If AWS didn't return a transcript, raise an error
        raise Exception("Transcription failed: AWS Transcribe did not return a transcript.")


    async def _transcribe_with_aws(self, audio_bytes: bytes, language: str) -> str:
        """Uses AWS Transcribe Streaming."""
        language_map = {'en': 'en-US', 'hi': 'hi-IN', 'kn': 'kn-IN'}
        language_code = language_map.get(language)
        if not language_code:
            raise ValueError(f"Language '{language}' not supported by AWS Transcribe.")

        client = TranscribeStreamingClient(region=self.aws_region)
        handler = AWSTranscriptHandler()

        async def audio_stream():
            chunk_size = 1024 * 4
            for i in range(0, len(audio_bytes), chunk_size):
                yield audio_bytes[i:i + chunk_size]
                await asyncio.sleep(0.1)

        stream = await client.start_stream_transcription(
            language_code=language_code,
            media_sample_rate_hz=16000,
            media_encoding="pcm",
            transcript_result_stream=handler,
        )

        async for chunk in audio_stream():
            await stream.input_stream.send_audio_event(audio_chunk=chunk)
        
        await stream.input_stream.end_stream()
        
        return handler.full_transcript.strip()

# async def _transcribe_with_whisper(self, audio_bytes: bytes) -> str: # Commented out
#     """
#     Uses the local faster-whisper model for transcription.
#     """
#     loop = asyncio.get_running_loop()
    
#     audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
#     wav_buffer = io.BytesIO()
#     audio.export(wav_buffer, format="wav")
#     wav_buffer.seek(0)

#     model = WhisperManager.get_model()

#     def transcribe_sync():
#         segments, info = model.transcribe(wav_buffer, beam_size=5)
#         # The result is a generator, so we iterate and join
#         return " ".join([segment.text for segment in segments])

#     # Run the synchronous, CPU-bound whisper call in a thread pool
#     full_text = await loop.run_in_executor(
#         None, transcribe_sync
#     )
    
#     return full_text.strip()