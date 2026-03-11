"""
YS Lead Scraper — Launcher
Corre con: uv run python run.py
"""
import subprocess
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


def main() -> None:
    console.print()
    console.print(Panel.fit(
        "[bold cyan]YS Business Services[/bold cyan]\n"
        "[dim]Google Places Lead Scraper[/dim]",
        border_style="cyan",
    ))
    console.print()
    console.print("  [bold cyan]1[/bold cyan]  Web UI   [dim](Streamlit — abre en el browser)[/dim]")
    console.print("  [bold cyan]2[/bold cyan]  Terminal [dim](Textual  — corre aqui mismo)[/dim]")
    console.print("  [bold cyan]3[/bold cyan]  CLI      [dim](original — inputs manuales)[/dim]")
    console.print()

    choice = Prompt.ask(
        "[bold]Elige una opcion[/bold]",
        choices=["1", "2", "3"],
        default="1",
    )

    if choice == "1":
        console.print("\n[green]Iniciando Streamlit...[/green]")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

    elif choice == "2":
        console.print("\n[green]Iniciando TUI...[/green]")
        from tui import YSLeadScraper
        YSLeadScraper().run()

    elif choice == "3":
        console.print("\n[green]Iniciando CLI...[/green]")
        from main import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
