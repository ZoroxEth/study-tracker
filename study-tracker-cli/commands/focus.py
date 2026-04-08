"""
Pomodoro focus timer commands
"""

import time
import threading
import signal
import sys
from datetime import datetime
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.align import Align

from utils.timer import Timer
from utils.config import get_config
from utils.formatters import print_success, print_error, subject_emoji

app = typer.Typer(help="Pomodoro focus timer")
console = Console()

# Global timer for signal handling
current_timer = None


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    if current_timer:
        console.print("\n\n[yellow]Timer cancelled[/]")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


@app.command()
def start(
    duration: int = typer.Option(25, "--duration", "-d", help="Focus duration (minutes)"),
    break_duration: int = typer.Option(5, "--break", "-b", help="Break duration (minutes)"),
    subject: Optional[str] = typer.Option(None, "--subject", "-s", help="What you're working on"),
    auto_start_break: bool = typer.Option(False, "--auto-break", help="Auto-start break after focus"),
):
    """Start a Pomodoro focus session"""

    global current_timer

    if not subject:
        subject = typer.prompt("What are you working on?", default="Deep work")

    focus_seconds = duration * 60
    break_seconds = break_duration * 60

    # Focus Session
    console.clear()
    console.print(f"\n[bold purple]{'═' * 50}[/]\n")
    console.print(Align.center(f"[bold cyan]🎯 FOCUS MODE[/]"))
    console.print(Align.center(f"[dim]{subject}[/]"))
    console.print(f"\n[bold purple]{'═' * 50}[/]\n")

    timer = Timer(focus_seconds)
    current_timer = timer

    try:
        with Live(get_timer_display(timer, duration, "FOCUS"), refresh_per_second=4) as live:
            while not timer.is_finished():
                if timer.is_paused:
                    time.sleep(0.1)
                    continue
                timer.tick()
                live.update(get_timer_display(timer, duration, "FOCUS"))
                time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Focus session cancelled[/]")
        return

    current_timer = None

    # Success!
    console.clear()
    console.print(f"\n[bold green]{'═' * 50}[/]\n")
    console.print(Align.center("[bold green]✓ FOCUS COMPLETE![/]"))
    console.print(Align.center(f"[dim]You focused for {duration} minutes[/]"))
    console.print(f"\n[bold green]{'═' * 50}[/]\n")

    # Log the session
    from database.db import add_session
    from commands.study import add as add_study

    add_session(subject, duration, datetime.now(), focus=5, tags=["pomodoro"], notes=None)
    print_success("Session logged automatically")

    # Break time
    if not auto_start_break:
        if not typer.confirm("\nStart break?", default=True):
            return

    console.print(f"\n[bold blue]{'═' * 50}[/]\n")
    console.print(Align.center("[bold blue]☕ BREAK TIME[/]"))
    console.print(Align.center(f"[dim]Relax for {break_duration} minutes[/]"))
    console.print(f"\n[bold blue]{'═' * 50}[/]\n")

    timer = Timer(break_seconds)
    current_timer = timer

    try:
        with Live(get_timer_display(timer, break_duration, "BREAK"), refresh_per_second=4) as live:
            while not timer.is_finished():
                timer.tick()
                live.update(get_timer_display(timer, break_duration, "BREAK"))
                time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Break ended early[/]")
        return

    console.print(f"\n[bold green]{'═' * 50}[/]")
    console.print(Align.center("[bold green]Break complete! Ready to focus again?[/]"))
    console.print(f"[bold green]{'═' * 50}[/]\n")


def get_timer_display(timer: Timer, total_minutes: int, mode: str) -> Panel:
    """Generate timer display"""

    remaining = timer.remaining_seconds()
    minutes, seconds = divmod(remaining, 60)

    progress = 1 - (remaining / (total_minutes * 60))
    bar_width = 40
    filled = int(bar_width * progress)
    bar = "█" * filled + "░" * (bar_width - filled)

    if mode == "FOCUS":
        color = "green"
        icon = "🎯"
    else:
        color = "blue"
        icon = "☕"

    time_str = f"{minutes:02d}:{seconds:02d}"

    content = f"""
[bold {color}]{icon} {mode}[/]

[bold white]{time_str}[/]

[{color}]{bar}[/{color}]  {int(progress * 100)}%

[dim]Press Ctrl+C to cancel[/]
    """

    return Panel(
        content,
        border_style=color,
        width=60,
        title=f"[bold]{mode} TIMER[/]",
    )


@app.command()
def quick(
    minutes: int = typer.Argument(25, help="Quick focus duration"),
):
    """Start a quick focus session (simplified)"""

    start(duration=minutes, subject="Quick focus")


@app.command()
def status():
    """Check if a timer is running"""

    if current_timer:
        console.print("[yellow]Timer is running...[/]")
    else:
        console.print("[dim]No active timer[/]")
