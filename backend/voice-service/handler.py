"""
Lambda handler for Voice Service - Speech-to-Text
"""
import json
import base64
import tempfile
import os
from typing import Dict, Any
import logging

# Import shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

from transcribe import get_transcription_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for speech-to-text transcription
    
    Event structure:
    {
        "body": {
            "audio": "base64_encoded_audio",
            "language": "en|hi|kn" (optional)
        }
    }
    
    Returns:
    {
        "statusCode": 200,
        "body": {
            "text": "transcribed text",
            "confidence": 0.95,
            "language": "hi"
        }
    }
    """
    try:
        logger.info("Voice Service Lambda invoked")
        logger.info(f"Event: {json.dumps(event)[:200]}...")
        
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Extract audio data
        audio_base64 = body.get('audio')
        if not audio_base64:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing audio data',
                    'message': 'Please provide base64-encoded audio in the request body'
                })
            }
        
        # Get language preference (optional)
        language = body.get('language')
        if language and language not in ['en', 'hi', 'kn']:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid language',
                    'message': 'Supported languages: en, hi, kn'
                })
            }
        
        # Decode audio
        try:
            audio_bytes = base64.b64decode(audio_base64)
        except Exception as e:
            logger.error(f"Failed to decode audio: {str(e)}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid audio encoding',
                    'message': 'Audio must be base64-encoded'
                })
            }
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name
        
        try:
            # Transcribe audio
            logger.info(f"Transcribing audio (language: {language or 'auto-detect'})...")
            transcription_service = get_transcription_service()
            text, confidence, detected_language = transcription_service.transcribe_audio(
                temp_audio_path,
                language
            )
            
            logger.info(f"Transcription successful: {text[:50]}...")
            
            # Return response
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'text': text,
                    'confidence': confidence,
                    'language': detected_language,
                    'timestamp': context.request_id if context else None
                })
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
    
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Transcription failed',
                'message': str(e)
            })
        }
