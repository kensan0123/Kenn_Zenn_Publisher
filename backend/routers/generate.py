from fastapi import APIRouter
from pydantic import BaseModel
import requests
import os
from typing import Literal

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

class GenerateRequest(BaseModel):
    title: str
    emoji: str
    content: str

class AIGenerateRequest(BaseModel):
    prompt: str

class ZennResult(BaseModel):
    status: Literal["success", "fail"]
    slug: str

router = APIRouter(
    prefix="/generate",
    tags=["Generate"]
)

@router.get("/")
def generate(req: GenerateRequest) -> ZennResult:
    """
    手書きで記事を作成する場合に使用する関数
    """
    

@router.get("/ai")
def generate_ai(req: AIGenerateRequest) -> ZennResult:
    """
    Docstring for generate_ai
    
    :param req: Description
    :type req: AIGenerateRequest
    """
    _prompt = f"""
    あなたはZennのテックライターです。
    次のタイトルでZenn用の技術記事を書いてください。

    # 条件
    - タイトル: {req.prompt}
    - Markdown形式
    - 導入 → 背景 → 手順 → まとめ の構成
    - 見出し（##, ###）を適切に使う
    - コード例があれば ```言語名 で囲む
    - です・ます調

    # 出力要件
    jsonのみを出力すること
    ```json
    {
        "title": "hogehoge",
        "emoji": "hoge",
        "content": "this is the content of article",
    }
    ```

    では記事を書いてください。
    """

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": "llama3", "prompt": _prompt, "stream": False},
    )

    response_json = response.json()
    article_title: str = response_json.get("title", "")
    article_emoji: str = response_json.get("emoji", "")
    article_content: str = response_json.get("content", "")

    

    result: ZennResult = ZennResult(
        status="success",
        slug=article_slug,
    )

    return result

    