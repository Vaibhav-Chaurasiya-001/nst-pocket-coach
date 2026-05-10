"""Final state at end of CP5 — polished app with sidebar nav, streak, and edit page."""
import streamlit as st
import db
import prompts

db.init_db()
st.set_page_config(page_title="Pocket Coach", page_icon="🤖")

PAGES = ["Daily check-in", "🔍 See what Gemma saw", "Edit goals"]


def setup_wizard():
    st.title("Pocket Coach 🤖")
    st.write("Welcome — let's set up your goals.")
    with st.form("setup"):
        ex = st.number_input("Exercise hrs/week", 0, 30, 4)
        sd = st.number_input("Study hrs/week", 0, 60, 15)
        bk = st.number_input("Books/month", 0, 20, 1)
        other = st.text_input("Anything else? (optional)", "")
        persona = st.radio(
            "Coach style",
            ["supportive", "drill_sergeant", "philosopher", "hype_friend"],
        )
        if st.form_submit_button("Save"):
            db.save_goals(ex, sd, bk, persona, other=other)
            st.rerun()


def daily_check_in():
    goals = db.get_goals()
    st.title("Pocket Coach 🤖")
    streak = db.streak_count_ending_today()
    if streak:
        st.caption(f"🔥 {streak}-day streak · Persona: {goals['persona']}")
    else:
        st.caption(f"Persona: {goals['persona']}")

    today = st.text_area("How was today?", height=100)
    if st.button("Check in", type="primary", disabled=not today.strip()):
        with st.spinner("Gemma is thinking..."):
            result = prompts.run_daily_chain(today.strip())
        st.success(result["coach_reply"])
        with st.expander("Mood + progress summary"):
            st.write(f"**Mood:** {result['mood']}")
            st.write(f"**Progress:** {result['progress_summary']}")


def see_what_gemma_saw():
    st.title("🔍 See what Gemma saw")
    logs = db.get_recent_logs(10)
    if not logs:
        st.info("No check-ins yet.")
        return
    for log in logs:
        with st.expander(f"{log['log_date']} — {log['user_input'][:50]}"):
            for run in db.get_prompt_runs(log["id"]):
                st.markdown(f"### Step: `{run['step_name']}`  ({run['ms_elapsed']} ms)")
                st.code(run["prompt_text"], language="text")
                st.markdown(f"**Gemma replied:** {run['response_text']}")


def edit_goals():
    st.title("Edit goals")
    goals = db.get_goals()
    with st.form("edit"):
        ex = st.number_input("Exercise hrs/week", 0, 30, goals["exercise_hours_per_week"])
        sd = st.number_input("Study hrs/week", 0, 60, goals["study_hours_per_week"])
        bk = st.number_input("Books/month", 0, 20, goals["books_per_month"])
        other = st.text_input("Other", goals.get("other_goal") or "")
        persona = st.radio(
            "Coach style",
            ["supportive", "drill_sergeant", "philosopher", "hype_friend"],
            index=["supportive", "drill_sergeant", "philosopher", "hype_friend"].index(
                goals["persona"]
            ),
        )
        if st.form_submit_button("Save changes"):
            db.save_goals(ex, sd, bk, persona, other=other)
            st.success("Saved.")


def main():
    if db.get_goals() is None:
        setup_wizard()
        return
    page = st.sidebar.radio("Page", PAGES)
    if page == "Daily check-in":
        daily_check_in()
    elif page == "🔍 See what Gemma saw":
        see_what_gemma_saw()
    elif page == "Edit goals":
        edit_goals()


if __name__ == "__main__":
    main()
