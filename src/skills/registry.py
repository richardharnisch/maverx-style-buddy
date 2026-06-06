"""Auto-discovers all skill modules and exposes them as OpenAI tool definitions.

Each skill module must define:
  TOOL_SPEC: dict   — the OpenAI function/tool schema
  execute(**kwargs) — called when the model invokes the tool
"""
