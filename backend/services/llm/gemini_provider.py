"""
Google Gemini Provider - Multilingual support with Gemini 1.5 Flash
"""
import os
import logging
from typing import Dict, List
from .base_provider import BaseLLMProvider
from shared.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider for multilingual support"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.client = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
                logger.info(f"✓ Gemini initialized with model: {self.model_name}")
            except ImportError as e:
                logger.warning("Gemini import failed: %s", e)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Generate response using Gemini"""
        if not self.client:
            raise Exception("Gemini client not initialized")
        
        # Build conversation for Gemini
        # Gemini uses a different format - combine system prompt with first user message
        conversation_text = f"{system_prompt}\n\n"
        
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation_text += f"{role}: {msg['content']}\n"
        
        conversation_text += "Assistant:"
        
        logger.info(f"Calling Gemini ({self.model_name})...")
        
        response = self.client.generate_content(
            conversation_text,
            generation_config={
                'max_output_tokens': max_tokens,
                'temperature': temperature,
                'top_p': 0.9
            }
        )
        
        result = response.text
        logger.info(f"✓ Gemini response: {result[:100]}...")
        
        return result
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.client is not None
    
    @property
    def name(self) -> str:
        return f"Gemini ({self.model_name})"
