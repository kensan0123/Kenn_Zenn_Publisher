import uuid
from datetime import datetime
from sqlalchemy import String, JSON, DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WritingSessionModel(Base):
    """WritingSessionのテーブルモデル"""

    __tablename__ = "writing_session"
    session_id = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),  # refactor: invert to server_default
    )
    topic = mapped_column(
        String(50),
        nullable=False,
    )
    target_audience = mapped_column(
        String(50),
    )
    outline = mapped_column(
        JSON,
        default=list,
    )
    content = mapped_column(
        JSON,
        default=dict,
    )
    created_at = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    def __repr__(self) -> str:
        return f"<WritingSession(session_id={self.session_id}, topic={self.topic})>)"
