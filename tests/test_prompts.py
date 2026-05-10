import tempfile
import os
import pytest
from unittest.mock import patch
import db
import prompts


@pytest.fixture
def db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db.init_db(path)
    db.save_goals(4, 15, 1, "supportive", db_path=path)
    yield path
    os.remove(path)


def test_extract_mood_template_includes_input():
    rendered = prompts.EXTRACT_MOOD_TEMPLATE.format(user_input="ran 5km")
    assert "ran 5km" in rendered
    assert "positive" in rendered.lower() or "mood" in rendered.lower()


def test_encourage_template_includes_persona():
    rendered = prompts.ENCOURAGE_TEMPLATE.format(
        persona="drill_sergeant",
        progress_summary="on track",
        mood="positive",
    )
    assert "drill_sergeant" in rendered
    assert "on track" in rendered


def test_run_daily_chain_calls_three_steps(db_path):
    fake_replies = iter(["positive — strong day", "tracking well overall", "Crushing it!"])
    with patch("prompts.generate", side_effect=lambda _: next(fake_replies)):
        result = prompts.run_daily_chain("studied 4 hours", db_path=db_path)

    assert result["mood"].startswith("positive")
    assert "tracking well" in result["progress_summary"]
    assert result["coach_reply"] == "Crushing it!"

    runs = db.get_prompt_runs(result["log_id"], db_path=db_path)
    assert [r["step_name"] for r in runs] == [
        "extract_mood", "evaluate_progress", "encourage"
    ]


def test_run_daily_chain_includes_history_in_step_2(db_path):
    db.save_log("2026-05-08", "yesterday's input", "neutral", "ok", "keep going",
                db_path=db_path)
    captured_prompts = []

    def fake_generate(prompt):
        captured_prompts.append(prompt)
        return "fake response"

    with patch("prompts.generate", side_effect=fake_generate):
        prompts.run_daily_chain("today's input", db_path=db_path)

    step_2_prompt = captured_prompts[1]
    assert "yesterday's input" in step_2_prompt
