"""
Database operations for Study Tracker CLI
"""

import sqlite3
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from platformdirs import user_data_dir

APP_NAME = "study-tracker"
APP_AUTHOR = "cli"

# Get platform-specific data directory
DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
DB_PATH = DATA_DIR / "study_tracker.db"


@dataclass
class StudySession:
    id: int
    subject: str
    duration: int  # minutes
    date: datetime
    focus: int  # 1-5
    tags: List[str]
    notes: Optional[str]


@dataclass
class Habit:
    id: int
    name: str
    category: str
    created_at: datetime


@dataclass
class HabitCompletion:
    id: int
    habit_id: int
    completed_date: str  # ISO format date


def get_connection() -> sqlite3.Connection:
    """Get database connection"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables"""
    conn = get_connection()
    cursor = conn.cursor()

    # Study sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            duration INTEGER NOT NULL,
            date TEXT NOT NULL,
            focus INTEGER DEFAULT 3,
            tags TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Habits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Habit completions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habit_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completed_date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id),
            UNIQUE(habit_id, completed_date)
        )
    """)

    conn.commit()
    conn.close()


# Study Session Operations

def add_session(
    subject: str,
    duration: int,
    date: datetime,
    focus: int = 3,
    tags: List[str] = None,
    notes: Optional[str] = None
) -> int:
    """Add a new study session"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO study_sessions (subject, duration, date, focus, tags, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (subject, duration, date.isoformat(), focus, json.dumps(tags or []), notes)
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_sessions(limit: int = 10, subject: Optional[str] = None) -> List[StudySession]:
    """Get recent study sessions"""
    conn = get_connection()
    cursor = conn.cursor()

    if subject:
        cursor.execute(
            """SELECT * FROM study_sessions WHERE subject = ? ORDER BY date DESC LIMIT ?""",
            (subject, limit)
        )
    else:
        cursor.execute(
            """SELECT * FROM study_sessions ORDER BY date DESC LIMIT ?""",
            (limit,)
        )

    rows = cursor.fetchall()
    conn.close()

    return [_row_to_session(row) for row in rows]


def get_session_by_id(session_id: int) -> Optional[StudySession]:
    """Get a session by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM study_sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_session(row) if row else None


def update_session(
    session_id: int,
    subject: str,
    duration: int,
    date: datetime,
    focus: int,
    tags: List[str],
    notes: Optional[str]
):
    """Update a study session"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE study_sessions
           SET subject = ?, duration = ?, date = ?, focus = ?, tags = ?, notes = ?
           WHERE id = ?""",
        (subject, duration, date.isoformat(), focus, json.dumps(tags), notes, session_id)
    )
    conn.commit()
    conn.close()


def delete_session(session_id: int):
    """Delete a study session"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM study_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()


def get_sessions_by_date_range(start: datetime, end: datetime) -> List[StudySession]:
    """Get sessions within a date range"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM study_sessions WHERE date >= ? AND date <= ? ORDER BY date DESC""",
        (start.isoformat(), end.isoformat())
    )
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_session(row) for row in rows]


def get_daily_totals(start: datetime, end: datetime) -> List[tuple]:
    """Get daily study totals for a date range"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT date(date) as day, SUM(duration) as total
           FROM study_sessions
           WHERE date >= ? AND date <= ?
           GROUP BY day
           ORDER BY day""",
        (start.isoformat(), end.isoformat())
    )
    rows = cursor.fetchall()
    conn.close()
    return [(row['day'], row['total']) for row in rows]


def get_all_subjects() -> List[Dict[str, Any]]:
    """Get aggregated data for all subjects"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT subject, SUM(duration) as total_minutes,
                  COUNT(*) as session_count,
                  AVG(focus) as avg_focus
           FROM study_sessions
           GROUP BY subject
           ORDER BY total_minutes DESC"""
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "name": row["subject"],
            "total_minutes": row["total_minutes"],
            "session_count": row["session_count"],
            "avg_focus": round(row["avg_focus"] or 3, 1),
        }
        for row in rows
    ]


def get_weekly_summary() -> Dict[str, Any]:
    """Get summary stats for current week"""
    now = datetime.now()
    start = now - timedelta(days=now.weekday())
    sessions = get_sessions_by_date_range(
        datetime.combine(start.date(), datetime.min.time()),
        now
    )

    total = sum(s.duration for s in sessions)
    return {
        "total_minutes": total,
        "session_count": len(sessions),
        "daily_average": total / 7,
    }


# Habit Operations

def add_habit(name: str, category: str = "general") -> int:
    """Add a new habit"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO habits (name, category) VALUES (?, ?)",
            (name, category)
        )
        habit_id = cursor.lastrowid
        conn.commit()
        return habit_id
    except sqlite3.IntegrityError:
        # Habit already exists, get its ID
        cursor.execute("SELECT id FROM habits WHERE name = ?", (name,))
        return cursor.fetchone()[0]
    finally:
        conn.close()


def get_habits() -> List[Habit]:
    """Get all habits"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habits ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [Habit(
        id=row["id"],
        name=row["name"],
        category=row["category"],
        created_at=datetime.fromisoformat(row["created_at"]),
    ) for row in rows]


def toggle_habit_today(habit_id: int, unmark: bool = False) -> bool:
    """Toggle habit completion for today"""
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().date().isoformat()

    cursor.execute(
        "SELECT id FROM habit_completions WHERE habit_id = ? AND completed_date = ?",
        (habit_id, today)
    )
    existing = cursor.fetchone()

    if unmark:
        if existing:
            cursor.execute(
                "DELETE FROM habit_completions WHERE id = ?",
                (existing["id"],)
            )
    else:
        if not existing:
            cursor.execute(
                "INSERT INTO habit_completions (habit_id, completed_date) VALUES (?, ?)",
                (habit_id, today)
            )
        else:
            conn.close()
            return True  # Already marked

    conn.commit()
    conn.close()
    return True


def get_habits_for_date(date: datetime) -> List[Habit]:
    """Get habits completed on a specific date"""
    conn = get_connection()
    cursor = conn.cursor()
    date_str = date.isoformat() if isinstance(date, datetime) else date

    cursor.execute(
        """SELECT h.* FROM habits h
           JOIN habit_completions hc ON h.id = hc.habit_id
           WHERE hc.completed_date = ?""",
        (date_str,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [Habit(
        id=row["id"],
        name=row["name"],
        category=row["category"],
        created_at=datetime.fromisoformat(row["created_at"]),
    ) for row in rows]


def get_habit_streak(habit_id: int) -> int:
    """Calculate current streak for a habit"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT completed_date FROM habit_completions
           WHERE habit_id = ? ORDER BY completed_date DESC""",
        (habit_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return 0

    streak = 0
    today = datetime.now().date()
    expected_date = today

    for row in rows:
        date = datetime.fromisoformat(row["completed_date"]).date()
        if date == expected_date or (streak == 0 and date == today):
            streak += 1
            expected_date -= timedelta(days=1)
        elif date < expected_date:
            break

    return streak


def delete_habit(habit_id: int) -> bool:
    """Delete a habit"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habit_completions WHERE habit_id = ?", (habit_id,))
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# Export

def export_data(format: str, output_path: Optional[str] = None) -> str:
    """Export all data to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format == "json":
        filepath = output_path or f"study_export_{timestamp}.json"
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM study_sessions")
        sessions = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM habits")
        habits = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM habit_completions")
        completions = [dict(row) for row in cursor.fetchall()]

        conn.close()

        with open(filepath, 'w') as f:
            json.dump({
                "sessions": sessions,
                "habits": habits,
                "completions": completions,
                "exported_at": datetime.now().isoformat(),
            }, f, indent=2, default=str)

    elif format == "csv":
        filepath = output_path or f"study_export_{timestamp}.csv"
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM study_sessions ORDER BY date DESC")
        rows = cursor.fetchall()
        conn.close()

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'subject', 'duration', 'date', 'focus', 'tags', 'notes'])
            for row in rows:
                writer.writerow([
                    row['id'],
                    row['subject'],
                    row['duration'],
                    row['date'],
                    row['focus'],
                    row['tags'],
                    row['notes']
                ])

    return filepath


def _row_to_session(row: sqlite3.Row) -> StudySession:
    """Convert database row to StudySession"""
    return StudySession(
        id=row["id"],
        subject=row["subject"],
        duration=row["duration"],
        date=datetime.fromisoformat(row["date"]),
        focus=row["focus"],
        tags=json.loads(row["tags"] or "[]"),
        notes=row["notes"],
    )
