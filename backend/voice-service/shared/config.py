"""
Shared configuration for RTI Voice Assistant Lambda functions
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # AWS Configuration
    aws_region: str = os.getenv('AWS_REGION', 'ap-south-1')
    aws_account_id: Optional[str] = os.getenv('AWS_ACCOUNT_ID')
    
    # DynamoDB Tables
    dynamodb_sessions_table: str = os.getenv('DYNAMODB_SESSIONS_TABLE', 'rti-sessions-dev')
    dynamodb_consent_table: str = os.getenv('DYNAMODB_CONSENT_TABLE', 'rti-consent-dev')
    
    # S3 Buckets
    s3_documents_bucket: str = os.getenv('S3_DOCUMENTS_BUCKET', '')
    s3_knowledge_base_bucket: str = os.getenv('S3_KNOWLEDGE_BASE_BUCKET', '')
    
    # Amazon Bedrock
    bedrock_model_id: str = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
    bedrock_region: str = os.getenv('BEDROCK_REGION', 'ap-south-1')
    bedrock_max_tokens: int = int(os.getenv('BEDROCK_MAX_TOKENS', '2048'))
    bedrock_temperature: float = float(os.getenv('BEDROCK_TEMPERATURE', '0.7'))
    
    # AWS Polly
    polly_voice_hindi: str = os.getenv('POLLY_VOICE_HINDI', 'Aditi')
    polly_voice_english: str = os.getenv('POLLY_VOICE_ENGLISH', 'Joanna')
    polly_output_format: str = os.getenv('POLLY_OUTPUT_FORMAT', 'mp3')
    
    # Session Configuration
    session_ttl_hours: int = int(os.getenv('SESSION_TTL_HOURS', '24'))
    
    # Lambda Configuration
    lambda_timeout: int = int(os.getenv('LAMBDA_TIMEOUT', '900'))
    lambda_memory: int = int(os.getenv('LAMBDA_MEMORY', '10240'))
    
    # Logging
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Supported Languages
    supported_languages: list[str] = ['en', 'hi', 'kn']  # English, Hindi, Kannada
    
    class Config:
        env_file = '.env'
        case_sensitive = False


# Global settings instance
settings = Settings()
