from backend.session.session_manager import SessionManager
from backend.agents.suggestion_agent import SuggestAgent
from backend.schemas.assistant_schemas import WritingSession, SuggestionResponse, SuggestionRequest


class SuggestSearvice:
    """agentとのsessionを定義する"""

    def __init__(self):
        self._session_manager: SessionManager = SessionManager()
        self._suggest_agent: SuggestAgent = SuggestAgent()

    def generate_suggestion(self, suggest_request: SuggestionRequest) -> SuggestionResponse:
        _writing_session: WritingSession = self._session_manager.get_session(
            session_id=suggest_request.session_id
        )

        response: SuggestionResponse = self._suggest_agent.generate_suggestion(
            writing_session=_writing_session,
            current_section_id=suggest_request.current_section_id,
            current_content=suggest_request.current_content,
        )

        return response
