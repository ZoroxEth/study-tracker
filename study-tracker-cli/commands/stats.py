"""
Analytics and statistics commands
"""

from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich import box
from rich.tree import Tree
from rich.text import Text

from database.db import (
    get_sessions_by_date_range, get_all_subjects,
    get_daily_totals, get_weekly_summary
)
from utils.formatters import (
    format_duration, get_insight_message,
    subject_emoji, print_success
)

app = typer.Typer(help="View analytics and insights")
console = Console()


@app.command()
def today():
    """Show today's study stats"""

    today_date = datetime.now()
    start = datetime.combine(today_date.date(), datetime.min.time())
    end = datetime.combine(today_date.date(), datetime.max.time())

    sessions = get_sessions_by_date_range(start, end)
    total_minutes = sum(s.duration for s in sessions)

    # Subject breakdown
    subject_data = defaultdict(int)
    for s in sessions:
        subject_data[s.subject] += s.duration

    console.print()
    console.print(f"[bold cyan]📅 {today_date.strftime('%A, %B %d')}[/]\n")

    # Main stats
    hours = total_minutes / 60
    console.print(Panel(
        f"[bold green]{hours:.1f}[/] hours\n"
        f"[dim]{len(sessions)} sessions[/]",
        title="[bold]Total Study Time[/]",
        border_style="green",
        width=30,
    ))

    if subject_data:
        console.print("\n[bold]Subjects:[/]")
        for subject, mins in sorted(subject_data.items(), key=lambda x: -x[1]):
            bar_length = int((mins / max(subject_data.values())) * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            console.print(f"  {subject_emoji(subject)} {subject:<15} {bar}  {format_duration(mins)}")

    console.print()


@app.command()
def week(
    last: bool = typer.Option(False, "--last", "-l", help="Show last week instead of current"),
):
    """Show weekly study summary"""

    now = datetime.now()
    if last:
        end = now - timedelta(days=now.weekday() + 1)
        start = end - timedelta(days=6)
    else:
        start = now - timedelta(days=now.weekday())
        end = start + timedelta(days=6)

    sessions = get_sessions_by_date_range(start, end)

    total_minutes = sum(s.duration for s in sessions)
    daily_data = defaultdict(int)
    subject_data = defaultdict(int)

    for s in sessions:
        day = s.date.strftime("%a")
        daily_data[day] += s.duration
        subject_data[s.subject] += s.duration

    console.print()
    title = "Last Week" if last else "This Week"
    console.print(f"[bold cyan]📊 {title} - {start.strftime('%m/%d')} to {end.strftime('%m/%d')}[/]\n")

    # Weekly chart
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    max_mins = max(daily_data.values()) if daily_data else 1

    console.print("[bold]Daily Breakdown:[/]\n")
    for day in days:
        mins = daily_data.get(day, 0)
        bar_length = int((mins / max(max_mins, 1)) * 25)
        bar = "█" * bar_length + "░" * (25 - bar_length)
        color = "green" if mins > 60 else "yellow" if mins > 0 else "dim"
        time_str = format_duration(mins) if mins > 0 else "-"
        console.print(f"  [bold]{day}[/]  [{color}]{bar}[/{color}]  {time_str}")

    # Summary
    avg_daily = total_minutes / 7
    console.print(f"\n[dim]Total: {format_duration(total_minutes)}  •  Daily Avg: {format_duration(int(avg_daily))}[/]")

    # Subject breakdown
    if subject_data:
        console.print("\n[bold]Subjects:[/]")
        for subject, mins in sorted(subject_data.items(), key=lambda x: -x[1])[:5]:
            pct = (mins / total_minutes) * 100 if total_minutes > 0 else 0
            console.print(f"  {subject_emoji(subject)} {subject:<15} {format_duration(mins):>8}  ({pct:.1f}%)")

    console.print()


@app.command()
def subjects():
    """Show subject-wise analytics"""

    subjects_list = get_all_subjects()
    if not subjects_list:
        console.print("[dim]No data yet[/]")
        return

    table = Table(
        title="📚 Subject Analytics",
        box=box.ROUNDED,
        border_style="purple",
        header_style="bold cyan",
    )

    table.add_column("Subject", style="white")
    table.add_column("Total Time", style="green", justify="right")
    table.add_column("Sessions", style="blue", justify="right")
    table.add_column("Avg Focus", style="yellow", justify="center")

    for subject_data in sorted(subjects_list, key=lambda x: -x["total_minutes"]):
        emoji = subject_emoji(subject_data["name"])
        table.add_row(
            f"{emoji} {subject_data['name']}",
            format_duration(subject_data["total_minutes"]),
            str(subject_data["session_count"]),
            "★" * int(subject_data["avg_focus"]),
        )

    console.print()
    console.print(table)
    console.print()


@app.command()
def insights():
    """Show AI-style insights about your study patterns"""

    now = datetime.now()
    week_ago = now - timedelta(days=7)

    sessions = get_sessions_by_date_range(week_ago, now)

    if not sessions:
        console.print("\n[dim]Not enough data for insights yet. Keep tracking![/]\n")
        return

    # Calculate metrics
    total_minutes = sum(s.duration for s in sessions)
    avg_daily = total_minutes / 7

    # Find best day
    daily_totals = defaultdict(int)
    hourly_totals = defaultdict(int)
    subject_totals = defaultdict(int)

    for s in sessions:
        day = s.date.strftime("%A")
        daily_totals[day] += s.duration
        hourly_totals[s.date.hour] += s.duration
        subject_totals[s.subject] += s.duration

    best_day = max(daily_totals.items(), key=lambda x: x[1])
    best_hour = max(hourly_totals.items(), key=lambda x: x[1])
    top_subject = max(subject_totals.items(), key=lambda x: x[1])

    # Consistency check
    days_with_sessions = len([d for d in daily_totals.values() if d > 0])
    consistency = (days_with_sessions / 7) * 100

    console.print()
    console.print(Panel(
        "[bold cyan]🤖 Study Insights[/]",
        border_style="cyan",
        width=60,
    ))

    # Insight cards
    insights_data = [
        ("🌟", "Peak Performance", f"You study best on [bold]{best_day[0]}s[/] ({format_duration(best_day[1])})"),
        ("⏰", "Power Hour", f"Most productive at [bold]{best_hour[0]}:00[/] ({format_duration(best_hour[1])})"),
        ("📚", "Top Subject", f"[bold]{top_subject[0]}[/] leads with {format_duration(top_subject[1])}"),
        ("📈", "Consistency", f"Studied on [bold]{days_with_sessions}/7[/] days ({consistency:.0f}%)"),
    ]

    for emoji, title, desc in insights_data:
        console.print(f"\n  {emoji} [bold]{title}[/]")
        console.print(f"     {desc}")

    # Motivational message
    msg = get_insight_message(total_minutes, consistency)
    console.print(f"\n[italic dim]💡 {msg}[/]")
    console.print()


@app.command()
def trends(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
):
    """Show study trends over time"""

    end = datetime.now()
    start = end - timedelta(days=days)

    daily_totals = get_daily_totals(start, end)

    if not daily_totals:
        console.print("[dim]No data for this period[/]")
        return

    console.print(f"\n[bold cyan]📈 Study Trends - Last {days} Days[/]\n")

    # Simple ASCII trend
    values = [m for _, m in daily_totals]
    max_val = max(values) if values else 1

    # Show last 14 days
    for date_str, minutes in list(daily_totals)[-14:]:
        date_obj = datetime.fromisoformat(date_str)
        day_label = date_obj.strftime("%a %m/%d")
        bar_length = int((minutes / max(max_val, 1)) * 30)
        bar = "█" * bar_length + "░" * (30 - bar_length)

        if minutes >= 120:
            color = "green"
        elif minutes >= 60:
            color = "yellow"
        elif minutes > 0:
            color = "white"
        else:
            color = "dim"

        time_str = format_duration(minutes) if minutes > 0 else "—"
        console.print(f"  [bold]{day_label}[/]  [{color}]{bar}[/{color}]  {time_str}")

    # Stats
    total = sum(values)
    avg = total / len(values) if values else 0
    console.print(f"\n[dim]Total: {format_duration(total)}  •  Daily Avg: {format_duration(int(avg))}[/]")
    console.print()


@app.command()
def export(
    format: str = typer.Option("csv", "--format", "-f", help="Export format (csv/json)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Export study data"""

    from database.db import export_data

    filepath = export_data(format, output)
    print_success(f"Data exported to: [cyan]{filepath}[/]")
