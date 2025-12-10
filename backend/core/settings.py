from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = None
    OPENAI_API_KEY_FILE: str | None = None
    ROOT_DIR: str
    ARTICLE_DIR: str = Field(default="./articles")
    GITHUB_USER: str
    GITHUB_PAT: str | None = None
    GITHUB_PAT_FILE: str | None = None

    @model_validator(mode="before")
    @classmethod
    def load_secrets_from_files(cls, data: dict) -> dict:
        """Docker Secretsファイルから認証情報を読み込む"""
        # OPENAI_API_KEY の読み込み
        if not data.get("OPENAI_API_KEY"):
            file_path = data.get("OPENAI_API_KEY_FILE")
            if file_path and Path(file_path).exists():
                key = Path(file_path).read_text().strip()
                if key.startswith("sk-"):
                    data["OPENAI_API_KEY"] = key

        # GITHUB_PAT の読み込み
        if not data.get("GITHUB_PAT"):
            file_path = data.get("GITHUB_PAT_FILE")
            if file_path and Path(file_path).exists():
                pat = Path(file_path).read_text().strip()
                if pat.startswith("ghp_"):
                    data["GITHUB_PAT"] = pat

        return data

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v):
        """OPENAI_API_KEYが必須であることを検証"""
        if not v or not v.startswith("sk-"):
            raise ValueError("Valid OPENAI_API_KEY is required")
        return v

    @field_validator("GITHUB_PAT")
    @classmethod
    def validate_github_pat(cls, v):
        """GITHUB_PATが必須であることを検証"""
        if not v or not v.startswith("ghp_"):
            raise ValueError("Valid GITHUB_PAT is required")
        return v
