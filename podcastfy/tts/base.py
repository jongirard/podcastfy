"""Abstract base class for Text-to-Speech providers."""

from abc import ABC, abstractmethod
from typing import List, ClassVar, Tuple
import re

class TTSProvider(ABC):
    """Abstract base class that defines the interface for TTS providers."""
    
    # Common SSML tags supported by most providers
    COMMON_SSML_TAGS: ClassVar[List[str]] = [
        'lang', 'p', 'phoneme', 's', 'sub'
    ]
    
    @abstractmethod
    def generate_audio(self, text: str, voice: str, model: str, voice2: str) -> bytes:
        """
        Generate audio from text using the provider's API.
        
        Args:
            text: Text to convert to speech
            voice: Voice ID/name to use
            model: Model ID/name to use
            
        Returns:
            Audio data as bytes
            
        Raises:
            ValueError: If invalid parameters are provided
            RuntimeError: If audio generation fails
        """
        pass

    def get_supported_tags(self) -> List[str]:
        """
        Get set of SSML tags supported by this provider.
        
        Returns:
            Set of supported SSML tag names
        """
        return self.COMMON_SSML_TAGS.copy()
    
    def validate_parameters(self, text: str, voice: str, model: str, voice2: str = None) -> None:
        """
        Validate input parameters before generating audio.
        
        Raises:
            ValueError: If any parameter is invalid
        """
        if not text:
            raise ValueError("Text cannot be empty")
        if not voice:
            raise ValueError("Voice must be specified")
        if not model:
            raise ValueError("Model must be specified")
        
    def split_qa(self, input_text: str, ending_message: str, supported_tags: List[str] = None) -> List[Tuple[str, str]]:
        """
        Split the input text into question-answer pairs, handling both complete pairs 
        and standalone Person1 blocks.

        Args:
            input_text (str): The input text containing Person1 and Person2 dialogues.
            ending_message (str): The ending message (currently unused, kept for compatibility).

        Returns:
            List[Tuple[str, str]]: A list of tuples containing (Person1, Person2) dialogues.
                                  Standalone Person1 blocks will have empty string as Person2.
        """
        input_text = self.clean_tss_markup(input_text, supported_tags=supported_tags)
        
        # Add placeholder if input_text starts with <Person2>
        if input_text.strip().startswith("<Person2>"):
            input_text = "<Person1> Humm... </Person1>" + input_text

        # Strategy: Instead of forcing pairs, let's find all Person1 and Person2 blocks
        # separately, then intelligently pair them up
        
        # Find all Person1 blocks with their positions
        person1_pattern = r"<Person1>(.*?)</Person1>"
        person1_matches = []
        for match in re.finditer(person1_pattern, input_text, re.DOTALL):
            content = " ".join(match.group(1).split()).strip()
            person1_matches.append((content, match.start(), match.end()))
        
        # Find all Person2 blocks with their positions  
        person2_pattern = r"<Person2>(.*?)</Person2>"
        person2_matches = []
        for match in re.finditer(person2_pattern, input_text, re.DOTALL):
            content = " ".join(match.group(1).split()).strip()
            person2_matches.append((content, match.start(), match.end()))
        
        # Now pair them up intelligently
        processed_matches = []
        person2_index = 0  # Track which Person2 we're looking at
        
        for person1_content, p1_start, p1_end in person1_matches:
            # Look for the next Person2 that comes after this Person1
            paired_person2 = ""
            
            # Check if there's a Person2 that starts after this Person1 ends
            while person2_index < len(person2_matches):
                p2_content, p2_start, p2_end = person2_matches[person2_index]
                
                if p2_start >= p1_end:  # This Person2 comes after our Person1
                    paired_person2 = p2_content
                    person2_index += 1  # Move to next Person2 for next iteration
                    break
                else:
                    # This Person2 comes before our Person1, skip it
                    person2_index += 1
            
            # Add the pair (even if Person2 is empty)
            processed_matches.append((person1_content, paired_person2))
        
        return processed_matches

    def clean_tss_markup(self, input_text: str, additional_tags: List[str] = ["Person1", "Person2"], supported_tags: List[str] = None) -> str:
        """
        Remove unsupported TSS markup tags from the input text while preserving supported SSML tags.

        Args:
            input_text (str): The input text containing TSS markup tags.
            additional_tags (List[str]): Optional list of additional tags to preserve. Defaults to ["Person1", "Person2"].
            supported_tags (List[str]): Optional list of supported tags. If None, use COMMON_SSML_TAGS.
        Returns:
            str: Cleaned text with unsupported TSS markup tags removed.
        """
        if supported_tags is None:
            supported_tags = self.COMMON_SSML_TAGS.copy()

        # Append additional tags to the supported tags list
        supported_tags.extend(additional_tags)

        # Create a pattern that matches any tag not in the supported list
        pattern = r'</?(?!(?:' + '|'.join(supported_tags) + r')\b)[^>]+>'

        # Remove unsupported tags
        cleaned_text = re.sub(pattern, '', input_text)

        # Remove any leftover empty lines
        cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)

        # Ensure closing tags for additional tags are preserved
        for tag in additional_tags:
            cleaned_text = re.sub(f'<{tag}>(.*?)(?=<(?:{"|".join(additional_tags)})>|$)', 
                                f'<{tag}>\\1</{tag}>', 
                                cleaned_text, 
                                flags=re.DOTALL)

        return cleaned_text.strip()