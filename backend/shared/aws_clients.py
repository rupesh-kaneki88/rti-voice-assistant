"""
AWS service clients with proper configuration
"""
import boto3
from botocore.config import Config
from typing import Optional
from .config import settings
import logging

logger = logging.getLogger(__name__)


# Boto3 client configuration
boto_config = Config(
    region_name=settings.aws_region,
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'
    }
)


class AWSClients:
    """Singleton class for AWS service clients"""
    
    _dynamodb = None
    _s3 = None
    _bedrock_runtime = None
    _polly = None
    _transcribe = None
    _kms = None
    
    @classmethod
    def get_dynamodb(cls):
        """Get DynamoDB client"""
        if cls._dynamodb is None:
            if settings.use_mock_services:
                logger.info("Using mock DynamoDB")
                return None
            cls._dynamodb = boto3.resource('dynamodb', config=boto_config)
        return cls._dynamodb
    
    @classmethod
    def get_s3(cls):
        """Get S3 client"""
        if cls._s3 is None:
            if settings.use_mock_services:
                logger.info("Using mock S3")
                return None
            cls._s3 = boto3.client('s3', config=boto_config)
        return cls._s3
    
    @classmethod
    def get_bedrock_runtime(cls):
        """Get Bedrock Runtime client"""
        if cls._bedrock_runtime is None:
            if settings.use_mock_services:
                logger.info("Using mock Bedrock")
                return None
            bedrock_config = Config(
                region_name=settings.bedrock_region,
                retries={'max_attempts': 3, 'mode': 'adaptive'}
            )
            cls._bedrock_runtime = boto3.client('bedrock-runtime', config=bedrock_config)
        return cls._bedrock_runtime
    
    @classmethod
    def get_polly(cls):
        """Get Polly client"""
        if cls._polly is None:
            if settings.use_mock_services:
                logger.info("Using mock Polly")
                return None
            cls._polly = boto3.client('polly', config=boto_config)
        return cls._polly
    
    @classmethod
    def get_transcribe(cls):
        """Get Transcribe client"""
        if cls._transcribe is None:
            if settings.use_mock_services:
                logger.info("Using mock Transcribe")
                return None
            cls._transcribe = boto3.client('transcribe', config=boto_config)
        return cls._transcribe
    
    @classmethod
    def get_kms(cls):
        """Get KMS client"""
        if cls._kms is None:
            if settings.use_mock_services:
                logger.info("Using mock KMS")
                return None
            cls._kms = boto3.client('kms', config=boto_config)
        return cls._kms


# Convenience functions
def get_dynamodb_table(table_name: str):
    """Get DynamoDB table resource"""
    dynamodb = AWSClients.get_dynamodb()
    if dynamodb is None:
        return None
    return dynamodb.Table(table_name)


def get_sessions_table():
    """Get sessions DynamoDB table"""
    return get_dynamodb_table(settings.dynamodb_sessions_table)


def get_consent_table():
    """Get consent DynamoDB table"""
    return get_dynamodb_table(settings.dynamodb_consent_table)
