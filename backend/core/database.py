from typing import Generator
import json
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from backend.core.settings import settings
from backend.models.session_model import Base


class DataBase:
    def __init__(self) -> None:
        self._user: str = settings.POSTGRES_USER
        self._pass: str = settings.POSTGRES_PASSWORD
        self._db: str = settings.POSTGRES_DB
        self._host: str = "postgres"
        self._port: int = 5432

        self._database_url = (
            f"postgresql://{self._user}:{self._pass}@{self._host}:{self._port}/{self._db}"
        )

        self._engine: Engine = create_engine(
            self._database_url,
            echo=True,
            pool_pre_ping=True,
            json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
        )

        self._session_local = sessionmaker(
            autoflush=False,
            bind=self._engine,
        )

    @property
    def engine(self) -> Engine:
        """ "エンジンを取得"""
        return self._engine

    def get_session(self) -> Generator[Session, None, None]:
        """sessionを取得"""
        session = self._session_local()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_tables(self) -> None:
        """全テーブルを作成"""
        Base.metadata.create_all(self._engine)


database = DataBase()


def get_db() -> Generator[Session, None, None]:
    yield from database.get_session()
