from sqlalchemy.orm import Session
from backend.session.session_manager import SessionManager
from backend.agents.suggestion_agent import SuggestAgent
from backend.schemas.assistant_schemas import (
    WritingSession,
    SuggestionResponse,
    SuggestionRequest,
    UpdatedSessionResponse,
)
from backend.core.logger import get_logger

logger = get_logger(__name__)


# refactor: thre are complex roule each function may access by id or obj...
class SuggestService:
    """agentとsessionを定義する"""

    def __init__(self, db: Session):
        self._session_manager: SessionManager = SessionManager(db=db)
        self._suggest_agent: SuggestAgent = SuggestAgent()

    def update_session(
        self,
        writing_session: WritingSession,
    ) -> UpdatedSessionResponse:
        result = self._session_manager.update_session(
            writing_session=writing_session,
        )

        if result:
            res = UpdatedSessionResponse(status="success", session_id=writing_session.session_id)
            logger.info("Succeed update: session_id=%s", writing_session.session_id)
            return res
        else:
            res = UpdatedSessionResponse(status="fail", session_id=writing_session.session_id)
            logger.info("Failed to update: session_id=%s", writing_session.session_id)
            return res

    def generate_suggestion(
        self,
        suggest_request: SuggestionRequest,
        writing_session: WritingSession,
    ) -> SuggestionResponse:
        # refact: is this right to save session in this point? This is insane...(db up and get)
        logger.info("Update session to generate suggestion")
        self.update_session(writing_session=writing_session)

        logger.info("Fetch session to generate suggestion")
        _writing_session: WritingSession = self._session_manager.get_session(
            session_id=suggest_request.session_id,
        )

        logger.info("Generating suggestion")
        response: SuggestionResponse = self._suggest_agent.generate_suggestion(
            writing_session=_writing_session,
            current_section_id=suggest_request.current_section_id,
            current_content=suggest_request.current_content,
        )

        return response
