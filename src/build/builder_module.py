"""Load the bundled build script as an importable module.

The deterministic builder lives under ``.agents/skills/...`` as a standalone
script. We import it (rather than only shelling out) so the lesson-plan stage
can reuse its exact template-selection logic to size decks that the builder is
guaranteed to be able to render.
"""

from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from types import ModuleType

from src.constants import BUILD_SCRIPT_PATH


@lru_cache(maxsize=1)
def load_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "maverx_build_script", BUILD_SCRIPT_PATH
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load build script at {BUILD_SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    # Register before exec so dataclasses can resolve the module's namespace.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
