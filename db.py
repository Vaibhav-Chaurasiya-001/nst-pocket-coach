"""SQLite persistence layer. No LLM awareness — talks to disk, returns dicts."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB_PATH = "data/coach.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS goals (
  id INTEGER PRIMARY KEY,
  exercise_hours_per_week INTEGER,
  study_hours_per_week INTEGER,
  books_per_month INTEGER,
  other_goal TEXT,
  persona TEXT DEFAULT 'supportive',
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS daily_logs (
  id INTEGER PRIMARY KEY,
  log_date TEXT,
  user_input TEXT,
  extracted_mood TEXT,
  progress_summary TEXT,
  coach_reply TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS prompt_runs (
  id INTEGER PRIMARY KEY,
  log_id INTEGER,
  step_name TEXT,
  prompt_text TEXT,
  response_text TEXT,
  ms_elapsed INTEGER,
  FOREIGN KEY (log_id) REFERENCES daily_logs(id)
);
"""


def _connect(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.executescript(SCHEMA)


def save_goals(exercise: int, study: int, books: int, persona: str,
               other: str = "", db_path: str = DEFAULT_DB_PATH) -> None:
    """Replace any prior goals row with a new one — only one active goal set at a time."""
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM goals")
        conn.execute(
            "INSERT INTO goals (exercise_hours_per_week, study_hours_per_week, "
            "books_per_month, other_goal, persona, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (exercise, study, books, other, persona,
             datetime.now(timezone.utc).isoformat()),
        )


def get_goals(db_path: str = DEFAULT_DB_PATH) -> dict | None:
    with _connect(db_path) as conn:
        row = conn.execute("SELECT * FROM goals ORDER BY id DESC LIMIT 1").fetchone()
        return dict(row) if row else None


def save_log(log_date: str, user_input: str, extracted_mood: str | None,
             progress_summary: str | None, coach_reply: str | None,
             db_path: str = DEFAULT_DB_PATH) -> int:
    with _connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO daily_logs (log_date, user_input, extracted_mood, "
            "progress_summary, coach_reply, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (log_date, user_input, extracted_mood, progress_summary, coach_reply,
             datetime.now(timezone.utc).isoformat()),
        )
        return cur.lastrowid


def get_recent_logs(n: int, db_path: str = DEFAULT_DB_PATH) -> list[dict]:
    """Return up to n most recent logs, newest first."""
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM daily_logs ORDER BY log_date DESC, id DESC LIMIT ?", (n,)
        ).fetchall()
        return [dict(r) for r in rows]


def save_prompt_run(log_id: int, step_name: str, prompt_text: str,
                    response_text: str, ms_elapsed: int,
                    db_path: str = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO prompt_runs (log_id, step_name, prompt_text, "
            "response_text, ms_elapsed) VALUES (?, ?, ?, ?, ?)",
            (log_id, step_name, prompt_text, response_text, ms_elapsed),
        )


def get_prompt_runs(log_id: int, db_path: str = DEFAULT_DB_PATH) -> list[dict]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM prompt_runs WHERE log_id = ? ORDER BY id ASC", (log_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def update_log_outputs(log_id: int, mood: str, progress_summary: str,
                       coach_reply: str, db_path: str = DEFAULT_DB_PATH) -> None:
    """Backfill the chain outputs onto a previously-saved daily_logs row."""
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE daily_logs SET extracted_mood = ?, progress_summary = ?, "
            "coach_reply = ? WHERE id = ?",
            (mood, progress_summary, coach_reply, log_id),
        )


def streak_count_ending_today(db_path: str = DEFAULT_DB_PATH) -> int:
    """Return consecutive days ending today (inclusive) with at least one log row."""
    from datetime import date, timedelta
    streak = 0
    cur = date.today()
    with _connect(db_path) as conn:
        while True:
            row = conn.execute(
                "SELECT 1 FROM daily_logs WHERE log_date = ? LIMIT 1",
                (cur.isoformat(),),
            ).fetchone()
            if not row:
                break
            streak += 1
            cur -= timedelta(days=1)
    return streak
