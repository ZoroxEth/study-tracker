[README.md](https://github.com/user-attachments/files/26575439/README.md)
# 🧠 Study Tracker CLI

A powerful, modern terminal-based study tracker with analytics, habit tracking, and Pomodoro focus mode. Built for developers who love clean CLI tools.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 📚 Study Session Management
- Log study sessions with subject, duration, and focus rating
- Tag sessions for organization
- Edit and delete sessions
- Automatic SQLite storage

### 🔥 Habit Tracking
- Track daily habits with streak counters
- Categories: study, health, productivity
- Visual streak leaderboard

### 📊 Analytics & Insights
- Daily and weekly summaries
- Subject-wise breakdowns
- ASCII-style trend charts
- "AI" insights about your study patterns

### 🎯 Focus Mode (Pomodoro)
- Built-in customizable timer
- Beautiful terminal countdown display
- Auto-log completed sessions
- Break timer included

### 🎨 Modern CLI Design
- **Rich** terminal UI with colors, tables, and progress bars
- Command-based interface (study add, habit list, etc.)
- Dark theme with hacker aesthetics
- Responsive layouts

## 🚀 Installation

### Method 1: Using pip

```bash
# Clone the repository
git clone <repo-url>
cd study-tracker-cli

# Install dependencies
pip install -r requirements.txt

# Run the CLI
python main.py welcome
```

### Method 2: Using poetry (recommended)

```bash
# Install poetry if not already installed
pip install poetry

# Install dependencies
poetry install

# Run the CLI
poetry run python main.py welcome
```

## 📖 Usage

### Quick Start

```bash
# See the welcome screen
python main.py welcome

# Add a study session
python main.py study add --subject "Python" --duration 60 --tags "coding"

# Start Pomodoro timer
python main.py focus start --duration 25 --subject "Deep Work"

# Mark habits complete
python main.py habit mark

# View today's stats
python main.py stats today
```

### Commands Reference

#### Study Sessions
```bash
study add [OPTIONS]              # Log a new session
study list [OPTIONS]             # View recent sessions
study edit SESSION_ID            # Edit a session
study delete SESSION_ID          # Delete a session
study today                      # Today's summary
```

#### Habits
```bash
habit add --name "Exercise"      # Create new habit
habit list                       # View all habits
habit mark [--id ID]             # Mark habit complete
habit streaks                    # Streak leaderboard
habit delete HABIT_ID            # Delete a habit
```

#### Focus Timer
```bash
focus start [OPTIONS]            # Start Pomodoro timer
focus quick MINUTES              # Quick focus session
```

#### Statistics
```bash
stats today                      # Today's stats
stats week [--last]              # Weekly summary
stats subjects                   # Subject analytics
stats insights                   # AI-style insights
stats trends [--days 30]         # Trend charts
stats export [--format csv]      # Export data
```

### Examples

```bash
# Log a study session with all options
study add \
  --subject "Algorithms" \
  --duration 90 \
  --focus 5 \
  --tags "leetcode,interview" \
  --notes "Solved 3 hard problems"

# Start a 50/10 Pomodoro
focus start --duration 50 --break 10 --subject "System Design"

# View last week's stats
stats week --last

# Export to CSV
stats export --format csv --output my_study_data.csv
```

## 🗂️ Project Structure

```
study-tracker-cli/
├── main.py              # Entry point
├── pyproject.toml       # Poetry config
├── requirements.txt     # Dependencies
├── README.md
│
├── commands/            # CLI command modules
│   ├── __init__.py
│   ├── study.py         # Study session commands
│   ├── habit.py         # Habit tracking commands
│   ├── focus.py         # Pomodoro timer commands
│   └── stats.py         # Analytics commands
│
├── database/            # Database layer
│   ├── __init__.py
│   └── db.py            # SQLite operations
│
└── utils/               # Utilities
    ├── __init__.py
    ├── formatters.py    # Display formatting
    ├── timer.py         # Timer logic
    └── config.py        # Config management
```

## 🎨 Design Philosophy

- **Clean commands**: `study add` instead of interactive menus
- **Rich output**: Tables, progress bars, colored text
- **Fast feedback**: Quick commands with optional interactivity
- **Data portability**: SQLite + CSV/JSON export
- **Keyboard-friendly**: Short commands, tab completion support

## 🔧 Configuration

Config is stored in platform-specific location:
- **Linux**: `~/.config/study-tracker/`
- **macOS**: `~/Library/Application Support/study-tracker/`
- **Windows**: `%APPDATA%/study-tracker/`

Edit `config.json` to customize:
- Default Pomodoro duration
- Daily/weekly goals
- Theme settings

## 📝 Data Storage

All data is stored locally in SQLite:
- **Linux**: `~/.local/share/study-tracker/`
- **macOS**: `~/Library/Application Support/study-tracker/`
- **Windows**: `%LOCALAPPDATA%/study-tracker/`

Back up your data:
```bash
stats export --format json
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use and modify!

---

Built with ❤️ for focused developers.
