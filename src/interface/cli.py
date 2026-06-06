"""CLI interface — accepts a user prompt and optional --skill flag, runs the agent."""

import argparse
import logging

from rich.console import Console
from rich.markdown import Markdown

from src.agent.client import OpenRouterClient
from src.agent.loop import AgentLoop
from src.logger import configure
from src.skills.registry import SkillRegistry

console = Console()


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Maverx Style Buddy — AI-powered training builder")
    parser.add_argument("prompt", nargs="?", help="What to build (omit for interactive mode)")
    parser.add_argument(
        "--skill",
        choices=["combined", "presentation-builder", "training-builder"],
        default="combined",
        help="Which agent skill to run (default: combined — auto-detects from request)",
    )
    parser.add_argument("--model", help="Override the model (e.g. openai/gpt-4o)")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING"],
        help="Log verbosity",
    )
    args = parser.parse_args()

    configure(level=getattr(logging, args.log_level))

    client = OpenRouterClient(model=args.model)
    registry = SkillRegistry(skill=args.skill)
    loop = AgentLoop(client, registry)

    console.print(f"[dim]Skill:[/dim]  {args.skill}")
    console.print(f"[dim]Model:[/dim]  {client.model}")
    console.print(f"[dim]Tools:[/dim]  {', '.join(s['function']['name'] for s in registry.tool_specs())}\n")

    if args.prompt:
        _run(loop, args.prompt)
    else:
        console.print(
            f"[bold]Maverx Style Buddy[/bold] ({args.skill}) — "
            "type your request, or [dim]quit[/dim] to exit.\n"
        )
        while True:
            try:
                prompt = console.input("[bold cyan]>[/bold cyan] ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not prompt or prompt.lower() in ("quit", "exit"):
                break
            if prompt.lower() in ("reset", "new", "/reset", "/new"):
                loop.reset()
                console.print("[dim]Conversation reset.[/dim]\n")
                continue
            _run(loop, prompt)


def _run(loop: AgentLoop, prompt: str) -> None:
    console.print()
    with console.status("[dim]Thinking…[/dim]"):
        result = loop.run(prompt)
    console.print(Markdown(result))
    console.print()
