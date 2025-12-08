from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OLLAMA_URL: str
    KENN_ZENN_URL: str
    openai_api_key: str
