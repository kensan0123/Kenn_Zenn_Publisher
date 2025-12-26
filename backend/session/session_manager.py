import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from backend.schemas.assistant_schemas import (
    WritingSession,
    CreateSessionResponse,
)
from backend.exceptions.exceptions import SessionException
from backend.models.session_model import WritingSessionModel
from backend.core.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    def __init__(self, db: Session):
        self._db: Session = db

    def create_session(self, topic: str) -> CreateSessionResponse:
        """Create session and return session_id"""

        _session_id = str(uuid.uuid4())  # review: session id should created by pre layer.
        if not self.check_db_by_session_id(_session_id):
            created_model: WritingSessionModel = WritingSessionModel(
                session_id=_session_id,
                topic=topic,
            )

            self._db.add(created_model)

            session_response: CreateSessionResponse = CreateSessionResponse(
                status="success",
                session_id=_session_id,
            )

            logger.info("Created session from db")
            return session_response

        raise SessionException(
            message="Session id is already exists.",
            endpoint="/assist",
        )

    def get_session(self, session_id: str) -> WritingSession:
        """Return WritingSession by session_id"""

        fetched_model: WritingSessionModel = self.check_db_by_session_id(session_id=session_id)
        if fetched_model:
            # review: is there a more simple code... (dump into session obj)
            fetched_session: WritingSession = WritingSession(
                session_id=fetched_model.session_id,
                topic=fetched_model.topic,
                target_audience=fetched_model.target_audience,
                outline=fetched_model.outline,
                content=fetched_model.content,
                created_at=fetched_model.created_at,
                updated_at=fetched_model.updated_at,
            )

            logger.info("Got session from db")
            return fetched_session

        else:
            raise SessionException(
                message=f"Session {session_id} not found",
                endpoint="/assist",
            )

    def update_session(self, writing_session: WritingSession) -> CreateSessionResponse:
        """Create session and return session_id"""

        _session_id = writing_session.session_id
        writing_session_json = writing_session.model_dump()

        fetched_model: WritingSessionModel = self.check_db_by_session_id(session_id=_session_id)
        if fetched_model:
            fetched_model.topic = writing_session_json["topic"]
            fetched_model.target_audience = writing_session_json["target_audience"]
            fetched_model.outline = writing_session_json["outline"]
            fetched_model.content = writing_session_json["content"]
            fetched_model.updated_at = datetime.now()

            session_response: CreateSessionResponse = CreateSessionResponse(
                status="success",
                session_id=_session_id,
            )

            logger.info("Updated session form db")
            return session_response

        raise SessionException(
            message="Session not found",
            endpoint="/assist",
        )

    # todo move to session service
    def check_db_by_session_id(self, session_id: str) -> WritingSessionModel | None:
        if not session_id:
            logger.error("No section id")
            raise SessionException(
                message="Rquire session_id",
                endpoint="/assist",
            )
        else:
            result = self._db.get(WritingSessionModel, session_id)
            if result:
                logger.info("Registerd session found")
                return result
            else:
                logger.info("This session_id is not used")
                return None
