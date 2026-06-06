"""Agent reasoning loop: sends messages, handles tool calls, iterates until done."""

import json
import logging
from pathlib import Path

from src.agent.client import OpenRouterClient
from src.skills.registry import SkillRegistry

log = logging.getLogger(__name__)

MAX_ITERATIONS = 40

SYSTEM_PROMPT = (
    "You are an AI assistant that creates PowerPoint presentations based on branded style guides.\n\n"
    "Follow this order for every presentation:\n"
    "1. Call create_presentation with the correct style guide name.\n"
    "2. Call list_layouts to discover all available layout keys and their descriptions. Read them carefully.\n"
    "3. Optionally call list_images if the presentation would benefit from photos or icons.\n"
    "4. Call add_slide for each slide.\n"
    "5. Call render_slides to get PNG images of every slide. Review each carefully for:\n"
    "   - Text cut off or overflowing outside the slide boundary\n"
    "   - Text areas that are empty but should have content\n"
    "   - Layout choices that don't match the content (e.g. two-column layout with only one column filled)\n"
    "   - Slides that look visually weak or sparse compared to others in the deck\n"
    "6. For any slide that needs improvement, call update_slide with corrected content.\n"
    "   You may change the layout key if a different layout suits the content better.\n"
    "7. After making updates, call render_slides again to verify the changes look correct.\n"
    "8. Repeat steps 6–7 until satisfied. Aim for 1–2 rounds; stop after 3 at most.\n"
    "9. Call export_pptx to finalise and save the presentation.\n\n"
    "Layout selection rules — follow these strictly:\n"
    "- VARY your layout choices across slides. A deck with 6 slides should use at least 3-4 different layouts.\n"
    "- Match the layout's visual style to the slide's purpose:\n"
    "  • Opening slide / section divider → use a cover or photo-background layout\n"
    "  • Comparison or two-point content → use a two-column layout\n"
    "  • Informational content → use a standard title+body layout\n"
    "  • High-impact statement → use a title-only or decorative layout\n"
    "  • Data-heavy or multi-point → use a layout with multiple body areas\n"
    "- Read each layout description; pay attention to whether it has a dark/light background, "
    "photo area, or special structure.\n"
    "- Never use the same layout for every slide unless the content genuinely demands it.\n\n"
    "Never skip list_layouts — layout keys vary per style guide and must be discovered at runtime."
)

_SKILL_MD = Path(__file__).parents[1] / "style_guides" / "PRESENTATION_CREATION_GUIDE.md"


def _load_skill_guide() -> str:
    if _SKILL_MD.exists():
        return "\n\n---\n\n" + _SKILL_MD.read_text()
    log.warning("PRESENTATION_CREATION_GUIDE.md not found at %s — proceeding without it", _SKILL_MD)
    return ""


class AgentLoop:
    def __init__(self, client: OpenRouterClient, registry: SkillRegistry) -> None:
        self.client = client
        self.registry = registry
        self._messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT + _load_skill_guide()}]

    def run(self, user_prompt: str) -> str:
        tools = self.registry.tool_specs()
        self._messages.append({"role": "user", "content": user_prompt})
        log.info(
            "Agent loop started: model=%s tools=%d history=%d messages",
            self.client.model, len(tools), len(self._messages),
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

                    # render_slides returns base64 images — build a multimodal tool message
                    if tc.function.name == "render_slides" and "slides" in result:
                        log.debug("render_slides: %d slide image(s) received", result.get("count", 0))
                        content: list[dict] = [
                            {"type": "text", "text": f"Rendered {result['count']} slide(s). Review each carefully:"}
                        ]
                        for s in result["slides"]:
                            content.append({"type": "text", "text": f"Slide {s['index'] + 1}:"})
                            content.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{s['image_b64']}"},
                            })
                        messages.append({"role": "tool", "tool_call_id": tc.id, "content": content})
                    else:
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
        self._messages = [{"role": "system", "content": SYSTEM_PROMPT + _load_skill_guide()}]
        log.debug("Conversation history cleared")
