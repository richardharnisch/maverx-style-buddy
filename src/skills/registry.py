"""Auto-discovers all skill modules and exposes them as OpenAI tool definitions.

Each skill module must define:
  TOOL_SPEC: dict   — the OpenAI function/tool schema
  execute(**kwargs) — called when the model invokes the tool
"""

import importlib
import pkgutil
from types import ModuleType

import src.skills as _skills_pkg


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, ModuleType] = {}
        self._load()

    def _load(self) -> None:
        for _, name, _ in pkgutil.iter_modules(_skills_pkg.__path__):
            if name == "registry":
                continue
            module = importlib.import_module(f"src.skills.{name}")
            if hasattr(module, "TOOL_SPEC") and hasattr(module, "execute"):
                tool_name: str = module.TOOL_SPEC["function"]["name"]
                self._skills[tool_name] = module

    def tool_specs(self) -> list[dict]:
        return [m.TOOL_SPEC for m in self._skills.values()]

    def dispatch(self, name: str, args: dict) -> dict:
        if name not in self._skills:
            return {"error": f"Unknown skill: {name}"}
        try:
            result = self._skills[name].execute(**args)
            return result if isinstance(result, dict) else {}
        except Exception as e:
            return {"error": str(e)}
