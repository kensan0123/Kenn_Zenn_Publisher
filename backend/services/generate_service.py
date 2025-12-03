from routers.generate import GenerateRequest
import requests
from pydantic import BaseModel
from typing import Literal

class GeneratedResponse(BaseModel):
   status: Literal["generated!", "fail"]
   slug: str

def generate_article(req: GenerateRequest) -> GeneratedResponse:
    
    article_response: GeneratedResponse = requests.post(KENN_ZENN_URL + "/generate")

    return article_response
