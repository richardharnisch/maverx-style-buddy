#!/usr/bin/env python3
"""Thin OpenRouter client used by every planner / writer script.

- Reads OPENROUTER_API_KEY from env (or --api-key flag).
- Supports JSON-mode responses (response_format=json_object).
- Retries on 429 / 5xx with exponential backoff.
- Streams writes nothing back; callers consume the returned dict.
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Any

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_PLANNER_MODEL = os.environ.get(
    "MAVERX_PLANNER_MODEL", "anthropic/claude-sonnet-4.5"
)
DEFAULT_WRITER_MODEL = os.environ.get(
    "MAVERX_WRITER_MODEL", "openai/gpt-4.1-mini"
)


def call_openrouter(
    *,
    system: str,
    user: str,
    model: str | None = None,
    json_mode: bool = True,
    max_tokens: int = 4096,
    temperature: float = 0.3,
    api_key: str | None = None,
    max_retries: int = 4,
) -> dict[str, Any] | str:
    """Call OpenRouter chat completions. Returns parsed JSON if json_mode, else raw text."""
    key = api_key or os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    model = model or DEFAULT_WRITER_MODEL
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://maverx-training-builder.local",
        "X-Title": "Maverx Training Builder",
    }
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    delay = 2.0
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=180)
            if r.status_code == 429 or r.status_code >= 500:
                raise requests.HTTPError(f"{r.status_code}: {r.text[:300]}")
            r.raise_for_status()
            data = r.json()
            content = data["choices"][0]["message"]["content"]
            if json_mode:
                # strip possible markdown fences
                txt = content.strip()
                if txt.startswith("```"):
                    txt = txt.strip("`")
                    if txt.lower().startswith("json"):
                        txt = txt[4:].strip()
                return json.loads(txt)
            return content
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"[openrouter] attempt {attempt + 1} failed: {e}", file=sys.stderr)
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"OpenRouter failed after {max_retries} retries: {last_err}")


if __name__ == "__main__":
    # Quick smoke test: python openrouter_call.py "hello"
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Reply with {\"ok\": true}"
    out = call_openrouter(system="You output strict JSON.", user=prompt)
    print(json.dumps(out, indent=2))
