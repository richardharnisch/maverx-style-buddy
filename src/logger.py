"""Logging setup — call configure() once at startup."""

import logging
from rich.logging import RichHandler


def configure(level: int = logging.DEBUG) -> None:
    logging.basicConfig(
        level=level,
        format="%(name)s  %(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True, show_path=False)],
    )
