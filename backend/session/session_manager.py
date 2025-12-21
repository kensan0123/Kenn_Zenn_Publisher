from fastapi import Depends
from typing import Dict
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from backend.schemas.assistant_schemas import (
    WritingSession,
    WritingInfo,
    CreateSessionResponse,
    CreateSession,
)
from backend.exceptions.exceptions import SessionException
from backend.core.database import get_db
from backend.models.session_model import WritingSessionModel


class SessionManager:
    def __init__(self, db: Session):
        self._db: Session = db

    def create_session(self, topic: str) -> CreateSessionResponse:
        """Create session and return session_id"""

        _session_id = str(uuid.uuid4())
        if not self.already_registered_session_id(_session_id):
            created_session_model: WritingSessionModel = WritingSessionModel(
                session_id=_session_id,
                topic=topic,
            )

            self._db.add(created_session_model)

            session_response: CreateSessionResponse = CreateSessionResponse(
                status="success",
                session_id=_session_id,
            )

            return session_response

        raise SessionException(
            message="Session id is already exists.",
            endpoint="/assist",
        )

    def get_session(self, session_id: str) -> WritingSession:
        """Return WritingSession by session_id"""
        if self.already_registered_session_id(session_id=session_id):
            fetched_session: WritingSession = self._db.get(
                WritingSessionModel, {"session_id": session_id}
            )

        else:
            raise SessionException(
                message=f"Session {session_id} not found",
                endpoint="/assist",
            )

        return fetched_session

    def update_session(self, writing_session: WritingSession, db: Session) -> CreateSessionResponse:
        """Create session and return session_id"""

        _session_id = writing_session.session_id
        if self.already_registered_session_id(session_id=_session_id):
            _updated_session: WritingSession = writing_session

            session_response: CreateSessionResponse = CreateSessionResponse(
                status="success",
                session_id=_updated_session.session_id,
            )

            return session_response

        raise SessionException(
            message="Session id is already exists.",
            endpoint="/assist",
        )

    def already_registered_session_id(self, session_id: str) -> bool:
        if self._db:
            return False
        else:
            return True
