from datetime import date
import streamlit as st
import db
from ai import generate

db.init_db()
st.set_page_config(page_title="Pocket Coach", page_icon="🤖")

goals = db.get_goals()
if goals is None:
    with st.form("setup"):
        ex = st.number_input("Exercise hrs/week", 0, 30, 4)
        sd = st.number_input("Study hrs/week", 0, 60, 15)
        bk = st.number_input("Books/month", 0, 20, 1)
        persona = st.radio(
            "Coach style",
            ["supportive", "drill_sergeant", "philosopher", "hype_friend"],
        )
        if st.form_submit_button("Save"):
            db.save_goals(ex, sd, bk, persona)
            st.rerun()
    st.stop()

st.title("Pocket Coach 🤖")
st.caption(f"Persona: {goals['persona']}")

today = st.text_area("How was today?", height=100)
if st.button("Check in", type="primary", disabled=not today.strip()):
    prompt_text = f"""You are a {goals['persona']} coach.
The student aims for {goals['exercise_hours_per_week']}h exercise per week,
{goals['study_hours_per_week']}h study, {goals['books_per_month']} books/month.

Today they said: {today.strip()}

Reply in 2-3 sentences, fully in character."""
    with st.spinner("Gemma is thinking..."):
        reply = generate(prompt_text)
    log_id = db.save_log(
        log_date=date.today().isoformat(),
        user_input=today.strip(),
        extracted_mood=None,
        progress_summary=None,
        coach_reply=reply,
    )
    db.save_prompt_run(log_id, "single_check_in", prompt_text, reply, 0)
    st.success(reply)
