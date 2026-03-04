"""
Groq LLM Provider - Fast inference with LLaMA 3 and Mixtral
"""
import os
import logging
from typing import Dict, List
from .base_provider import BaseLLMProvider

from shared.config import settings

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """Groq provider for fast LLM inference"""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.client = None
        
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                logger.info(f"✓ Groq initialized with model: {self.model}")
            except ImportError:
                logger.warning("Groq package not installed. Run: pip install groq")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq: {e}")
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Generate response using Groq"""
        if not self.client:
            raise Exception("Groq client not initialized")
        
        # Build messages with system prompt
        groq_messages = [{"role": "system", "content": system_prompt}]
        groq_messages.extend(messages)
        
        logger.info(f"Calling Groq ({self.model})...")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=groq_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9
        )
        
        result = response.choices[0].message.content
        logger.info(f"✓ Groq response: {result[:100]}...")
        
        return result
    
    def is_available(self) -> bool:
        """Check if Groq is available"""
        return self.client is not None
    
    @property
    def name(self) -> str:
        return f"Groq ({self.model})"
