from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()


def info(msg: str):
    console.print(f"[bold cyan]ℹ[/] {msg}")


def ok(msg: str):
    console.print(f"[bold green]✔[/] {msg}")


def warn(msg: str):
    console.print(f"[bold yellow]⚠[/] {msg}")


def err(msg: str):
    console.print(f"[bold red]✖[/] {msg}")


def header(title: str, subtitle: str = ""):
    console.print(
        Panel.fit(title if not subtitle else f"{title}\n[dim]{subtitle}[/]", style="bold", box=box.ROUNDED)
    )


def step(msg: str):
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[bold]{msg}[/]"),
        transient=True,
        console=console,
    )
