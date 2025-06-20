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
    
    async def _try_generate_question(self, retry_count: int = 0, max_retries: int = 5) -> AIResponse:
        """Internal method to try generating a question with retry logic.

        Args:
            retry_count (int, optional): Current retry attempt. Defaults to 0.
            max_retries (int, optional): Maximum number of retries. Defaults to 3.

        Returns:
            AIResponse: Generated question with answer options

        Raises:
            ServerError: If max retries exceeded
        """
        try:
            prompt = "Generate a music quiz question from any era or genre with 3 answer options (1 correct). "
            prompt += """
            Return the response in the following JSON format:
            {
                "question": "Your question here",
                "options": [
                    {"text": "Option 1", "is_correct": true},
                    {"text": "Option 2", "is_correct": false},
                    {"text": "Option 3", "is_correct": false},
                ],
                "hint": "Optional hint about the correct answer"
            }
            """
            
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
                return await self._try_generate_question(retry_count + 1, max_retries)
            raise
        
    async def generate_question(self) -> AIResponse:
        """Generate a music quiz question with automatic retry on server overload.

        Returns:
            AIResponse: Generated question with answer options
        """
        return await self._try_generate_question()
