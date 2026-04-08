"""
Study session management commands
"""

from datetime import datetime, timedelta
from typing import Optional, List
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box

from database.db import (
    add_session, get_sessions, update_session, delete_session,
    get_session_by_id, get_sessions_by_date_range
)
from utils.formatters import (
    format_duration, get_motivational_message,
    subject_emoji, print_success, print_error, print_warning
)

app = typer.Typer(help="Manage study sessions")
console = Console()


@app.command()
def add(
    subject: Optional[str] = typer.Option(None, "--subject", "-s", help="Subject/topic studied"),
    duration: Optional[int] = typer.Option(None, "--duration", "-d", help="Duration in minutes"),
    date: Optional[str] = typer.Option(None, "--date", help="Date (YYYY-MM-DD, default: today)"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Comma-separated tags"),
    focus: Optional[int] = typer.Option(3, "--focus", "-f", help="Focus level 1-5", min=1, max=5),
    notes: Optional[str] = typer.Option(None, "--notes", "-n", help="Additional notes"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
):
    """Add a new study session"""

    if interactive or not subject:
        console.print("\n[bold cyan]📝 New Study Session[/]\n")
        subject = Prompt.ask("Subject", default=subject or "")
        duration = int(Prompt.ask("Duration (minutes)", default=str(duration or "30")))
        focus = int(Prompt.ask("Focus level (1-5)", default=str(focus)))
        notes = Prompt.ask("Notes (optional)", default=notes or "") or None

    if not subject or not duration:
        print_error("Subject and duration are required")
        raise typer.Exit(1)

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Parse date
    if date:
        try:
            session_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print_error("Date must be in YYYY-MM-DD format")
            raise typer.Exit(1)
    else:
        session_date = datetime.now()

    session_id = add_session(subject, duration, session_date, focus, tag_list, notes)

    # Display success
    emoji = subject_emoji(subject)
    msg = get_motivational_message(duration)

    console.print(f"\n{emoji} [bold green]Session logged![/]")
    console.print(f"   Subject: [cyan]{subject}[/]")
    console.print(f"   Duration: [green]{duration} minutes[/]")
    console.print(f"   Focus: {'★' * focus}{'☆' * (5-focus)}")
    console.print(f"\n[italic dim]{msg}[/]\n")


@app.command()
def list(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of sessions to show"),
    subject: Optional[str] = typer.Option(None, "--subject", "-s", help="Filter by subject"),
):
    """List recent study sessions"""

    sessions = get_sessions(limit, subject)

    if not sessions:
        console.print("\n[dim]No study sessions found. Start tracking with:[/]")
        console.print("[cyan]  study add[/]\n")
        return

    table = Table(
        title="📚 Recent Study Sessions",
        box=box.ROUNDED,
        border_style="purple",
        header_style="bold cyan",
        row_styles=["", "dim"],
    )

    table.add_column("ID", style="dim", width=4)
    table.add_column("Date", style="white", width=12)
    table.add_column("Subject", style="cyan")
    table.add_column("Duration", style="green", justify="right")
    table.add_column("Focus", style="yellow", justify="center")
    table.add_column("Tags", style="dim blue")

    for s in sessions:
        tags_str = ", ".join(s.tags) if s.tags else ""
        table.add_row(
            str(s.id),
            s.date.strftime("%m/%d"),
            f"{subject_emoji(s.subject)} {s.subject}",
            format_duration(s.duration),
            "★" * s.focus + "☆" * (5 - s.focus),
            tags_str[:25],
        )

    console.print()
    console.print(table)
    console.print()


@app.command()
def edit(
    session_id: int = typer.Argument(..., help="Session ID to edit"),
):
    """Edit an existing study session"""

    session = get_session_by_id(session_id)
    if not session:
        print_error(f"Session {session_id} not found")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]Editing Session #{session_id}[/]\n")

    new_subject = Prompt.ask("Subject", default=session.subject)
    new_duration = int(Prompt.ask("Duration (minutes)", default=str(session.duration)))
    new_focus = int(Prompt.ask("Focus level (1-5)", default=str(session.focus)))

    update_session(session_id, new_subject, new_duration, session.date, new_focus, session.tags, session.notes)
    print_success("Session updated!")


@app.command()
def delete(
    session_id: int = typer.Argument(..., help="Session ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a study session"""

    session = get_session_by_id(session_id)
    if not session:
        print_error(f"Session {session_id} not found")
        raise typer.Exit(1)

    if not force:
        console.print(f"\n[yellow]Are you sure you want to delete this session?[/]")
        console.print(f"   {session.subject} - {format_duration(session.duration)}")
        if not Confirm.ask("Delete?", default=False):
            console.print("[dim]Cancelled[/]")
            return

    delete_session(session_id)
    print_success("Session deleted")


@app.command()
def today():
    """Show today's study summary"""

    today_date = datetime.now().date()
    start = datetime.combine(today_date, datetime.min.time())
    end = datetime.combine(today_date, datetime.max.time())

    sessions = get_sessions_by_date_range(start, end)

    total_minutes = sum(s.duration for s in sessions)
    subject_counts = {}

    for s in sessions:
        subject_counts[s.subject] = subject_counts.get(s.subject, 0) + s.duration

    console.print()
    console.print(Panel(
        f"[bold cyan]Today's Study Summary[/]\n\n"
        f"Total Time: [bold green]{format_duration(total_minutes)}[/]\n"
        f"Sessions: [bold]{len(sessions)}[/]\n"
        + ("\n[bold]Subjects:[/]\n" + "\n".join(
            f"  • [cyan]{sub}:[/] {format_duration(mins)}"
            for sub, mins in sorted(subject_counts.items(), key=lambda x: -x[1])
        ) if subject_counts else ""),
        border_style="green",
        width=60,
    ))
    console.print()
