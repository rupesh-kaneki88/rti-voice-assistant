"""
Simplified Lambda handler for Voice Service - Mock Speech-to-Text
Use this for infrastructure testing before adding IndicWhisper
"""
import json
import base64
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Simplified Lambda handler that returns mock transcriptions
    
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
            "text": "mock transcribed text",
            "confidence": 0.95,
            "language": "hi"
        }
    }
    """
    try:
        logger.info("Voice Service Lambda invoked (SIMPLE MODE)")
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
        language = body.get('language', 'en')
        if language not in ['en', 'hi', 'kn']:
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
        
        # Validate audio is base64
        try:
            audio_bytes = base64.b64decode(audio_base64)
            audio_size = len(audio_bytes)
            logger.info(f"Received audio: {audio_size} bytes")
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
        
        # Return mock transcription based on language
        mock_transcriptions = {
            'en': 'This is a mock transcription in English for infrastructure testing.',
            'hi': 'यह बुनियादी ढांचे के परीक्षण के लिए हिंदी में एक नकली प्रतिलेखन है।',
            'kn': 'ಇದು ಮೂಲಸೌಕರ್ಯ ಪರೀಕ್ಷೆಗಾಗಿ ಕನ್ನಡದಲ್ಲಿ ಅಣಕು ಪ್ರತಿಲೇಖನವಾಗಿದೆ.'
        }
        
        logger.info(f"Returning mock transcription for language: {language}")
        
        # Return mock response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'text': mock_transcriptions[language],
                'confidence': 0.95,
                'language': language,
                'timestamp': context.request_id if context else None,
                'mode': 'MOCK',
                'message': 'This is a mock response for infrastructure testing. IndicWhisper will be added later.'
            })
        }
    
    except Exception as e:
        logger.error(f"Error in simple handler: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
