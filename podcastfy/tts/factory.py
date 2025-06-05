"""Factory for creating TTS providers."""

from typing import Dict, Type, Optional
from .base import TTSProvider
from .providers.elevenlabs import ElevenLabsTTS
from .providers.openai import OpenAITTS
from .providers.edge import EdgeTTS
from .providers.gemini import GeminiTTS
from .providers.kokoros import KokorosTTS
from .providers.geminimulti import GeminiMultiTTS
class TTSProviderFactory:
    """Factory class for creating TTS providers."""
    
    _providers: Dict[str, Type[TTSProvider]] = {
        'elevenlabs': ElevenLabsTTS,
        'openai': OpenAITTS,
        'kokoros': KokorosTTS,
        'edge': EdgeTTS,
        'gemini': GeminiTTS,
        'geminimulti': GeminiMultiTTS
    }
    
    @classmethod
    def create(cls, provider_name: str, api_key: Optional[str] = None, model: Optional[str] = None) -> TTSProvider:
        """Create a TTS provider instance."""
        print(f"DEBUG Factory: Creating provider '{provider_name}' with model '{model}'")
        
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            print(f"DEBUG Factory: Provider '{provider_name}' not found in {list(cls._providers.keys())}")
            raise ValueError(f"Unsupported provider: {provider_name}. "
                          f"Choose from: {', '.join(cls._providers.keys())}")
        
        print(f"DEBUG Factory: Found provider class: {provider_class}")
        
        instance = provider_class(api_key, model) if api_key else provider_class(model=model)
        print(f"DEBUG Factory: Created instance: {type(instance).__name__}")
        return instance
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[TTSProvider]) -> None:
        """Register a new provider class."""
        cls._providers[name.lower()] = provider_class 