from typing import Literal

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    title: str
    emoji: str
    type: str
    content: str


class AIGenerateRequest(BaseModel):
    prompt: str


class GeneratedResponse(BaseModel):
    status: Literal["success", "error"]
    slug: str


class AIPrompt(BaseModel):
    prompt: str


class PublishRequest(BaseModel):
    slug: str


class PublishResponse(BaseModel):
    status: Literal["published!", "failed"]
    slug: str


class PublishResult(BaseModel):
    result: bool
    slug: str
