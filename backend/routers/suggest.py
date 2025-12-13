from fastapi import APIRouter
from backend.schemas.assistant_schemas import (
    WritingInfo,
    SuggestionRequest,
    SuggestionResponse,
    CreateSessionResponse,
)
from backend.services.suggest_service import SuggestSearvice
from backend.session.session_manager import SessionManager

router = APIRouter(prefix="/assist", tags=["assist"])


@router.post("/bigin")
def create_session(writing_info: WritingInfo) -> CreateSessionResponse:
    """
    Create session

    :param writing_info: info of the article
    :type writing_info: WritingInfo
    :rtype: session_id
    """
    session_manager: SessionManager = SessionManager()

    session_response: CreateSessionResponse = session_manager.create_session(
        writing_info=writing_info
    )

    return session_response


@router.post("/suggest")
def writing_assist(suggest_request: SuggestionRequest) -> SuggestionResponse:
    _suggest_service: SuggestSearvice = SuggestSearvice()

    response: SuggestionResponse = _suggest_service.generate_suggestion(
        suggest_request=suggest_request
    )

    return response
