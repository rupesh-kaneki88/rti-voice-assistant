"""
Local FastAPI server for testing Voice Service without Lambda/Docker
Run with: uvicorn app_local:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RTI Voice Service - Local Testing")

# Enable CORS for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranscribeRequest(BaseModel):
    audio: str  # base64 encoded audio
    language: str = "en"  # en, hi, kn


class TranscribeResponse(BaseModel):
    text: str
    confidence: float
    language: str
    mode: str
    message: str


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "RTI Voice Service",
        "status": "running",
        "mode": "LOCAL_TESTING",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/voice/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(request: TranscribeRequest):
    """
    Transcribe audio to text (mock implementation for testing)
    
    Args:
        request: TranscribeRequest with base64 encoded audio and language
        
    Returns:
        TranscribeResponse with transcribed text
    """
    try:
        logger.info(f"Received transcription request for language: {request.language}")
        
        # Validate language
        if request.language not in ['en', 'hi', 'kn']:
            raise HTTPException(
                status_code=400,
                detail="Invalid language. Supported: en, hi, kn"
            )
        
        # Validate audio is base64
        try:
            audio_bytes = base64.b64decode(request.audio)
            audio_size = len(audio_bytes)
            logger.info(f"Received audio: {audio_size} bytes")
        except Exception as e:
            logger.error(f"Failed to decode audio: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid audio encoding. Must be base64-encoded."
            )
        
        # Return mock transcription based on language
        mock_transcriptions = {
            'en': 'This is a mock transcription in English for local testing.',
            'hi': 'यह स्थानीय परीक्षण के लिए हिंदी में एक नकली प्रतिलेखन है।',
            'kn': 'ಇದು ಸ್ಥಳೀಯ ಪರೀಕ್ಷೆಗಾಗಿ ಕನ್ನಡದಲ್ಲಿ ಅಣಕು ಪ್ರತಿಲೇಖನವಾಗಿದೆ.'
        }
        
        logger.info(f"Returning mock transcription for language: {request.language}")
        
        return TranscribeResponse(
            text=mock_transcriptions[request.language],
            confidence=0.95,
            language=request.language,
            mode="LOCAL_TESTING",
            message="This is a mock response for local testing. Real transcription will use IndicWhisper."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in transcription: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/voice/tts")
async def text_to_speech(text: str, language: str = "en"):
    """
    Text-to-speech endpoint (placeholder for future implementation)
    
    Args:
        text: Text to convert to speech
        language: Language code (en, hi, kn)
        
    Returns:
        Mock response indicating TTS is not yet implemented
    """
    return {
        "message": "TTS endpoint - Coming soon",
        "text": text,
        "language": language,
        "status": "not_implemented"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
