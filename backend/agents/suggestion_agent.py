from anthropic import Anthropic
from anthropic.types import MessageParam, ToolUnionParam
from typing import Dict, Any
from backend.schemas.assistant_schemas import (
    WritingSession,
    Suggestions,
    SuggestionResponse,
)
from backend.core.settings import settings


class SuggestAgent:
    def __init__(self):
        self._client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def generate_suggestion(
        self, writing_session: WritingSession, current_section_id: str, current_content: str
    ) -> SuggestionResponse:
        prompt = self._build_prompt(
            session=writing_session,
            current_session_id=current_section_id,
            current_content=current_content,
        )
        tools: list[ToolUnionParam] = self._build_tools()
        messages: list[MessageParam] = [{"role": "user", "content": prompt}]

        while True:
            response = self._client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1000,
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

            else:
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

    def _build_prompt(
        self, session: WritingSession, current_session_id: str, current_content: str
    ) -> str:
        """prompt building"""

        prompt: str = f"""
            {session}{current_session_id}{current_content}
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
                "discription": "Search the web for information",
                "input_schema": {
                    "type": "object",
                    "propaties": {
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
