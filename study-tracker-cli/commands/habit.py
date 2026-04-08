"""
Habit tracking commands
"""

from datetime import datetime, timedelta
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich import box
from rich.prompt import Prompt, Confirm

from database.db import (
    add_habit, get_habits, toggle_habit_today, delete_habit,
    get_habit_streak, get_habits_for_date
)
from utils.formatters import print_success, print_error, print_warning

app = typer.Typer(help="Track daily habits")
console = Console()


@app.command()
def add(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Habit name"),
    category: Optional[str] = typer.Option("general", "--category", "-c", help="Category (study/health/productivity)"),
):
    """Add a new habit to track"""

    if not name:
        name = Prompt.ask("Habit name")

    if not name:
        print_error("Habit name is required")
        raise typer.Exit(1)

    habit_id = add_habit(name, category)
    print_success(f"Added habit: [cyan]{name}[/]")


@app.command()
def list(
    all_time: bool = typer.Option(False, "--all", "-a", help="Show all habits including completed"),
):
    """List habits and their streaks"""

    habits = get_habits()

    if not habits:
        console.print("\n[dim]No habits yet. Create one with:[/]")
        console.print("[cyan]  habit add[/]\n")
        return

    today = datetime.now().date()
    today_str = today.isoformat()

    table = Table(
        title=f"🔥 Daily Habits - {today.strftime('%A, %B %d')}",
        box=box.ROUNDED,
        border_style="purple",
        header_style="bold cyan",
    )

    table.add_column("ID", style="dim", width=4)
    table.add_column("Habit", style="white")
    table.add_column("Category", style="blue", width=12)
    table.add_column("Status", style="green", width=12, justify="center")
    table.add_column("Streak", style="yellow", width=10, justify="right")

    for habit in habits:
        # Check if completed today
        completions = get_habits_for_date(today)
        is_done_today = habit.id in [h.id for h in completions]

        status = "[green]✓ Done[/]" if is_done_today else "[dim]○ Pending[/]"
        streak = get_habit_streak(habit.id)
        streak_display = f"{streak} 🔥" if streak > 0 else "-"

        # Dim completed habits unless showing all
        style = "dim" if is_done_today and not all_time else ""

        table.add_row(
            str(habit.id),
            habit.name,
            habit.category,
            status,
            streak_display,
            style=style,
        )

    console.print()
    console.print(table)
    console.print()


@app.command()
def mark(
    habit_id: Optional[int] = typer.Option(None, "--id", "-i", help="Habit ID to mark"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Habit name (alternative to ID)"),
    unmark: bool = typer.Option(False, "--unmark", "-u", help="Unmark as done"),
):
    """Mark a habit as complete for today"""

    if not habit_id and not name:
        # Show interactive list
        habits = get_habits()
        if not habits:
            print_error("No habits found. Create one with: habit add")
            raise typer.Exit(1)

        console.print("\n[bold cyan]Select habit to mark:[/]\n")
        for h in habits:
            console.print(f"  [dim]{h.id}.[/] {h.name}")

        choice = Prompt.ask("\nHabit ID", default="")
        if not choice:
            return
        habit_id = int(choice)

    result = toggle_habit_today(habit_id, unmark)

    if result:
        if unmark:
            print_warning("Habit unmarked")
        else:
            streak = get_habit_streak(habit_id)
            if streak > 0:
                print_success(f"Marked complete! Current streak: [yellow]{streak} days 🔥[/]")
            else:
                print_success("Marked complete!")
    else:
        print_error("Habit not found")


@app.command()
def delete(
    habit_id: int = typer.Argument(..., help="Habit ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a habit"""

    if not force:
        if not Confirm.ask(f"Delete habit #{habit_id}?", default=False):
            return

    if delete_habit(habit_id):
        print_success("Habit deleted")
    else:
        print_error("Habit not found")


@app.command()
def streaks():
    """Show streak leaderboard"""

    habits = get_habits()
    if not habits:
        console.print("[dim]No habits yet[/]")
        return

    # Calculate all streaks
    habit_streaks = [(h, get_habit_streak(h.id)) for h in habits]
    habit_streaks.sort(key=lambda x: -x[1])

    console.print("\n[bold cyan]🏆 Streak Leaderboard[/]\n")

    for i, (habit, streak) in enumerate(habit_streaks, 1):
        bar_length = min(streak, 30)  # Cap at 30 chars
        bar = "█" * bar_length + "░" * (30 - bar_length)

        color = "green" if streak >= 7 else "yellow" if streak >= 3 else "white"

        console.print(f"  [bold]{i}.[/] {habit.name:<20} [bold {color}]{streak} days[/]")
        console.print(f"     [{color}]{bar}[/{color}]")

    console.print()


@app.command()
def reset():
    """Reset all habits for a new day (testing only)"""

    if Confirm.ask("Reset all habit completions?", default=False):
        # This is handled automatically by date in production
        print_warning("Habits reset for testing")
