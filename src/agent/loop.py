"""Agent reasoning loop: sends messages, handles tool calls, iterates until done."""

import json

from src.agent.client import OpenRouterClient
from src.skills.registry import SkillRegistry

MAX_ITERATIONS = 20

SYSTEM_PROMPT = (
    "You are an AI assistant that creates PowerPoint presentations based on style guides. "
    "Use the available tools to build presentations step by step. "
    "Always create a presentation before adding slides, and export when done."
)


class AgentLoop:
    def __init__(self, client: OpenRouterClient, registry: SkillRegistry) -> None:
        self.client = client
        self.registry = registry

    def run(self, user_prompt: str) -> str:
        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        tools = self.registry.tool_specs()

        for _ in range(MAX_ITERATIONS):
            response = self.client.chat(messages, tools=tools or None)
            choice = response.choices[0]

            # Build assistant message manually — avoids .model_dump() quirks across SDK versions
            assistant_msg: dict = {"role": "assistant", "content": choice.message.content}
            if choice.message.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in choice.message.tool_calls
                ]
            messages.append(assistant_msg)

            if choice.finish_reason == "tool_calls":
                for tc in choice.message.tool_calls:
                    args = json.loads(tc.function.arguments)
                    result = self.registry.dispatch(tc.function.name, args)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(result),
                        }
                    )
            else:
                return choice.message.content or ""

        return "Max iterations reached without a final response."
