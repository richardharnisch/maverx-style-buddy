"""Agent reasoning loop: sends messages, handles tool calls, iterates until done."""

import json
import logging
from pathlib import Path

from src.agent.client import OpenRouterClient
from src.skills.registry import SkillRegistry

log = logging.getLogger(__name__)

MAX_ITERATIONS = 40

_SKILL_ROOT = Path(__file__).parents[2] / ".agents" / "skills"
_SKILL_DIRS = {
    "presentation-builder": "maverx-presentation-builder",
    "training-builder": "maverx-training-builder",
}
_COMBINED_HEADER = """\
You manage two workflows. Read the user's request and decide which one applies:

- **Training Builder** — the user wants to design a training, create a lesson plan, or define a \
didactic programme. Run the intake conversation, then generate and write lesson_plan.json.
- **Presentation Builder** — the user has a lesson_plan.json and wants PPTX decks and DOCX \
artifacts built from it.

The full workflow instructions for each are below.

"""


def _load_skill_md(dir_name: str) -> str:
    path = _SKILL_ROOT / dir_name / "SKILL.md"
    if not path.exists():
        log.warning("SKILL.md not found at %s", path)
        return ""
    return path.read_text(encoding="utf-8")


def _load_system_prompt(skill: str) -> str:
    if skill == "combined":
        training = _load_skill_md("maverx-training-builder")
        presentation = _load_skill_md("maverx-presentation-builder")
        return _COMBINED_HEADER + training + "\n\n---\n\n" + presentation
    dir_name = _SKILL_DIRS.get(skill, skill)
    prompt = _load_skill_md(dir_name)
    return prompt or "You are a helpful AI assistant."


class AgentLoop:
    def __init__(self, client: OpenRouterClient, registry: SkillRegistry) -> None:
        self.client = client
        self.registry = registry
        self._system_prompt = _load_system_prompt(registry.skill)
        self._messages: list[dict] = [{"role": "system", "content": self._system_prompt}]

    def run(self, user_prompt: str) -> str:
        tools = self.registry.tool_specs()
        self._messages.append({"role": "user", "content": user_prompt})
        log.info(
            "Agent loop started: skill=%s model=%s tools=%d history=%d messages",
            self.registry.skill, self.client.model, len(tools), len(self._messages),
        )

        messages = self._messages

        for iteration in range(MAX_ITERATIONS):
            log.debug("Iteration %d: sending %d messages", iteration + 1, len(messages))
            response = self.client.chat(messages, tools=tools or None)
            choice = response.choices[0]
            usage = response.usage
            log.debug(
                "Response: finish_reason=%s tokens(prompt=%s completion=%s)",
                choice.finish_reason,
                usage.prompt_tokens if usage else "?",
                usage.completion_tokens if usage else "?",
            )

            assistant_msg: dict = {"role": "assistant", "content": choice.message.content}
            if choice.message.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in choice.message.tool_calls
                ]
            messages.append(assistant_msg)

            if choice.finish_reason == "tool_calls":
                for tc in choice.message.tool_calls:
                    args = json.loads(tc.function.arguments)
                    log.info("Tool call: %s(%s)", tc.function.name, json.dumps(args))
                    result = self.registry.dispatch(tc.function.name, args)
                    log.debug("Tool result: %s", json.dumps(result))
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(result),
                        }
                    )
            else:
                log.info("Agent finished after %d iteration(s)", iteration + 1)
                return choice.message.content or ""

        log.warning("Max iterations (%d) reached without a final response", MAX_ITERATIONS)
        return "Max iterations reached without a final response."

    def reset(self) -> None:
        """Clear conversation history, keeping only the system prompt."""
        self._messages = [{"role": "system", "content": self._system_prompt}]
        log.debug("Conversation history cleared")
