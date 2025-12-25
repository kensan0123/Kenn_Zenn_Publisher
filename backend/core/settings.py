from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_API_KEY_FILE: str
    ANTHROPIC_API_KEY: str
    ANTHROPIC_API_KEY_FILE: str
    ROOT_DIR: str = Field(default="/app")
    ARTICLE_DIR: str = Field(default="./articles")
    GITHUB_USER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @model_validator(mode="before")
    @classmethod
    def load_secrets_from_files(cls, data: dict) -> dict:
        """Docker Secretsファイルから認証情報を読み込む"""
        if not data.get("OPENAI_API_KEY"):
            file_path = data.get("OPENAI_API_KEY_FILE")
            if file_path and Path(file_path).exists():
                key = Path(file_path).read_text().strip()
                if key.startswith("sk-"):
                    data["OPENAI_API_KEY"] = key

        if not data.get("ANTHROPIC_API_KEY"):
            file_path = data.get("ANTHROPIC_API_KEY_FILE")
            if file_path and Path(file_path).exists():
                key = Path(file_path).read_text().strip()
                if key.startswith("sk-"):
                    data["ANTHROPIC_API_KEY"] = key

        return data

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v):
        """OPENAI_API_KEYが必須であることを検証"""
        if not v or not v.startswith("sk-"):
            raise ValueError("Valid OPENAI_API_KEY is required")
        return v

    @field_validator("ANTHROPIC_API_KEY")
    @classmethod
    def validate_anthropic_key(cls, v):
        """ANTHROPIC_API_KEYが必須であることを検証"""
        if not v or not v.startswith("sk-"):
            raise ValueError("Valid ANTHROPIC_API_KEY is required")
        return v


settings: Settings = Settings()  # type: ignore
