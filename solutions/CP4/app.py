import streamlit as st
import db
import prompts

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

page = st.sidebar.radio("Page", ["Daily check-in", "🔍 See what Gemma saw"])

if page == "Daily check-in":
    st.title("Pocket Coach 🤖")
    st.caption(f"Persona: {goals['persona']}")
    today = st.text_area("How was today?", height=100)
    if st.button("Check in", type="primary", disabled=not today.strip()):
        with st.spinner("Gemma is thinking..."):
            result = prompts.run_daily_chain(today.strip())
        st.success(result["coach_reply"])
        with st.expander("Mood + progress summary"):
            st.write(f"**Mood:** {result['mood']}")
            st.write(f"**Progress:** {result['progress_summary']}")
else:
    st.title("🔍 See what Gemma saw")
    logs = db.get_recent_logs(10)
    if not logs:
        st.info("No check-ins yet.")
    for log in logs:
        with st.expander(f"{log['log_date']} — {log['user_input'][:50]}"):
            for run in db.get_prompt_runs(log["id"]):
                st.markdown(f"### Step: `{run['step_name']}`  ({run['ms_elapsed']} ms)")
                st.code(run["prompt_text"], language="text")
                st.markdown(f"**Gemma replied:** {run['response_text']}")
