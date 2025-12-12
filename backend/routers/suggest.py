from fastapi import APIRouter
import uuid
from datetime import datetime
from backend.schemas.assistant_schemas import (
    WritingInfo,
    WritingSession,
    SuggestionRequest,
    SuggestionResponse,
)
from backend.services.suggest_service import SuggestSearvice
from backend.session.session_manager import SessionManager

router = APIRouter(prefix="/assist", tags=["assist"])


@router.post("/bigin")
def create_session(writing_info: WritingInfo) -> WritingSession:
    writing_session: WritingSession = WritingSession(
        session_id=str(uuid.uuid4()),
        topic=writing_info.topic,
        target_audience=writing_info.target_audience,
        outline=[],
        content={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    return writing_session


@router.post("/suggest")
def writing_assist(suggest_request: SuggestionRequest) -> SuggestionResponse:
    suggest_service: SuggestSearvice = SuggestSearvice()

    response: SuggestionResponse = suggest_service.generate_suggestion(
        suggest_request=suggest_request
    )

    return response
