from pydantic import BaseModel
from typing import List, Optional


class AnswerOption(BaseModel):
    text: str
    is_correct: bool


class AIResponse(BaseModel):
    question: str
    options: List[AnswerOption]
    hint: Optional[str]
