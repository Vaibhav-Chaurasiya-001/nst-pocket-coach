import tempfile
import os
import pytest
from db import (
    init_db, save_goals, get_goals,
    save_log, get_recent_logs,
    save_prompt_run, get_prompt_runs,
)


@pytest.fixture
def db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    os.remove(path)


def test_goals_roundtrip(db_path):
    save_goals(4, 15, 1, "supportive", db_path=db_path)
    goals = get_goals(db_path=db_path)
    assert goals["exercise_hours_per_week"] == 4
    assert goals["study_hours_per_week"] == 15
    assert goals["books_per_month"] == 1
    assert goals["persona"] == "supportive"


def test_get_goals_empty_returns_none(db_path):
    assert get_goals(db_path=db_path) is None


def test_save_goals_replaces_previous(db_path):
    save_goals(4, 15, 1, "supportive", db_path=db_path)
    save_goals(5, 20, 2, "drill_sergeant", db_path=db_path)
    goals = get_goals(db_path=db_path)
    assert goals["persona"] == "drill_sergeant"
    assert goals["exercise_hours_per_week"] == 5


def test_log_roundtrip(db_path):
    log_id = save_log(
        log_date="2026-05-09",
        user_input="ran 5km",
        extracted_mood="positive",
        progress_summary="on track",
        coach_reply="Nice work!",
        db_path=db_path,
    )
    assert log_id > 0
    logs = get_recent_logs(5, db_path=db_path)
    assert len(logs) == 1
    assert logs[0]["user_input"] == "ran 5km"
    assert logs[0]["coach_reply"] == "Nice work!"


def test_get_recent_logs_returns_newest_first(db_path):
    save_log("2026-05-07", "day 1", "neutral", "ok", "Keep going", db_path=db_path)
    save_log("2026-05-08", "day 2", "positive", "ok", "Nice", db_path=db_path)
    save_log("2026-05-09", "day 3", "positive", "ok", "Awesome", db_path=db_path)
    logs = get_recent_logs(2, db_path=db_path)
    assert len(logs) == 2
    assert logs[0]["log_date"] == "2026-05-09"
    assert logs[1]["log_date"] == "2026-05-08"


def test_prompt_run_roundtrip(db_path):
    log_id = save_log("2026-05-09", "hi", None, None, None, db_path=db_path)
    save_prompt_run(log_id, "extract_mood", "Prompt text...", "positive", 123, db_path=db_path)
    save_prompt_run(log_id, "evaluate_progress", "Other prompt...", "tracking well", 456, db_path=db_path)
    runs = get_prompt_runs(log_id, db_path=db_path)
    assert len(runs) == 2
    assert runs[0]["step_name"] == "extract_mood"
    assert runs[0]["ms_elapsed"] == 123
    assert runs[1]["step_name"] == "evaluate_progress"


def test_update_log_outputs(db_path):
    log_id = save_log("2026-05-09", "ran 5km", None, None, None, db_path=db_path)
    from db import update_log_outputs
    update_log_outputs(log_id, "positive", "great progress", "Awesome work!",
                       db_path=db_path)
    logs = get_recent_logs(1, db_path=db_path)
    assert logs[0]["extracted_mood"] == "positive"
    assert logs[0]["progress_summary"] == "great progress"
    assert logs[0]["coach_reply"] == "Awesome work!"


def test_streak_count_ending_today(db_path):
    from datetime import date, timedelta
    from db import streak_count_ending_today
    today = date.today()
    save_log(today.isoformat(), "x", None, None, None, db_path=db_path)
    save_log((today - timedelta(days=1)).isoformat(), "y", None, None, None, db_path=db_path)
    save_log((today - timedelta(days=3)).isoformat(), "skip", None, None, None, db_path=db_path)
    assert streak_count_ending_today(db_path=db_path) == 2
