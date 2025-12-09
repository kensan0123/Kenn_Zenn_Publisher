from typing import Literal

from pydantic import BaseModel


class PublishRequest(BaseModel):
    slug: str


class PublishResponse(BaseModel):
    status: Literal["published!", "failed"]
    slug: str


class PublishResult(BaseModel):
    result: bool
    slug: str
