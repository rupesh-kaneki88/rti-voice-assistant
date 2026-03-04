"""
Base LLM Provider Interface
"""
from abc import ABC, abstractmethod
from typing import Dict, List


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a response from the LLM
        
        Args:
            messages: List of conversation messages [{"role": "user", "content": "..."}]
            system_prompt: System instructions for the model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for logging"""
        pass
