"""Thin wrapper around the OpenAI-compatible OpenRouter client."""

import os
from openai import OpenAI
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv

load_dotenv()


class OpenRouterClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ["OPENROUTER_API_KEY"]
        self.base_url = base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = model or os.getenv("MODEL", "anthropic/claude-sonnet-4-5")
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        **kwargs,
    ) -> ChatCompletion:
        params: dict = {"model": self.model, "messages": messages, **kwargs}
        if tools:
            params["tools"] = tools
        return self._client.chat.completions.create(**params)
