from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.schemas.assistant_schemas import (
    WritingInfo,
    SuggestionRequest,
    SuggestionResponse,
    CreateSessionResponse,
)
from backend.services.suggest_service import SuggestSearvice
from backend.session.session_manager import SessionManager
from backend.core.database import get_db

router = APIRouter(prefix="/assist", tags=["assist"])


@router.post("/begin")
def begin_session(
    writing_info: WritingInfo, db: Session = Depends(get_db)
) -> CreateSessionResponse:
    session_manager: SessionManager = SessionManager(db=db)

    session_response: CreateSessionResponse = session_manager.create_session(
        topic=writing_info.topic
    )

    return session_response


@router.post("/suggest")
def writing_assist(suggest_request: SuggestionRequest) -> SuggestionResponse:
    _suggest_service: SuggestSearvice = SuggestSearvice()

    response: SuggestionResponse = _suggest_service.generate_suggestion(
        suggest_request=suggest_request
    )

    return response
