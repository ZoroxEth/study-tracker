"""
Timer utilities for focus mode
"""

import time
from typing import Optional


class Timer:
    """Simple countdown timer for Pomodoro sessions"""

    def __init__(self, duration_seconds: int):
        self.duration = duration_seconds
        self.start_time: Optional[float] = None
        self.elapsed = 0
        self.is_paused = False
        self.start()

    def start(self):
        """Start the timer"""
        self.start_time = time.time() - self.elapsed
        self.is_paused = False

    def pause(self):
        """Pause the timer"""
        if not self.is_paused:
            self.elapsed = time.time() - self.start_time
            self.is_paused = True

    def resume(self):
        """Resume the timer"""
        if self.is_paused:
            self.start_time = time.time() - self.elapsed
            self.is_paused = False

    def tick(self):
        """Update elapsed time (call once per second)"""
        if not self.is_paused:
            self.elapsed = time.time() - self.start_time

    def remaining_seconds(self) -> int:
        """Get remaining seconds"""
        return max(0, int(self.duration - self.elapsed))

    def is_finished(self) -> bool:
        """Check if timer is complete"""
        return self.remaining_seconds() <= 0

    def get_progress(self) -> float:
        """Get progress as percentage (0.0 to 1.0)"""
        if self.duration == 0:
            return 1.0
        return min(1.0, self.elapsed / self.duration)

    def format_remaining(self) -> str:
        """Format remaining time as MM:SS"""
        remaining = self.remaining_seconds()
        minutes = remaining // 60
        seconds = remaining % 60
        return f"{minutes:02d}:{seconds:02d}"
