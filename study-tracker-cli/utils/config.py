"""
Configuration management for Study Tracker CLI
"""

import json
from pathlib import Path
from typing import Dict, Any
from platformdirs import user_config_dir

APP_NAME = "study-tracker"
APP_AUTHOR = "cli"

CONFIG_DIR = Path(user_config_dir(APP_NAME, APP_AUTHOR))
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "theme": "dark",
    "default_focus_duration": 25,
    "default_break_duration": 5,
    "daily_goal_minutes": 120,
    "weekly_goal_hours": 14,
    "sound_enabled": True,
    "notifications_enabled": True,
    "auto_start_break": False,
    "keyboard_shortcuts": {
        "quick_add": "ctrl+shift+s",
        "start_timer": "ctrl+shift+f",
        "mark_habits": "ctrl+shift+h",
    },
    "export_format": "csv",
}


def ensure_config():
    """Ensure config file exists with defaults"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)


def get_config() -> Dict[str, Any]:
    """Load configuration"""
    ensure_config()

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Merge with defaults for any missing keys
            merged = DEFAULT_CONFIG.copy()
            merged.update(config)
            return merged
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]):
    """Save configuration"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def update_config(key: str, value: Any):
    """Update a specific config value"""
    config = get_config()
    config[key] = value
    save_config(config)


def get_data_dir() -> Path:
    """Get platform-specific data directory"""
    from platformdirs import user_data_dir
    data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
