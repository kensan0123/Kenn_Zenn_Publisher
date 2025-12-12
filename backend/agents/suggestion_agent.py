from anthropic import Anthropic
from anthropic.types import MessageParam, ToolUnionParam
from typing import Dict, Any
from backend.schemas.assistant_schemas import (
    WritingSession,
    Suggestions,
    SuggestionResponse,
)
from backend.core.settings import settings
from backend.exceptions.exceptions import AgentException


class SuggestAgent:
    def __init__(self):
        self._client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def generate_suggestion(
        self, writing_session: WritingSession, current_section_id: str, current_content: str
    ) -> SuggestionResponse:
        _system_prompt = self._system_prompt()
        _prompt = self._build_prompt(
            session=writing_session,
            current_session_id=current_section_id,
            current_content=current_content,
        )
        tools: list[ToolUnionParam] = self._build_tools()
        messages: list[MessageParam] = [{"role": "user", "content": _prompt}]

        while True:
            response = self._client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1000,
                system=_system_prompt,
                tools=tools,
                messages=messages,
            )

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_id = block.id

                        result = self._execute_tool(tool_name, tool_input)

                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": result,
                            }
                        )
                messages.append({"role": "user", "content": tool_results})

            elif response.stop_reason == "end_turn":
                final_text = ""
                for block in response.content:
                    if block.type == "text":
                        final_text += block.text

                suggestions: Suggestions = Suggestions.model_validate_json(final_text)

                suggestion_respons: SuggestionResponse = SuggestionResponse(
                    suggestions=suggestions,
                    related_links=[],
                    summary_report="",
                )
                return suggestion_respons

            else:
                raise AgentException(
                    message="Agent call error",
                    endpoint="/assist",
                )

    def _system_prompt(self):
        _system_prompt: str = """
        ## 役割

        あなたは優秀な記事編集者兼記事編集アシスタントです。
        あなたはユーザーが書く記事を記事執筆の途中段階で評価し、最適なアドバイスをユーザーに提供します。

        ## 入力情報

        - topic : 記事のテーマ・トピック
        - target_audience : ターゲットとする視聴者
        - outline : 記事の目次
        - content : 記事全文
        - current_section_id : 現在執筆中の目次項目
        - current_content : 現在執筆中の目次項目の内容

        ## 出力要件

        - JSONフォーマット
        - JSONのみ

        ## 出力JSONスキーマ

        ```input_schema
        {
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
        }

        ```

        ## 出力例

        ```schema.json
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
                追加情報として、Zenn CLI は GitHub 連携を行ることをこの章の記事内容に含むことを
                推奨します。参考になりそうな記事を載せます。",
                "priority": 1,
            }
        ]
        ```
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
            # ----------hook the tool

            return f"Search result for: {tool_input['query']}"
        return "Unknown tool"

    def _build_tools(self) -> list[ToolUnionParam]:
        """tools buildeing for anthropic agent"""

        tools: list[ToolUnionParam] = [
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
            }  # type: ignore
        ]
        return tools
