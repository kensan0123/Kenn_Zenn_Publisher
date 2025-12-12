import json
from fastapi import APIRouter
from openai import OpenAI

from core.settings import settings
from backend.zenn.zenn_article_schemas import (
    AIGenerateRequest,
    AIPrompt,
    GeneratedResponse,
    GenerateRequest,
)
from backend.zenn.generate_service import GenerateService

openai_aip_key: str = settings.OPENAI_API_KEY
generator: GenerateService = GenerateService()

router = APIRouter(prefix="/generate", tags=["Generate"])


@router.post("/")
def generate(req: GenerateRequest) -> GeneratedResponse:
    """
    手書きで記事を作成する場合に使用する関数
    """
    generate_request: GenerateRequest = req
    article_response: GeneratedResponse = generator.generate_article(article_info=generate_request)

    return article_response


@router.post("/openai")
def generate_openai(req: AIGenerateRequest) -> GeneratedResponse:
    """
    Docstring for generate_openai

    :param req: Description
    :type req: AIGenerateRequest
    """

    client = OpenAI(api_key=openai_aip_key)

    ai_prompt: AIPrompt = AIPrompt(prompt=req.prompt)
    _prompt = _build_prompt(req=ai_prompt)

    response = client.responses.create(model="gpt-5-nano", input=_prompt)

    response_content = response.output_text
    parsed_json = json.loads(response_content)

    article_title = parsed_json.get("title", "")
    article_emoji = parsed_json.get("emoji", "")
    article_type = parsed_json.get("type", "")
    article_content = parsed_json.get("content", "")

    generate_request: GenerateRequest = GenerateRequest(
        title=article_title,
        emoji=article_emoji,
        type=article_type,
        content=article_content,
    )

    article_response: GeneratedResponse = generator.generate_article(article_info=generate_request)

    return article_response


def _build_prompt(req: AIPrompt) -> str:
    _prompt = f"""
    You are a professional technical writer for Zenn.

    Write a high-quality technical article in Japanese based on the title below,
    and output ONLY a JSON object with the required fields.

    # Input Title
    {req.prompt}

    # Requirements for the article
    - Write in Markdown format
    - Structure: 導入 → 背景 → 手順 → まとめ
    - Use appropriate Markdown headers (##, ###)
    - Include code examples when appropriate (use ```言語名 syntax)
    - Use です・ます調 formal style
    - Article content must be long and detailed

    # Output format requirements
    - Output MUST be ONLY a valid JSON object
    - NO explanation, NO surrounding text, NO backticks, NO markdown fences
    - All values must be strings
    - Key order must be exactly as below

    # JSON Format Example
    {{
    "title": "hogehoge",
    "emoji": "hoge",
    "type": "article type ["Tech" or "Idea"],
    "content": "this is the content of article"
    }}

    # 📝 Hint — If You’re Struggling to Choose a Title

    ## How to Create Effective Blog Titles

    This guide explains **why blog titles are important** and 
    the **key methods for choosing strong titles**.

    ---

    ### 🎯 What a Good Title Should Achieve
    - Clearly communicates what the article is about
    - Stands out and competes with other articles

    ---

    ### 🪄 Tips for Writing Effective Blog Titles
    1. Match the title with the article’s content
    2. Use proven title formats or templates
    3. Keep it around **30 full-width characters** (≈ **15–18 English words**)
    4. Include important target keywords

    > These four points help you create titles that attract more 
    readers and improve article performance.

    ---

    ## 🤔 Unsure How to Choose the Article Type? (Tech or Idea)

    | Type | Choose this when… |
    |-------|----------------|
    | **Tech** | The article covers software, hardware, hands-on testing, implementation results,
    or technical insights from real experience |
    | **Idea** | The article covers careers, management, abstract thinking about technology,
    or information summaries not directly tied to technical implementation |

    ---

    Use these hints to choose the most suitable **title** and **type**, 
    and create content that reaches the right audience.

    # Output ONLY a valid JSON object.
    Do not include explanations, markdown, or code fences.

    # Finally Write this "この記事はAIによって作成されました。"

    """

    return _prompt
