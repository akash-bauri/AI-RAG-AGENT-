from pydantic import BaseModel, Field
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class GoogleLoginRequest(BaseModel):
    id_token: str


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's text question."
    )
    age: Optional[int] = Field(None, ge=0, le=120)
    monthly_income: Optional[float] = Field(None, ge=0.0)
    goal: Optional[str] = Field(None, max_length=200)


class ChatResponse(BaseModel):
    answer: str
    source_type: str
    source_name: str
    detected_language: str
    free_limit_reached: bool


class QuestionResponse(BaseModel):
    id: str
    category: str
    question: str
    language: str


class UserProfileResponse(BaseModel):
    user_id: str
    name: str
    email: str
    language_preference: str
    query_count: int
