from typing import Optional
import asyncio
from google import genai
from pydantic import SecretStr

from src.models import AIResponse


class MusicQuizAI:
    def __init__(self, api_key: str | SecretStr) -> None:
        """Initialize the MusicQuizAI with Google API key.

        Args:
            api_key (str | SecretStr): Google API key for authentication
        """
        if isinstance(api_key, SecretStr):
            api_key = api_key.get_secret_value()
        
        self.client = genai.Client(api_key=api_key)
    
    async def _try_generate_question(self, genre: Optional[str] = None, retry_count: int = 0, max_retries: int = 5) -> AIResponse:
        """Internal method to try generating a question with retry logic.

        Args:
            genre (Optional[str], optional): Specific music genre for questions. Defaults to None.
            retry_count (int, optional): Current retry attempt. Defaults to 0.
            max_retries (int, optional): Maximum number of retries. Defaults to 3.

        Returns:
            AIResponse: Generated question with answer options

        Raises:
            ServerError: If max retries exceeded
        """
        try:
            # Update prompt based on genre
            genre_prompt = f" focusing on {genre} music" if genre else ""
            prompt = f"Generate a challenging music quiz question{genre_prompt} with 3 answer options. " + \
                    "Include interesting facts as a hint. Format your response as JSON with the following structure: " + \
                    '{"question": "...", "options": [{"text": "...", "is_correct": true/false}, ...], "hint": "..."}. ' + \
                    "Make sure only one option is correct."
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": AIResponse,
                },
            )
            
            return response.parsed
            
        except Exception as e:
            if "503 UNAVAILABLE" in str(e) and retry_count < max_retries:
                await asyncio.sleep(2 ** retry_count)
                return await self._try_generate_question(genre, retry_count + 1, max_retries)
            raise
        
    async def generate_question(self, genre: Optional[str] = None) -> AIResponse:
        """Generate a music quiz question with automatic retry on server overload.

        Args:
            genre (Optional[str], optional): Specific music genre for the question. Defaults to None.

        Returns:
            AIResponse: Generated question with answer options
        """
        return await self._try_generate_question(genre)
