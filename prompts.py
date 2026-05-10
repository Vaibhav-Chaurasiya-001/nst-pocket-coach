"""Prompt templates and the daily check-in chain.

The chain is:
  1. extract_mood       - cheap classification of user_input
  2. evaluate_progress  - reads last 3 days from DB; summarises trend
  3. encourage          - persona-flavoured 2-3 sentence reply

Each step's prompt + response is persisted via db.save_prompt_run so you
can later inspect exactly what Gemma saw — that's the heart of CP4.
"""
import time
from datetime import date
from ai import generate
import db


HISTORY_DAYS = 3


EXTRACT_MOOD_TEMPLATE = """\
Read the student's check-in below and classify their mood as one of:
positive | neutral | negative | mixed

Then add ONE short sentence (max 12 words) explaining why.

Format your reply as: "<mood> — <reason>"

Student: {user_input}
"""


EVALUATE_PROGRESS_TEMPLATE = """\
You are an encouraging coach. The student's goals are:
- {exercise_hours_per_week} hours of exercise per week
- {study_hours_per_week} hours of study per week
- {books_per_month} books per month
- Other: {other_goal}

Their last few days of check-ins (newest first):
{history_block}

Today they said: "{user_input}"
Today's mood: {mood}

In 2-3 sentences, summarise how the student is tracking against their goals.
Be specific about what's going well and what could improve.
"""


ENCOURAGE_TEMPLATE = """\
You are a {persona} coach helping a Year 12 student.

Their progress today: {progress_summary}
Their mood: {mood}

Reply directly to the student in 2-3 sentences, fully in character as a {persona}.
Do not break character or explain yourself.
"""


def _format_history_block(logs: list[dict]) -> str:
    """Render a bullet list of recent logs, or a placeholder if empty."""
    if not logs:
        return "(No previous check-ins yet — this is their first.)"
    lines = []
    for log in logs:
        lines.append(
            f"- {log['log_date']}: {log['user_input']} "
            f"(mood: {log.get('extracted_mood', 'unknown')})"
        )
    return "\n".join(lines)


def run_daily_chain(user_input: str, db_path: str = db.DEFAULT_DB_PATH) -> dict:
    """Run the 3-step daily chain, persisting each prompt and its response.

    Returns: { log_id, mood, progress_summary, coach_reply }.
    """
    goals = db.get_goals(db_path=db_path) or {
        "exercise_hours_per_week": 0,
        "study_hours_per_week": 0,
        "books_per_month": 0,
        "other_goal": "",
        "persona": "supportive",
    }

    log_id = db.save_log(
        log_date=date.today().isoformat(),
        user_input=user_input,
        extracted_mood=None,
        progress_summary=None,
        coach_reply=None,
        db_path=db_path,
    )

    # Step 1 — extract mood
    p1 = EXTRACT_MOOD_TEMPLATE.format(user_input=user_input)
    t0 = time.time()
    mood = generate(p1).strip()
    db.save_prompt_run(log_id, "extract_mood", p1, mood,
                       int((time.time() - t0) * 1000), db_path=db_path)

    # Step 2 — evaluate progress (history-aware)
    history = db.get_recent_logs(HISTORY_DAYS, db_path=db_path)
    history = [h for h in history if h["id"] != log_id]
    p2 = EVALUATE_PROGRESS_TEMPLATE.format(
        **{k: goals[k] for k in (
            "exercise_hours_per_week", "study_hours_per_week",
            "books_per_month", "other_goal",
        )},
        history_block=_format_history_block(history),
        user_input=user_input,
        mood=mood,
    )
    t0 = time.time()
    progress_summary = generate(p2).strip()
    db.save_prompt_run(log_id, "evaluate_progress", p2, progress_summary,
                       int((time.time() - t0) * 1000), db_path=db_path)

    # Step 3 — encourage
    p3 = ENCOURAGE_TEMPLATE.format(
        persona=goals["persona"],
        progress_summary=progress_summary,
        mood=mood,
    )
    t0 = time.time()
    coach_reply = generate(p3).strip()
    db.save_prompt_run(log_id, "encourage", p3, coach_reply,
                       int((time.time() - t0) * 1000), db_path=db_path)

    db.update_log_outputs(log_id, mood, progress_summary, coach_reply,
                          db_path=db_path)

    return {
        "log_id": log_id,
        "mood": mood,
        "progress_summary": progress_summary,
        "coach_reply": coach_reply,
    }
