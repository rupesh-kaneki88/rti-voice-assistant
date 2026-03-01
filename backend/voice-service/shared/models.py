"""
Shared data models for RTI Voice Assistant
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
import time


class LanguageCode(str, Enum):
    """Supported language codes"""
    ENGLISH = "en"
    HINDI = "hi"
    KANNADA = "kn"


class ApplicantCategory(str, Enum):
    """RTI applicant categories"""
    GENERAL = "general"
    BPL = "bpl"  # Below Poverty Line


class InformationFormat(str, Enum):
    """Format for requested information"""
    INSPECTION = "inspection"
    COPY = "copy"
    CERTIFIED_COPY = "certified_copy"


class UrgencyLevel(str, Enum):
    """Urgency level for RTI request"""
    NORMAL = "normal"
    URGENT = "urgent"  # Life and liberty


class SessionStatus(str, Enum):
    """Session status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


# Address Model
class Address(BaseModel):
    """Address information"""
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    pincode: str
    country: str = "India"


# Contact Information
class ContactInformation(BaseModel):
    """Contact details"""
    email: Optional[str] = None
    phone: str
    alternate_phone: Optional[str] = None


# Applicant Details
class ApplicantDetails(BaseModel):
    """RTI applicant information"""
    name: str
    address: Address
    contact_info: ContactInformation
    category: ApplicantCategory = ApplicantCategory.GENERAL


# Information Request
class InformationRequest(BaseModel):
    """Details of information being requested"""
    description: str
    specific_questions: List[str] = Field(default_factory=list)
    timeframe_start: Optional[str] = None
    timeframe_end: Optional[str] = None
    format: InformationFormat = InformationFormat.COPY
    urgency: UrgencyLevel = UrgencyLevel.NORMAL


# Public Authority Information
class PublicAuthorityInfo(BaseModel):
    """Central Government department information"""
    name: str
    department: str
    pio_name: Optional[str] = None
    address: Address


# RTI Application
class RTIApplication(BaseModel):
    """Complete RTI application"""
    id: str
    applicant: ApplicantDetails
    public_authority: PublicAuthorityInfo
    information_sought: InformationRequest
    fee_paid: bool = False
    fee_amount: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Session Model
class Session(BaseModel):
    """User session"""
    session_id: str
    user_id: str
    language: LanguageCode = LanguageCode.ENGLISH
    current_step: str = "welcome"
    form_data: Dict[str, Any] = Field(default_factory=dict)
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    ttl: int = Field(default_factory=lambda: int(time.time()) + 86400)  # 24 hours
    
    @validator('ttl', pre=True, always=True)
    def set_ttl(cls, v):
        """Set TTL to 24 hours from now"""
        if v is None:
            return int(time.time()) + 86400
        return v


# Consent Record
class ConsentRecord(BaseModel):
    """DPDPA consent record"""
    user_id: str
    purposes: List[str]
    consent_given: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ttl: int = Field(default_factory=lambda: int(time.time()) + 86400)
    withdrawal_method: str = "User can withdraw consent by deleting session"


# Voice Preferences
class VoicePreferences(BaseModel):
    """User voice interaction preferences"""
    language: LanguageCode = LanguageCode.ENGLISH
    speech_rate: float = 1.0  # 0.5 to 2.0
    volume: float = 1.0  # 0.0 to 1.0
    voice_id: Optional[str] = None


# Transcription Result
class TranscriptionResult(BaseModel):
    """Speech-to-text result"""
    text: str
    confidence: float
    language: LanguageCode
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# API Response Models
class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
