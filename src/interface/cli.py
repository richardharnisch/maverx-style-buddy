"""CLI interface — accepts a user prompt and optional --style flag, runs the agent."""

import argparse

from rich.console import Console
from rich.markdown import Markdown

from src.agent.client import OpenRouterClient
from src.agent.loop import AgentLoop
from src.skills.registry import SkillRegistry

console = Console()


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Style Buddy — AI-powered PowerPoint generator")
    parser.add_argument("prompt", nargs="?", help="What to build (omit for interactive mode)")
    parser.add_argument("--model", help="Override the model (e.g. openai/gpt-4o)")
    args = parser.parse_args()

    client = OpenRouterClient(model=args.model)
    registry = SkillRegistry()
    loop = AgentLoop(client, registry)

    console.print(f"[dim]Model:[/dim] {client.model}")
    console.print(f"[dim]Skills:[/dim] {', '.join(s['function']['name'] for s in registry.tool_specs())}\n")

    if args.prompt:
        _run(loop, args.prompt)
    else:
        console.print("[bold]Style Buddy[/bold] — type your request, or [dim]quit[/dim] to exit.\n")
        while True:
            try:
                prompt = console.input("[bold cyan]>[/bold cyan] ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not prompt or prompt.lower() in ("quit", "exit"):
                break
            _run(loop, prompt)


def _run(loop: AgentLoop, prompt: str) -> None:
    console.print()
    with console.status("[dim]Thinking…[/dim]"):
        result = loop.run(prompt)
    console.print(Markdown(result))
    console.print()
