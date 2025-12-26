from fastapi import APIRouter, Depends
import time
from sqlalchemy.orm import Session
from backend.schemas.assistant_schemas import (
    WritingInfo,
    SuggestionRequest,
    SuggestionResponse,
    CreateSessionResponse,
    WritingSession,
)
from backend.services.suggest_service import SuggestService
from backend.session.session_manager import SessionManager
from backend.core.database import get_db
from backend.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/assist", tags=["assist"])


@router.post("/begin")
def begin_session(
    writing_info: WritingInfo,
    db: Session = Depends(get_db),
) -> CreateSessionResponse:
    start = time.perf_counter()
    logger.info("Creating session with topic: %s", writing_info.topic)
    session_manager: SessionManager = SessionManager(db=db)

    session_response: CreateSessionResponse = session_manager.create_session(
        topic=writing_info.topic
    )
    elapsed = time.perf_counter() - start
    logger.info(
        "Session created: session_id=%s, elapsed=%.2fs", session_response.session_id, elapsed
    )
    return session_response


@router.post("/suggest")
def assist_writing(
    suggest_request: SuggestionRequest,
    writing_session: WritingSession,
    db: Session = Depends(get_db),
) -> SuggestionResponse:
    start = time.perf_counter()
    logger.info("Generating suggestion: session_id=%s", suggest_request.session_id)
    suggest_service: SuggestService = SuggestService(db=db)

    response: SuggestionResponse = suggest_service.generate_suggestion(
        suggest_request=suggest_request,
        writing_session=writing_session,
    )
    elapsed = time.perf_counter() - start
    logger.info(
        "Suggestion generated: session_id=%s, elapsed=%.2fs",
        suggest_request.session_id,
        elapsed,
    )
    return response


@router.post("/update")
def update_writing(
    writing_session: WritingSession,
    db: Session = Depends(get_db),
):
    logger.info("Updating session: session_id=%s", writing_session.session_id)
    suggest_service: SuggestService = SuggestService(db=db)

    response = suggest_service.update_session(writing_session=writing_session)
    return response
