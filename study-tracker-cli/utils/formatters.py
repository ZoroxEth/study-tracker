"""
Formatting utilities for Study Tracker CLI
"""

import random
from typing import Dict, List
from rich.console import Console

console = Console()


def format_duration(minutes: int) -> str:
    """Format minutes into human-readable string"""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def subject_emoji(subject: str) -> str:
    """Get emoji for subject"""
    subject_lower = subject.lower()
    emojis = {
        "python": "🐍",
        "javascript": "⚡",
        "js": "⚡",
        "typescript": "🔷",
        "ts": "🔷",
        "rust": "🦀",
        "go": "🐹",
        "java": "☕",
        "cpp": "⚙️",
        "c++": "⚙️",
        "c": "🔧",
        "ruby": "💎",
        "swift": "🍎",
        "kotlin": "📱",
        "sql": "🗄️",
        "database": "🗄️",
        "math": "📐",
        "mathematics": "📐",
        "statistics": "📊",
        "data science": "📊",
        "machine learning": "🤖",
        "ml": "🤖",
        "ai": "🧠",
        "reading": "📖",
        "writing": "✍️",
        "english": "📝",
        "history": "🏛️",
        "science": "🔬",
        "physics": "⚛️",
        "chemistry": "🧪",
        "biology": "🧬",
        "design": "🎨",
        "ui": "🎨",
        "ux": "🎯",
        "devops": "🚀",
        "docker": "🐳",
        "kubernetes": "☸️",
        "git": "📦",
        "web": "🌐",
        "frontend": "💻",
        "backend": "🔌",
        "fullstack": "🥞",
        "mobile": "📱",
        "android": "🤖",
        "ios": "🍎",
        "algorithms": "🧩",
        "leetcode": "🏆",
        "system design": "🏗️",
        "interview": "🎤",
        "networking": "🌐",
        "security": "🔒",
        "cloud": "☁️",
        "aws": "☁️",
        "azure": "☁️",
        "gcp": "☁️",
    }

    for key, emoji in emojis.items():
        if key in subject_lower:
            return emoji
    return "📚"


def get_motivational_message(minutes: int) -> str:
    """Get a motivational message based on session length"""
    if minutes >= 120:
        messages = [
            "Epic deep work session! 🚀",
            "You're on fire! Keep it up! 🔥",
            "That's how legends are made! 💪",
            "Pure focus. Pure power. ⚡",
            "Incredible dedication! 🌟",
        ]
    elif minutes >= 60:
        messages = [
            "Solid hour of focus! 💪",
            "Great progress today! 📈",
            "One step closer to mastery! 🎯",
            "Keep building that momentum! 🚀",
            "Quality study time! ⭐",
        ]
    elif minutes >= 30:
        messages = [
            "Good focused session! 👍",
            "Consistency is key! 🔑",
            "Every minute counts! ⏱️",
            "Stay in the flow! 🌊",
        ]
    else:
        messages = [
            "Quick wins matter too! ✨",
            "Every session helps! 🌱",
            "Small steps forward! 👣",
            "Keep the streak going! 🔥",
        ]

    return random.choice(messages)


def get_insight_message(total_minutes: int, consistency: float) -> str:
    """Get personalized insight message"""
    if total_minutes > 600 and consistency > 80:
        return "You're a productivity machine! Keep crushing it! 🔥"
    elif total_minutes > 300 and consistency > 60:
        return "Great consistency! You're building strong habits. 💪"
    elif total_minutes > 300:
        return "Good volume, but try to study more regularly for better results. 📅"
    elif consistency > 60:
        return "You're consistent, but longer sessions could boost your progress. ⏱️"
    else:
        return "Start small, build the habit. You've got this! 🌱"


def print_success(message: str):
    """Print success message"""
    console.print(f"[bold green]✓[/] {message}")


def print_error(message: str):
    """Print error message"""
    console.print(f"[bold red]✗[/] {message}")


def print_warning(message: str):
    """Print warning message"""
    console.print(f"[bold yellow]⚠[/] {message}")


def print_info(message: str):
    """Print info message"""
    console.print(f"[bold blue]ℹ[/] {message}")


# Procrastination roasts
ROAST_MESSAGES = [
    "You're procrastinating again, bro. Just start. 🚨",
    "Future you is begging you to start. Please? 🥺",
    "Your goals aren't going to achieve themselves. 🎯",
    "That phone isn't going to scroll itself... oh wait. 📱",
    "Netflix will still be there after you study. Promise. 📺",
    "Your brain is a muscle. Exercise it. 🧠💪",
    "The best time to start was yesterday. The second best is NOW. ⏰",
    "Stop waiting for motivation. Create discipline. ⚡",
]


def get_roast() -> str:
    """Get a random roast message"""
    return random.choice(ROAST_MESSAGES)
