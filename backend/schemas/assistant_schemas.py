from pydantic import BaseModel
from typing import Dict, Literal, List
from datetime import datetime


class CreateSessionResponse(BaseModel):
    status: Literal["success", "fail"]
    session_id: str | None


class WritingInfo(BaseModel):
    topic: str
    target_audience: Literal["beginner", "intermediate", "advance"] | None = None


class OutlineSection(BaseModel):
    section_id: str
    title: str
    level: int  # h1, h2, ...
    order: int


class WritingSession(BaseModel):
    session_id: str
    topic: str
    target_audience: Literal["beginner", "intermediate", "advance"]
    outline: List[OutlineSection]
    content: Dict[str, str]  # {"section_id", "content"}
    created_at: datetime
    updated_at: datetime


class SuggestionRequest(BaseModel):
    session_id: str
    current_section_id: str
    current_content: str


class Suggestion(BaseModel):
    suggestion_id: str
    type: Literal["structure", "content", "improvement"]
    title: str
    description: str
    priority: int


class SuggestionAgentResponse(BaseModel):
    suggestions: List[Suggestion]
    summary_report: str


class RelatedLink(BaseModel):
    title: str
    url: str
    # source: str
    # relevance_score: float


class SuggestionResponse(BaseModel):
    suggestions: List[Suggestion]
    related_links: List[RelatedLink]
    summary_report: str


class WebSearchResponse(BaseModel):
    search_result: str
    related_links: List[RelatedLink]


class CreateSession(BaseModel):
    session_id: str
    topic: str
