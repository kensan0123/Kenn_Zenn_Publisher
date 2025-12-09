from pydantic import Field
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    OPENAI_API_KEY: str = Field(pattern=r"^sk-.+")
    ROOT_DIR: str
    ARTICLE_DIR: str = Field(default="./articles")
    GITHUB_USER: str
    GITHUB_PAT: str
