from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from modes.live_mode import run_live_mode
from modes.manual_mode import run_manual_mode


console = Console()


def main() -> None:
    load_dotenv()
    Path("output").mkdir(exist_ok=True)
    Path("knowledge_base").mkdir(exist_ok=True)

    while True:
        console.print(_menu())
        choice = console.input("[bold]Choose an option:[/bold] ").strip()
        if choice == "1":
            run_manual_mode()
        elif choice == "2":
            run_live_mode()
        elif choice == "3":
            console.print("[dim]Goodbye.[/dim]")
            return
        else:
            console.print("[red]Invalid option. Choose 1, 2, or 3.[/red]")


def _menu() -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left")
    table.add_row("[bold]DISCOVERY AGENT v1.0[/bold]")
    table.add_row("[1] Manual - colar texto/arquivo")
    table.add_row("[2] Live   - capturar call agora")
    table.add_row("[3] Sair")
    return Panel(table, border_style="white", expand=False)


if __name__ == "__main__":
    main()
