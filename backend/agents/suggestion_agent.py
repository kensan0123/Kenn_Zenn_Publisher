from anthropic import Anthropic
from anthropic.types import MessageParam, ToolUnionParam
from typing import Dict, Any, List
from backend.schemas.assistant_schemas import (
    WritingSession,
    SuggestionAgentResponse,
    SuggestionResponse,
)
from backend.core.settings import settings
from backend.core.logger import get_logger
from backend.exceptions.exceptions import AgentException
from backend.agents.web_search_agent import WebSearchAgent, WebSearchResponse

logger = get_logger(__name__)


class SuggestAgent:
    def __init__(self):
        self._client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self._web_search_client: WebSearchAgent = WebSearchAgent()
        self._related_links: List = []

    def generate_suggestion(
        self, writing_session: WritingSession, current_section_id: str, current_content: str
    ) -> SuggestionResponse:
        system_prompt = self._system_prompt()
        prompt = self._build_prompt(
            session=writing_session,
            current_session_id=current_section_id,
            current_content=current_content,
        )
        tools: list[ToolUnionParam] = self._build_tools()
        messages: list[MessageParam] = [{"role": "user", "content": prompt}]

        while True:
            logger.info("Called suggest agent")
            response = self._client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=1000,
                system=system_prompt,
                tools=tools,
                messages=messages,
            )

            if response.stop_reason == "tool_use":
                logger.info("Suggest agent calls tool")
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                tool_count = 0
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_id = block.id

                        tool_count += 1
                        logger.info("Executing tool: count=%s", tool_count)
                        result = self._execute_tool(tool_name, tool_input)

                        logger.info("Appending tool result")
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": result,
                            }
                        )
                messages.append({"role": "user", "content": tool_results})
                logger.info("Return results to suggest agent")

            elif response.stop_reason == "end_turn":
                logger.info("Finish generating suggestion")
                final_text = ""
                for block in response.content:
                    if block.type == "text":
                        final_text = block.text

                _agent_response: SuggestionAgentResponse = (
                    SuggestionAgentResponse.model_validate_json(final_text)
                )

                logger.info("Conpleted suggestion")

                suggestion_respons: SuggestionResponse = SuggestionResponse(
                    suggestions=_agent_response.suggestions,
                    related_links=self._related_links,
                    summary_report=_agent_response.summary_report,
                )
                return suggestion_respons

            else:
                raise AgentException(
                    message="Unexpected stop reason agent stoped",
                    endpoint="/assist",
                )

    def _system_prompt(self):
        _system_prompt: str = """
        ## 役割
        あなたは優秀な記事編集者兼記事編集アシスタントです。
        あなたはユーザーが書く記事を記事執筆の途中段階で評価し、最適なアドバイスをユーザーに提供します。

        # ツール
        記事アドバイスを生成するときに、あなたが最新のデータや有用な引用を提示したい場合、WebSearchツールを使うことができます。
        ツールの呼び出し方法についてはtoolsに記載しているので決められたスキーマに従って呼びだしを行なってください。

        ## 入力情報

        - topic : 記事のテーマ・トピック
        - target_audience : ターゲットとする視聴者
        - outline : 記事の目次
        - content : 記事全文
        - current_section_id : 現在執筆中の目次項目
        - current_content : 現在執筆中の目次項目の内容

        ## 最終出力要件

        - JSONフォーマット
        - JSONのみ

        ## 最終出力JSONスキーマ

        ```input_schema
        {
            "type": "object",
            "properties": {
                "suggestions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "suggestion_id": {
                                "type": "string",
                                "description": "order of suggestion",
                            },
                            "type": {
                                "type": "Literal["structure", "content", "improvement"]",
                                "description": "type of suggest",
                            },
                            "title": {
                                "type": "string",
                                "description": "title of suggestion",
                            },
                            "description": {
                                "type": "string",
                                "description": "description of suggestion",
                            },
                            "priority": {
                                "type": "int",
                                "description": "priority of suggestion",
                            },
                        },
                        "required": ["suggestion_id", "type", "title", "description", "priority"]
                    },
                },
                "summary_report": {
                    "type": "str",
                    "description": "summary of all suggestion."
                }
            },
        }

        ```

        ## 最終出力例

        ```schema.json
        {
            "suggestions": {
                [
                    {
                        "suggestion_id": "1",
                        "type": "structure",
                        "title": "例を書くことを推奨",
                        "description": "「Zenn CLIの使い方」に関する例を明示することを推奨します。
                        例えば、---ポートを指定してプレビュー画面を表示する方法---\n
                            npx zenn preview --port 8000 のような例を書くことを推奨します。",
                        "priority": 2,
                    },
                    {
                        "suggestion_id": "2",
                        "type": "content",
                        "title": "参考になりそうな情報",
                        "description": "「Zenn CLIの使い方」に関す66る記事を書かれているようですが、
                        追加情報として、Zenn CLI は GitHub 連携を行ることをこの章の記事内容に
                        含むことを推奨します。
                        参考になりそうな記事のリンクを掲載します。",
                        "priority": 1,
                    },
                ]
            },
            "summary_report": {
                "記事序盤の第1章から第3章までの構成は初めてZenn CLIを触る人にとって、1から導入
                方法を述べられているため非常にわかりやすい構成となっています。一方で、応用編の第4章からについてはGitHubとの連携方法や
                実装途中に入力が必要なコマンドの例を載せることでより良い文章になると思われます。掲載するリンク先のブログサイトを確認する
                ことを推奨します。"
            }
        }
        ```

        # 注意
        - 最終出力とツール使用時の出力のスキーマが異なります。ツール使用時に誤って最終出力を出力しな
        いように注意してください。
        - また、最終出力の際には```schema.json ``` で囲まれたJSON本体のみ出力してください。
        - 注釈やコメントは一切入りません。
        """
        return _system_prompt

    def _build_prompt(
        self, session: WritingSession, current_session_id: str, current_content: str
    ) -> str:
        """prompt building"""

        prompt: str = f"""
        - topic: {session.topic}
        - target_audience: {session.target_audience}
        - outline: {session.outline}
        - content: {session.content}
        - current_session_id: {current_session_id}
        - current_content: {current_content}
        """
        return prompt

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute the tool and return result"""

        if tool_name == "web_search":
            _web_search_response: WebSearchResponse = self._web_search_client.search_web(
                query=tool_input["query"]
            )

            self._related_links = _web_search_response.related_links

            return f"Search result for: {tool_input['query']}- {_web_search_response.search_result}"
        return "Unknown tool"

    def _build_tools(self) -> List[ToolUnionParam]:
        """tools buildeing for anthropic agent"""

        tools: List[ToolUnionParam] = [
            {
                "name": "web_search",
                "description": "Search the web for information",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        }
                    },
                    "required": ["query"],
                },
            }
        ]
        return tools
