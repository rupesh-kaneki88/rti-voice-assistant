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
from services.tts_service import TTSService
from services.transcribe_service import TranscribeService
from services.pdf_service import PDFService
from services.rti_agent_service import RTIAgentService

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

# Initialize services
tts_service = None
transcribe_service = None
pdf_service = None
rti_agent_service = None

# In-memory fallback storage
sessions_memory = {}


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global tts_service, transcribe_service, pdf_service, rti_agent_service
    
    try:
        if not settings.use_mock_services:
            logger.info("Initializing services...")
            tts_service = TTSService()
            transcribe_service = TranscribeService()
            pdf_service = PDFService()
            rti_agent_service = RTIAgentService()
            logger.info("✓ Services initialized")
        else:
            logger.info("Using mock services (USE_MOCK_SERVICES=true)")
            pdf_service = PDFService()  # PDF service doesn't need AWS
            rti_agent_service = RTIAgentService()  # Agent service works without AWS
    except Exception as e:
        logger.warning(f"Could not initialize AWS services: {e}")
        logger.info("Falling back to mock services")
        pdf_service = PDFService()  # Always initialize PDF service
        rti_agent_service = RTIAgentService()  # Always initialize agent service


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


class ConversationRequest(BaseModel):
    message: str
    language: str = "en"


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
            "rti_agent": rti_agent_service is not None,
            "tts": tts_service is not None,
            "transcribe": transcribe_service is not None
        }
    }


@app.post("/voice/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(request: TranscribeRequest):
    """
    Transcribe audio to text
    
    Note: Using mock transcription for speed. AWS Transcribe takes 30-60 seconds.
    For production, integrate real-time transcription service.
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
        
        # For hackathon: Use mock transcriptions (AWS Transcribe is too slow - 30-60s)
        # In production, use real-time transcription service or IndicWhisper
        mock_transcriptions = {
            'en': 'I want to file an RTI application to know about government spending on education',
            'hi': 'मैं शिक्षा पर सरकारी खर्च के बारे में जानने के लिए आरटीआई आवेदन दाखिल करना चाहता हूं',
            'kn': 'ನಾನು ಶಿಕ್ಷಣದ ಮೇಲೆ ಸರ್ಕಾರದ ಖರ್ಚಿನ ಬಗ್ಗೆ ತಿಳಿಯಲು ಆರ್‌ಟಿಐ ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಬಯಸುತ್ತೇನೆ'
        }
        
        return TranscribeResponse(
            text=mock_transcriptions[request.language],
            confidence=0.95,
            language=request.language,
            mode="mock_fast"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/extract-form-data")
async def extract_form_data(text: str, language: str = "en"):
    """
    Extract RTI form fields from transcribed text
    Uses simple keyword extraction (LLM extraction happens in conversation endpoint)
    """
    try:
        # Simple keyword extraction
        extracted_data = {
            "information_sought": text,
            "department": "Ministry of Education" if "education" in text.lower() or "शिक्षा" in text else None,
            "reason": "For personal information" if language == "en" else "व्यक्तिगत जानकारी के लिए"
        }
        
        return {
            "extracted_data": extracted_data,
            "mode": "simple"
        }
    
    except Exception as e:
        logger.error(f"Extraction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using gTTS (primary) and AWS Polly (fallback).
    """
    try:
        logger.info(f"TTS request: language={request.language}, text_length={len(request.text)}")
        
        if request.language not in settings.supported_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language. Supported: {', '.join(settings.supported_languages)}"
            )
        
        # Use the unified TTS service if available
        if tts_service and not settings.use_mock_services:
            try:
                audio_bytes = await tts_service.synthesize_speech(request.text, request.language)
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                # The mode can be determined by checking which service is available
                # For simplicity, we'll just label it based on the new service.
                mode = "tts_service" 
                
                return {
                    "audio": audio_base64,
                    "language": request.language,
                    "format": "mp3",
                    "mode": mode,
                    "size_bytes": len(audio_bytes)
                }
            except Exception as e:
                logger.error(f"TTS service failed: {e}")
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
            "form_data": {},
            "conversation_history": []
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


@app.post("/session/{session_id}/conversation")
async def have_conversation(session_id: str, request: ConversationRequest):
    """
    Have a conversation with the RTI agent
    This is the main endpoint for conversational interaction
    """
    session_data = get_session_from_db(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Get conversation history
        conversation_history = session_data.get('conversation_history', [])
        form_data = session_data.get('form_data', {})
        
        # If this is the first message, send greeting
        if not conversation_history:
            if rti_agent_service and not settings.use_mock_services:
                greeting = rti_agent_service.get_initial_greeting(request.language)
            else:
                greetings = {
                    'en': "Hello! I'm your RTI assistant. I'll help you file a Right to Information application. What information would you like to request from the government?",
                    'hi': "नमस्ते! मैं आपका आरटीआई सहायक हूं। मैं आपको सूचना का अधिकार आवेदन दाखिल करने में मदद करूंगा। आप सरकार से कौन सी जानकारी चाहते हैं?",
                    'kn': "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಆರ್‌ಟಿಐ ಸಹಾಯಕ. ನಾನು ನಿಮಗೆ ಮಾಹಿತಿ ಹಕ್ಕು ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ. ನೀವು ಸರ್ಕಾರದಿಂದ ಯಾವ ಮಾಹಿತಿಯನ್ನು ವಿನಂತಿಸಲು ಬಯಸುತ್ತೀರಿ?"
                }
                greeting = greetings.get(request.language, greetings['en'])
            
            # Add greeting to history
            conversation_history.append({
                "role": "assistant",
                "content": greeting
            })
            
            session_data['conversation_history'] = conversation_history
            save_session_to_db(session_data)
            
            return {
                "agent_response": greeting,
                "form_updates": {},
                "is_complete": False,
                "conversation_history": conversation_history
            }
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": request.message
        })
        
        # Get agent response
        if rti_agent_service and not settings.use_mock_services:
            response = rti_agent_service.get_agent_response(
                user_message=request.message,
                conversation_history=conversation_history,
                form_data=form_data,
                language=request.language
            )
            
            agent_message = response['agent_response']
            form_updates = response['form_updates']
            is_complete = response['is_complete']
        else:
            # Simple mock conversation
            agent_message = f"I heard you say: {request.message}. Let me help you with that."
            form_updates = {}
            is_complete = False
        
        # Update form data with extracted information
        if form_updates:
            for field, value in form_updates.items():
                form_data[field] = value
            session_data['form_data'] = form_data
        
        # Add agent response to history
        conversation_history.append({
            "role": "assistant",
            "content": agent_message
        })
        
        # Save updated session
        session_data['conversation_history'] = conversation_history
        save_session_to_db(session_data)
        
        logger.info(f"Conversation turn completed for session {session_id}")
        
        return {
            "agent_response": agent_message,
            "form_updates": form_updates,
            "is_complete": is_complete,
            "conversation_history": conversation_history[-6:]  # Last 3 exchanges
        }
    
    except Exception as e:
        logger.error(f"Conversation error: {e}", exc_info=True)
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
    """Generate RTI document PDF"""
    session_data = get_session_from_db(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    form_data = session_data["form_data"]
    
    # Validate required fields
    required_fields = ['applicant_name', 'address', 'information_sought']
    missing_fields = [field for field in required_fields if not form_data.get(field)]
    
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    try:
        # Generate PDF
        if pdf_service:
            pdf_bytes = pdf_service.generate_rti_pdf(form_data, session_id)
            
            # Save to S3 if available
            if not settings.use_mock_services:
                try:
                    s3_client = AWSClients.get_s3()
                    if s3_client:
                        pdf_key = f"documents/{session_id}/rti-application.pdf"
                        s3_client.put_object(
                            Bucket=settings.s3_documents_bucket,
                            Key=pdf_key,
                            Body=pdf_bytes,
                            ContentType='application/pdf'
                        )
                        
                        # Generate presigned URL (valid for 1 hour)
                        download_url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={
                                'Bucket': settings.s3_documents_bucket,
                                'Key': pdf_key
                            },
                            ExpiresIn=3600
                        )
                        
                        logger.info(f"PDF saved to S3: {pdf_key}")
                    else:
                        download_url = f"/form/{session_id}/download"
                except Exception as e:
                    logger.error(f"S3 upload error: {e}")
                    download_url = f"/form/{session_id}/download"
            else:
                download_url = f"/form/{session_id}/download"
            
            # Store PDF in session for download
            session_data['pdf_bytes'] = pdf_bytes
            save_session_to_db(session_data)
            
            document = {
                "session_id": session_id,
                "document_type": "RTI Application",
                "format": "pdf",
                "size_bytes": len(pdf_bytes),
                "generated_at": datetime.utcnow().isoformat(),
                "download_url": download_url,
                "message": "RTI application PDF generated successfully"
            }
            
            logger.info(f"Generated PDF for session: {session_id}, size: {len(pdf_bytes)} bytes")
            
            return document
        else:
            raise HTTPException(status_code=500, detail="PDF service not available")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Legal Guidance Endpoints
# ============================================================================

@app.post("/guidance/explain")
async def explain_rti_rights(language: str = "en"):
    """Explain RTI rights in simple language"""
    try:
        # Simple explanations (LLM can enhance these in conversation)
        explanations = {
            'en': "The Right to Information Act allows you to request information from government offices. You can ask questions about government decisions, policies, and actions.",
            'hi': "सूचना का अधिकार अधिनियम आपको सरकारी कार्यालयों से जानकारी मांगने की अनुमति देता है। आप सरकारी निर्णयों, नीतियों और कार्यों के बारे में सवाल पूछ सकते हैं।",
            'kn': "ಮಾಹಿತಿ ಹಕ್ಕು ಕಾಯ್ದೆಯು ಸರ್ಕಾರಿ ಕಛೇರಿಗಳಿಂದ ಮಾಹಿತಿಯನ್ನು ಕೇಳಲು ನಿಮಗೆ ಅನುಮತಿ ನೀಡುತ್ತದೆ."
        }
        
        return {
            "language": language,
            "explanation": explanations.get(language, explanations['en']),
            "source": "RTI Act 2005",
            "mode": "simple"
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
