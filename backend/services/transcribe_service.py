"""
AWS Transcribe service for speech-to-text
"""
import boto3
import uuid
import time
import logging
from typing import Tuple
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.config import settings
from shared.aws_clients import AWSClients

logger = logging.getLogger(__name__)


class TranscribeService:
    """Service for transcribing audio using AWS Transcribe"""
    
    def __init__(self):
        self.transcribe_client = AWSClients.get_transcribe()
        self.s3_client = AWSClients.get_s3()
        self.audio_bucket = settings.s3_audio_bucket
    
    def transcribe_audio(self, audio_bytes: bytes, language: str = 'hi') -> Tuple[str, float, str]:
        """
        Transcribe audio using AWS Transcribe
        
        Args:
            audio_bytes: Audio file bytes
            language: Language code (en, hi, kn)
            
        Returns:
            Tuple of (transcribed_text, confidence, detected_language)
        """
        try:
            # Map language codes
            language_map = {
                'en': 'en-IN',
                'hi': 'hi-IN',
                'kn': 'kn-IN'  # Kannada
            }
            
            language_code = language_map.get(language, 'hi-IN')
            
            # Generate unique job name
            job_name = f"rti-transcribe-{uuid.uuid4()}"
            audio_key = f"audio/{job_name}.wav"
            
            # Upload audio to S3
            logger.info(f"Uploading audio to S3: {audio_key}")
            self.s3_client.put_object(
                Bucket=self.audio_bucket,
                Key=audio_key,
                Body=audio_bytes
            )
            
            # Start transcription job
            logger.info(f"Starting transcription job: {job_name}")
            self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': f's3://{self.audio_bucket}/{audio_key}'},
                MediaFormat='wav',
                LanguageCode=language_code
            )
            
            # Wait for job to complete
            max_tries = 60
            while max_tries > 0:
                max_tries -= 1
                status = self.transcribe_client.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                
                if job_status in ['COMPLETED', 'FAILED']:
                    break
                
                logger.info(f"Transcription job status: {job_status}")
                time.sleep(2)
            
            if job_status == 'COMPLETED':
                # Get transcription result
                transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                
                # Download transcript
                import requests
                response = requests.get(transcript_uri)
                transcript_data = response.json()
                
                text = transcript_data['results']['transcripts'][0]['transcript']
                
                # Calculate average confidence
                items = transcript_data['results']['items']
                confidences = [float(item.get('alternatives', [{}])[0].get('confidence', 0.9)) 
                             for item in items if 'alternatives' in item]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.9
                
                logger.info(f"Transcription successful: {text[:50]}...")
                
                # Clean up S3
                self.s3_client.delete_object(Bucket=self.audio_bucket, Key=audio_key)
                
                return text, avg_confidence, language
            else:
                raise Exception(f"Transcription job failed: {job_status}")
        
        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            raise
