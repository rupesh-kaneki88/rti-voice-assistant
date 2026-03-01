"""
RTI Voice Assistant - Main FastAPI Application
Fully functional prototype with AWS services integration
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import base64
import logging
from typing import Optional
import uuid
from datetime import datetime, timedelta
import io
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from shared.config import settings
from shared.aws_clients import get_sessions_table
from services.bedrock_service import BedrockService
from services.polly_service import PollyService
from services.transcribe_service import TranscribeService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RTI Voice Assistant API",
    description="AI-powered RTI filing assistant for visually impaired users",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AWS services
bedrock_service = None
polly_service = None
transcribe_service = None

# In-memory fallback storage
sessions_memory = {}


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global bedrock_service, polly_service, transcribe_service
    
    try:
        if not settings.use_mock_services:
            logger.info("Initializing AWS services...")
            bedrock_service = BedrockService()
            polly_service = PollyService()
            transcribe_service = TranscribeService()
            logger.info("✓ AWS services initialized")
        else:
            logger.info("Using mock services (USE_MOCK_SERVICES=true)")
    except Exception as e:
        logger.warning(f"Could not initialize AWS services: {e}")
        logger.info("Falling back to mock services")


# ============================================================================
# Models
# ============================================================================

class TranscribeRequest(BaseModel):
    audio: str  # base64 encoded audio
    language: str = "en"  # en, hi, kn


class TranscribeResponse(BaseModel):
    text: str
    confidence: float
    language: str
    mode: str = "aws"


class TTSRequest(BaseModel):
    text: str
    language: str = "en"


class SessionCreate(BaseModel):
    language: str = "en"


class SessionResponse(BaseModel):
    session_id: str
    language: str
    created_at: str
    form_data: dict


class FormUpdate(BaseModel):
    field: str
    value: str


# ============================================================================
# Helper Functions
# ============================================================================

def get_session_from_db(session_id: str) -> Optional[dict]:
    """Get session from DynamoDB or memory"""
    try:
        if settings.use_mock_services:
            return sessions_memory.get(session_id)
        
        table = get_sessions_table()
        if table is None:
            return sessions_memory.get(session_id)
        
        response = table.get_item(Key={'session_id': session_id})
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        return sessions_memory.get(session_id)


def save_session_to_db(session_data: dict):
    """Save session to DynamoDB or memory"""
    try:
        if settings.use_mock_services:
            sessions_memory[session_data['session_id']] = session_data
            return
        
        table = get_sessions_table()
        if table is None:
            sessions_memory[session_data['session_id']] = session_data
            return
        
        # Add TTL (24 hours from now)
        ttl = int((datetime.utcnow() + timedelta(hours=settings.session_ttl_hours)).timestamp())
        session_data['ttl'] = ttl
        
        table.put_item(Item=session_data)
        logger.info(f"Session saved to DynamoDB: {session_data['session_id']}")
    except Exception as e:
        logger.error(f"Error saving session: {e}")
        sessions_memory[session_data['session_id']] = session_data


# ============================================================================
# Voice Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "RTI Voice Assistant API",
        "status": "running",
        "version": "2.0.0",
        "mode": "mock" if settings.use_mock_services else "aws",
        "endpoints": {
            "voice": "/voice/transcribe, /voice/tts",
            "session": "/session/create, /session/{id}",
            "form": "/form/{session_id}",
            "guidance": "/guidance/explain",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "mock" if settings.use_mock_services else "aws",
        "services": {
            "bedrock": bedrock_service is not None,
            "polly": polly_service is not None,
            "transcribe": transcribe_service is not None
        }
    }


@app.post("/voice/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(request: TranscribeRequest):
    """
    Transcribe audio to text using AWS Transcribe
    """
    try:
        logger.info(f"Transcription request: language={request.language}")
        
        # Validate language
        if request.language not in settings.supported_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language. Supported: {', '.join(settings.supported_languages)}"
            )
        
        # Decode audio
        try:
            audio_bytes = base64.b64decode(request.audio)
            logger.info(f"Audio size: {len(audio_bytes)} bytes")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail="Invalid audio encoding. Must be base64."
            )
        
        # Use AWS Transcribe if available
        if transcribe_service and not settings.use_mock_services:
            try:
                text, confidence, language = transcribe_service.transcribe_audio(
                    audio_bytes, request.language
                )
                return TranscribeResponse(
                    text=text,
                    confidence=confidence,
                    language=language,
                    mode="aws_transcribe"
                )
            except Exception as e:
                logger.error(f"AWS Transcribe error: {e}")
                logger.info("Falling back to mock transcription")
        
        # Mock transcriptions (fallback)
        mock_transcriptions = {
            'en': 'I want to file an RTI application',
            'hi': 'मैं आरटीआई आवेदन दाखिल करना चाहता हूं',
            'kn': 'ನಾನು ಆರ್‌ಟಿಐ ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಬಯಸುತ್ತೇನೆ'
        }
        
        return TranscribeResponse(
            text=mock_transcriptions[request.language],
            confidence=0.95,
            language=request.language,
            mode="mock"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using AWS Polly
    """
    try:
        logger.info(f"TTS request: language={request.language}, text_length={len(request.text)}")
        
        if request.language not in settings.supported_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language. Supported: {', '.join(settings.supported_languages)}"
            )
        
        # Use AWS Polly if available
        if polly_service and not settings.use_mock_services:
            try:
                audio_bytes = polly_service.synthesize_speech(request.text, request.language)
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                return {
                    "audio": audio_base64,
                    "language": request.language,
                    "format": "mp3",
                    "mode": "aws_polly",
                    "size_bytes": len(audio_bytes)
                }
            except Exception as e:
                logger.error(f"AWS Polly error: {e}")
                logger.info("Falling back to mock TTS")
        
        # Mock audio response (fallback)
        mock_audio = base64.b64encode(b"mock audio data").decode('utf-8')
        
        return {
            "audio": mock_audio,
            "language": request.language,
            "format": "mp3",
            "mode": "mock"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.post("/session/create", response_model=SessionResponse)
async def create_session(request: SessionCreate):
    """Create a new user session"""
    try:
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "language": request.language,
            "created_at": datetime.utcnow().isoformat(),
            "form_data": {}
        }
        
        save_session_to_db(session_data)
        logger.info(f"Created session: {session_id}")
        
        return SessionResponse(**session_data)
    
    except Exception as e:
        logger.error(f"Session creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session data"""
    session_data = get_session_from_db(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(**session_data)


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    session_data = get_session_from_db(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        if not settings.use_mock_services:
            table = get_sessions_table()
            if table:
                table.delete_item(Key={'session_id': session_id})
        
        if session_id in sessions_memory:
            del sessions_memory[session_id]
        
        logger.info(f"Deleted session: {session_id}")
        
        return {"message": "Session deleted", "session_id": session_id}
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RTI Form Endpoints
# ============================================================================

@app.post("/form/{session_id}/update")
async def update_form(session_id: str, update: FormUpdate):
    """Update a form field"""
    session_data = get_session_from_db(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data["form_data"][update.field] = update.value
    save_session_to_db(session_data)
    
    logger.info(f"Updated form field: {update.field} for session {session_id}")
    
    return {
        "message": "Form updated",
        "session_id": session_id,
        "field": update.field,
        "form_data": session_data["form_data"]
    }


@app.get("/form/{session_id}")
async def get_form(session_id: str):
    """Get form data"""
    session_data = get_session_from_db(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "form_data": session_data["form_data"]
    }


@app.post("/form/{session_id}/generate")
async def generate_document(session_id: str):
    """Generate RTI document"""
    session_data = get_session_from_db(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    form_data = session_data["form_data"]
    
    # TODO: Generate actual PDF using reportlab
    document = {
        "session_id": session_id,
        "document_type": "RTI Application",
        "format": "pdf",
        "content": form_data,
        "generated_at": datetime.utcnow().isoformat(),
        "download_url": f"/form/{session_id}/download",
        "message": "Document generation - PDF generation coming soon"
    }
    
    logger.info(f"Generated document for session: {session_id}")
    
    return document


# ============================================================================
# Legal Guidance Endpoints
# ============================================================================

@app.post("/guidance/explain")
async def explain_rti_rights(language: str = "en"):
    """Explain RTI rights in simple language using Amazon Bedrock"""
    try:
        # Use Bedrock if available
        if bedrock_service and not settings.use_mock_services:
            try:
                explanation = bedrock_service.explain_rti_rights(language)
                return {
                    "language": language,
                    "explanation": explanation,
                    "source": "Amazon Bedrock (Claude 3 Haiku)",
                    "mode": "aws_bedrock"
                }
            except Exception as e:
                logger.error(f"Bedrock error: {e}")
                logger.info("Falling back to mock explanation")
        
        # Mock explanations (fallback)
        explanations = {
            'en': "The Right to Information Act allows you to request information from government offices. You can ask questions about government decisions, policies, and actions.",
            'hi': "सूचना का अधिकार अधिनियम आपको सरकारी कार्यालयों से जानकारी मांगने की अनुमति देता है। आप सरकारी निर्णयों, नीतियों और कार्यों के बारे में सवाल पूछ सकते हैं।",
            'kn': "ಮಾಹಿತಿ ಹಕ್ಕು ಕಾಯ್ದೆಯು ಸರ್ಕಾರಿ ಕಛೇರಿಗಳಿಂದ ಮಾಹಿತಿಯನ್ನು ಕೇಳಲು ನಿಮಗೆ ಅನುಮತಿ ನೀಡುತ್ತದೆ."
        }
        
        return {
            "language": language,
            "explanation": explanations.get(language, explanations['en']),
            "source": "RTI Act 2005",
            "mode": "mock"
        }
    except Exception as e:
        logger.error(f"Guidance error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/guidance/next-steps")
async def get_next_steps(session_id: str):
    """Get next steps after RTI submission"""
    
    return {
        "session_id": session_id,
        "next_steps": [
            "Submit your RTI application to the concerned department",
            "You should receive a response within 30 days",
            "If no response, you can file an appeal",
            "Keep your application number for tracking"
        ],
        "timeline": "30 days for response",
        "appeal_info": "File appeal if no response within 30 days"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
