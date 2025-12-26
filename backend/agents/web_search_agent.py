from anthropic import Anthropic
from anthropic.types import ToolUnionParam, MessageParam
from anthropic.types.web_search_tool_result_block import WebSearchToolResultBlock
from backend.core.settings import settings
from typing import List
from backend.schemas.assistant_schemas import WebSearchResponse, RelatedLink
from backend.exceptions.exceptions import AgentException
from backend.core.logger import get_logger

logger = get_logger(__name__)


class WebSearchAgent:
    def __init__(self):
        self._client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def search_web(self, query: str) -> WebSearchResponse:
        """web search agent"""

        system_prompt = self._system_prompt()
        tools: List[ToolUnionParam] = [
            {"type": "web_search_20250305", "name": "web_search", "max_uses": 5}
        ]
        prompt = f"search query from parent agent: {query}"
        messages: List[MessageParam] = [{"role": "user", "content": prompt}]

        logger.info("Called web search agent")
        response = self._client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=1000,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )

        search_report: str = ""

        logger.info("Finished web searching")

        if response.stop_reason == "end_turn":
            related_links: List[RelatedLink] = []
            for block in response.content:
                if block.type == "web_search_tool_result":
                    if isinstance(block, WebSearchToolResultBlock):
                        if isinstance(block.content, list):
                            for b in block.content:
                                if b.type == "web_search_result":
                                    related_links.append(
                                        RelatedLink(
                                            title=b.title,
                                            url=b.url,
                                        )
                                    )

                elif block.type == "text":
                    logger.info("Appending report")
                    logger.info(block.text)
                    search_report += block.text

            if search_report == "":
                raise AgentException(
                    message="Web search agent error: response text not found",
                    endpoint="/assist",
                )
            logger.info(related_links)
            logger.info(search_report)
            search_response: WebSearchResponse = WebSearchResponse(
                search_result=search_report, related_links=related_links
            )
            logger.info("Properly finished web search")

            return search_response

        else:
            raise AgentException(
                message="Web search agent error: end_turn not found,"
                f" this is the reason {response.stop_reason}",
                endpoint="/assist",
            )

    def _system_prompt(self):
        _system_prompt = """
        ## 役割
        あなたはWeb検索、レポートエージェントです。親エージェントから検索指示が与えられるので、Web検索ツールを使って
        親エージェントが求める情報を検索し、親エージェントに端的に検索結果を報告します。

        ## ツール
        - Web search

        ## 出力要件
        - JSONのみで出力
        - 下記で指定したJSONスキーマを厳守すること。

        ## 出力スキーマ
        
        ```output_schema.json
        {
            "type": "object",
            "property": {
                "report": {
                    "type": "string(markdown)",
                    "description": "summary of this search",
                },
            },
        }
        ```

        ##出力例

        ```output_example.json
        {
            "report": "## Zenn CLI応用（CI/CD）レポート
            
            ### **1. GitHub連携による自動公開**
            GitHubリポジトリと連携することで、`main`ブランチへのpushで記事が自動的にZennに公開され
            ます。コミットメッセージに`[ci skip]`または`[skip ci]`を含めるとデプロイをスキップで
            きます。

            ### **2. GitHub Actionsとの統合**

            **品質チェック自動化:**
            - textlint/markdownlintでMarkdownの自動校正
            - 日本語表記ゆれの検出
            - PRトリガーでのLint実行

            **予約投稿機能:**
            - Front Matterの`published_at`で公開日時を指定
            - GitHub Actionsのcron設定で定期チェック
            - 指定時刻に自動で`published: true`に更新

            **自動レビューシステム:**
            - LLM（Gemini/Claude）による機密情報チェック
            - レビュワーの自動アサイン
            - Teams/Slackへの通知連携

            ### **3. ブランチ戦略**
            - ブランチ名プレフィックス（`draft/`, `review/`, `publish/`）で処理を自動分岐
            - Publication Proの特性に最適化された段階的公開フロー

            ### **4. その他の応用**
            - pre-commitフック（husky/lefthook）でローカルでのLint実行
            - 画像最適化スクリプトの自動実行
            - Git履歴管理によるバージョン管理とバックアップ

            CI/CDを活用することで、記事品質の担保、チーム執筆の効率化、安全な公開フローを実現できます。"
        }
        ```

        # 注意
        - 出力例はweb_searchの結果報告レポートの例を示しているが、より文章を短くしても親エージェント
        に伝わると考えた場合は文章を削減して、レポートにすること。
        """

        return _system_prompt
