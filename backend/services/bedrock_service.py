"""
Amazon Bedrock service for legal guidance and simplification
"""
import json
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.config import settings
from shared.aws_clients import AWSClients

logger = logging.getLogger(__name__)


class BedrockService:
    """Service for legal guidance using Amazon Bedrock (Claude)"""
    
    def __init__(self):
        self.bedrock_client = AWSClients.get_bedrock_runtime()
        self.model_id = settings.bedrock_model_id
    
    def explain_rti_rights(self, language: str = 'en') -> str:
        """
        Explain RTI rights in simple language
        
        Args:
            language: Language code (en, hi, kn)
            
        Returns:
            Simplified explanation
        """
        try:
            language_names = {
                'en': 'English',
                'hi': 'Hindi',
                'kn': 'Kannada'
            }
            
            lang_name = language_names.get(language, 'English')
            
            prompt = f"""You are a helpful assistant explaining the Right to Information (RTI) Act 2005 in India.

Explain the RTI rights in simple, easy-to-understand {lang_name} language suitable for someone who may not be familiar with legal terminology.

Cover these key points:
1. What is RTI?
2. Who can file an RTI?
3. What information can you request?
4. How long does it take to get a response?
5. Is there a fee?

Keep the explanation concise (under 200 words) and use simple language."""

            if language == 'hi':
                prompt += "\n\nProvide the explanation in Hindi."
            elif language == 'kn':
                prompt += "\n\nProvide the explanation in Kannada."
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": settings.bedrock_max_tokens,
                "temperature": settings.bedrock_temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            logger.info(f"Calling Bedrock for RTI explanation: language={language}")
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            explanation = response_body['content'][0]['text']
            
            logger.info(f"Bedrock response received: {len(explanation)} chars")
            
            return explanation
        
        except Exception as e:
            logger.error(f"Bedrock error: {e}", exc_info=True)
            raise
    
    def simplify_legal_text(self, text: str, language: str = 'en') -> str:
        """
        Simplify legal text for better understanding
        
        Args:
            text: Legal text to simplify
            language: Target language
            
        Returns:
            Simplified text
        """
        try:
            prompt = f"""Simplify the following legal text into easy-to-understand language:

{text}

Provide a simple explanation that a common person can understand."""

            if language == 'hi':
                prompt += "\n\nProvide the explanation in Hindi."
            elif language == 'kn':
                prompt += "\n\nProvide the explanation in Kannada."
            
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": settings.bedrock_max_tokens,
                "temperature": settings.bedrock_temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            simplified = response_body['content'][0]['text']
            
            return simplified
        
        except Exception as e:
            logger.error(f"Bedrock simplification error: {e}", exc_info=True)
            raise
