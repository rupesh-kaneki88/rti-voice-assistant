"""
RTI Voice Assistant - Main FastAPI Application
Single backend service for hackathon/prototype
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import logging
from typing import Optional
import uuid
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RTI Voice Assistant API",
    description="AI-powered RTI filing assistant for visually impaired users",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for development (replace with DynamoDB in production)
sessions = {}
forms = {}


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
    session_id: Optional[str] = None


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
# Voice Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "RTI Voice Assistant API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "voice": "/voice/transcribe, /voice/tts",
            "session": "/session/create, /session/{id}",
            "form": "/form/{session_id}",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/voice/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(request: TranscribeRequest):
    """
    Transcribe audio to text
    
    For now returns mock data. Will integrate IndicWhisper later.
    """
    try:
        logger.info(f"Transcription request: language={request.language}")
        
        # Validate language
        if request.language not in ['en', 'hi', 'kn']:
            raise HTTPException(
                status_code=400,
                detail="Invalid language. Supported: en, hi, kn"
            )
        
        # Validate audio
        try:
            audio_bytes = base64.b64decode(request.audio)
            logger.info(f"Audio size: {len(audio_bytes)} bytes")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail="Invalid audio encoding. Must be base64."
            )
        
        # Mock transcriptions
        mock_transcriptions = {
            'en': 'I want to file an RTI application',
            'hi': 'मैं आरटीआई आवेदन दाखिल करना चाहता हूं',
            'kn': 'ನಾನು ಆರ್‌ಟಿಐ ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಬಯಸುತ್ತೇನೆ'
        }
        
        return TranscribeResponse(
            text=mock_transcriptions[request.language],
            confidence=0.95,
            language=request.language
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech
    
    For now returns mock data. Will integrate AWS Polly later.
    """
    try:
        logger.info(f"TTS request: language={request.language}, text_length={len(request.text)}")
        
        if request.language not in ['en', 'hi', 'kn']:
            raise HTTPException(
                status_code=400,
                detail="Invalid language. Supported: en, hi, kn"
            )
        
        # Mock audio response (base64 encoded)
        mock_audio = base64.b64encode(b"mock audio data").decode('utf-8')
        
        return {
            "audio": mock_audio,
            "language": request.language,
            "format": "mp3",
            "message": "Mock TTS response. Will use AWS Polly in production."
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
        
        sessions[session_id] = session_data
        logger.info(f"Created session: {session_id}")
        
        return SessionResponse(**session_data)
    
    except Exception as e:
        logger.error(f"Session creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session data"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(**sessions[session_id])


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del sessions[session_id]
    logger.info(f"Deleted session: {session_id}")
    
    return {"message": "Session deleted", "session_id": session_id}


# ============================================================================
# RTI Form Endpoints
# ============================================================================

@app.post("/form/{session_id}/update")
async def update_form(session_id: str, update: FormUpdate):
    """Update a form field"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions[session_id]["form_data"][update.field] = update.value
    logger.info(f"Updated form field: {update.field} for session {session_id}")
    
    return {
        "message": "Form updated",
        "session_id": session_id,
        "field": update.field,
        "form_data": sessions[session_id]["form_data"]
    }


@app.get("/form/{session_id}")
async def get_form(session_id: str):
    """Get form data"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "form_data": sessions[session_id]["form_data"]
    }


@app.post("/form/{session_id}/generate")
async def generate_document(session_id: str):
    """Generate RTI document"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    form_data = sessions[session_id]["form_data"]
    
    # Mock document generation
    document = {
        "session_id": session_id,
        "document_type": "RTI Application",
        "format": "pdf",
        "content": form_data,
        "generated_at": datetime.utcnow().isoformat(),
        "download_url": f"/form/{session_id}/download",
        "message": "Mock document. Will generate real PDF in production."
    }
    
    logger.info(f"Generated document for session: {session_id}")
    
    return document


@app.get("/form/{session_id}/download")
async def download_document(session_id: str):
    """Download generated RTI document"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Mock PDF download
    return {
        "message": "Document download endpoint",
        "session_id": session_id,
        "note": "Will return actual PDF in production"
    }


# ============================================================================
# Legal Guidance Endpoints
# ============================================================================

@app.post("/guidance/explain")
async def explain_rti_rights(language: str = "en"):
    """Explain RTI rights in simple language"""
    
    explanations = {
        'en': "The Right to Information Act allows you to request information from government offices. You can ask questions about government decisions, policies, and actions.",
        'hi': "सूचना का अधिकार अधिनियम आपको सरकारी कार्यालयों से जानकारी मांगने की अनुमति देता है। आप सरकारी निर्णयों, नीतियों और कार्यों के बारे में सवाल पूछ सकते हैं।",
        'kn': "ಮಾಹಿತಿ ಹಕ್ಕು ಕಾಯ್ದೆಯು ಸರ್ಕಾರಿ ಕಛೇರಿಗಳಿಂದ ಮಾಹಿತಿಯನ್ನು ಕೇಳಲು ನಿಮಗೆ ಅನುಮತಿ ನೀಡುತ್ತದೆ."
    }
    
    return {
        "language": language,
        "explanation": explanations.get(language, explanations['en']),
        "source": "RTI Act 2005"
    }


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
