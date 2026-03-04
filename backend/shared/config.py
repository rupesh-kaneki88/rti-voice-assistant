"""
Shared configuration for RTI Voice Assistant
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # AWS Configuration
    aws_region: str = os.getenv('AWS_REGION', 'ap-south-1')
    aws_account_id: Optional[str] = os.getenv('AWS_ACCOUNT_ID')
    aws_access_key_id: Optional[str] = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key: Optional[str] = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # DynamoDB Tables
    dynamodb_sessions_table: str = os.getenv('DYNAMODB_SESSIONS_TABLE', 'rti-sessions-dev')
    dynamodb_consent_table: str = os.getenv('DYNAMODB_CONSENT_TABLE', 'rti-consent-dev')
    
    # S3 Buckets
    s3_documents_bucket: str = os.getenv('S3_DOCUMENTS_BUCKET', 'rti-documents-dev')
    s3_audio_bucket: str = os.getenv('S3_AUDIO_BUCKET', 'rti-audio-dev')
    
    # Amazon Bedrock
    bedrock_model_id: str = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
    bedrock_region: str = os.getenv('BEDROCK_REGION', 'us-east-1')  # Bedrock available in us-east-1
    bedrock_max_tokens: int = int(os.getenv('BEDROCK_MAX_TOKENS', '2048'))
    bedrock_temperature: float = float(os.getenv('BEDROCK_TEMPERATURE', '0.7'))

    # LLM providers
    GROQ_API_KEY: Optional[str] = os.getenv('GROQ_API_KEY')
    GROQ_MODEL: str = os.getenv('GROQ_MODEL')

    # Gemini (Fallback - Multilingual)
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL: str = os.getenv('GEMINI_MODEL')
    
    # AWS Polly
    polly_voice_hindi: str = os.getenv('POLLY_VOICE_HINDI', 'Aditi')
    polly_voice_english: str = os.getenv('POLLY_VOICE_ENGLISH', 'Joanna')
    polly_output_format: str = os.getenv('POLLY_OUTPUT_FORMAT', 'mp3')
    
    # AWS Transcribe
    transcribe_language_code_hindi: str = 'hi-IN'
    transcribe_language_code_english: str = 'en-IN'
    
    # Session Configuration
    session_ttl_hours: int = int(os.getenv('SESSION_TTL_HOURS', '24'))
    
    # Logging
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Supported Languages
    supported_languages: list[str] = ['en', 'hi', 'kn']  # English, Hindi, Kannada
    
    # Use mock services for local development
    use_mock_services: bool = os.getenv('USE_MOCK_SERVICES', 'false').lower() == 'true'
    
    class Config:
        env_file = '.env'
        case_sensitive = False


# Global settings instance
settings = Settings()
