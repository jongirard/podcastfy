from typing import List, Optional
from ..base import TTSProvider
import requests
import base64
import logging
import json

logger = logging.getLogger(__name__)

class KokorosTTS(TTSProvider):
    """Kokoros Text-to-Speech provider."""
    def __init__(self, api_key: Optional[str] = None, model: str = "tts-1-hd"):
        self.model = model
        print(f"KOKOROS DEBUG: Initialized with model='{model}'")

    def generate_audio(self, text: str, voice: str, model: str, voice2: str = None) -> bytes:
        """Generate audio using Kokoros API."""
        try:
            # Let's see exactly what parameters we're receiving
            print(f"KOKOROS DEBUG: generate_audio called with:")
            print(f"  text: '{text[:100]}...' (length: {len(text)})")
            print(f"  voice: '{voice}'")
            print(f"  model: '{model}'")
            print(f"  self.model: '{self.model}'")
            print(f"  voice2: '{voice2}'")
            
            # Validate parameters
            self.validate_parameters(text, voice, model)
            
            # Prepare the request payload
            payload = {
                "input": text,
                "voice": voice,
                "model": 'kokoro',
                "response_format": 'mp3',
            }
            
            # Log the exact request we're making
            print(f"KOKOROS DEBUG: Making request to http://localhost:8880/v1/audio/speech")
            print(f"KOKOROS DEBUG: Request payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                'http://localhost:8880/v1/audio/speech', 
                json=payload,
                timeout=30  # Add timeout to prevent hanging
            )
            
            # Log response details BEFORE checking status
            print(f"KOKOROS DEBUG: Response status code: {response.status_code}")
            print(f"KOKOROS DEBUG: Response headers: {dict(response.headers)}")
            
            # Try to get response text for debugging (even on error)
            try:
                response_text = response.text
                print(f"KOKOROS DEBUG: Response text: {response_text[:500]}...")
            except:
                print("KOKOROS DEBUG: Could not decode response text")
            
            # Check for errors
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            print(f"KOKOROS ERROR: Exception occurred: {str(e)}")
            logger.error(f"Failed to generate audio: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to generate audio: {str(e)}") from e