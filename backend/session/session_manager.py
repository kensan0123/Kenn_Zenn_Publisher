from typing import Dict
import uuid
from datetime import datetime
from backend.schemas.assistant_schemas import WritingSession, WritingInfo, CreateSessionResponse
from backend.exceptions.exceptions import SessionException


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, WritingSession] = {}

    def create_session(self, writing_info: WritingInfo) -> CreateSessionResponse:
        """Create session and return session_id"""
        _session_id = str(uuid.uuid4())
        if _session_id not in self._sessions:
            created_session: WritingSession = WritingSession(
                session_id=_session_id,
                topic=writing_info.topic,
                target_audience=writing_info.target_audience,
                outline=[],
                content={},
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            self._sessions[created_session.session_id] = created_session

            session_response: CreateSessionResponse = CreateSessionResponse(
                status="success",
                session_id=created_session.session_id,
            )

            return session_response

        raise SessionException(
            message="Session id is already exists.",
            endpoint="/assist",
        )

    def get_session(self, session_id: str) -> WritingSession:
        """Return WritingSession by session_id"""
        if session_id not in self._sessions:
            raise SessionException(
                message=f"Session {session_id} not found",
                endpoint="/assist",
            )

        writing_session: WritingSession = self._sessions[session_id]

        return writing_session
