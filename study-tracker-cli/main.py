#!/usr/bin/env python3
"""
Study Tracker CLI - A powerful terminal-based productivity tracker
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from commands import study, habit, focus, stats
from database.db import init_db
from utils.config import ensure_config

app = typer.Typer(
    name="study",
    help="🧠 Track your study sessions, habits, and productivity",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()

# Add subcommands
app.add_typer(study.app, name="study", help="Manage study sessions")
app.add_typer(habit.app, name="habit", help="Track daily habits")
app.add_typer(focus.app, name="focus", help="Pomodoro focus timer")
app.add_typer(stats.app, name="stats", help="View analytics and insights")


@app.callback()
def callback():
    """
    Study Tracker CLI - Your personal productivity companion
    """
    ensure_config()
    init_db()


@app.command()
def welcome():
    """Display welcome screen"""
    console.clear()

    title = Text()
    title.append("╔══════════════════════════════════════╗\n", style="bold purple")
    title.append("║    🧠 ", style="bold purple")
    title.append("STUDY TRACKER", style="bold white on purple")
    title.append(" ║\n", style="bold purple")
    title.append("╚══════════════════════════════════════╝\n", style="bold purple")

    console.print(title, justify="center")

    commands_table = """
[b cyan]Quick Commands:[/]
  • [green]study add[/]          - Log a study session
  • [green]study list[/]         - View recent sessions
  • [green]habit mark[/]         - Mark habits complete
  • [green]habit list[/]         - View habit streaks
  • [green]focus start[/]        - Start Pomodoro timer
  • [green]stats today[/]        - Today's summary
  • [green]stats weekly[/]       - Weekly analytics
  • [green]stats insights[/]     - AI-powered insights

[b cyan]Examples:[/]
  study add --subject "Python" --duration 60 --tags "coding,deep-work"
  focus start --duration 25 --break 5
  habit mark --name "exercise"
    """

    console.print(Panel(
        commands_table,
        title="[bold green]Get Started[/]",
        border_style="purple",
        padding=(1, 2)
    ))

    console.print("\n[dim]Type 'study --help' for full documentation[/]\n")


if __name__ == "__main__":
    app()
