"""Final state at end of CP5 — polished app with sidebar nav, streak, and edit page."""
import streamlit as st
import db
import prompts

db.init_db()
st.set_page_config(page_title="Pocket Coach", page_icon="🤖", layout="wide")

PAGES = ["Daily check-in", "🔍 See what Gemma saw", "Edit goals"]


def load_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;700&display=swap');
        
        /* Typography */
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        h1, h2, h3 { font-family: 'Outfit', sans-serif; }
        
        /* Metric cards for standard metrics */
        div[data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            background-color: rgba(255, 255, 255, 0.08);
        }
        
        /* Buttons */
        div[data-testid="stButton"] > button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        div[data-testid="stButton"] > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
        }
        
        /* Expanders */
        div[data-testid="stExpander"] {
            border-radius: 12px;
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            overflow: hidden;
        }
        </style>
    """, unsafe_allow_html=True)


def setup_wizard():
    st.title("Pocket Coach 🤖")
    st.write("Welcome — let's set up your goals.")
    with st.form("setup"):
        ex = st.number_input("Exercise hrs/week", 0, 30, 4)
        sd = st.number_input("Study hrs/week", 0, 60, 15)
        bk = st.number_input("Books/month", 0, 20, 1)
        subjects = st.text_input("Study Subjects (comma-separated)", "")
        other = st.text_input("Anything else? (optional)", "")
        persona = st.radio(
            "Coach style",
            ["supportive", "drill_sergeant", "philosopher", "hype_friend"],
        )
        if st.form_submit_button("Save"):
            db.save_goals(ex, sd, bk, persona, other=other, subjects=subjects)
            st.rerun()


def todo_list():
    st.subheader("📝 Daily To-Do List")
    todos = db.get_todos()
    for t in todos:
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            completed = st.checkbox(t["task"], value=bool(t["is_completed"]), key=f"todo_{t['id']}")
            if completed != bool(t["is_completed"]):
                db.toggle_todo(t["id"], completed)
                st.rerun()
        with col2:
            if st.button("❌", key=f"del_{t['id']}", help="Delete task"):
                db.delete_todo(t["id"])
                st.rerun()
    
    with st.form("add_todo_form", clear_on_submit=True):
        new_task = st.text_input("New task...")
        submitted = st.form_submit_button("Add Task")
        if submitted and new_task.strip():
            db.add_todo(new_task.strip())
            st.rerun()


def daily_check_in():
    goals = db.get_goals()
    st.title("Pocket Coach 🤖")
    
    # Render Metric Cards
    streak = db.streak_count_ending_today()
    col1, col2, col3 = st.columns(3)
    col1.metric("🔥 Streak", f"{streak} days" if streak else "0 days")
    col2.metric("🎭 Persona", goals['persona'].replace("_", " ").title())
    subjects = goals.get('subjects') or "None"
    col3.metric("📚 Subjects", subjects)
    
    st.markdown("---")
    
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.subheader("💬 Check In")
        today = st.text_area("How was today?", height=150, placeholder="I studied math for 2 hours and went for a run...")
        if st.button("Check in", type="primary", disabled=not today.strip(), use_container_width=True):
            with st.spinner("Gemma is thinking..."):
                result = prompts.run_daily_chain(today.strip())
            st.success(result["coach_reply"])
            with st.expander("Mood + progress summary"):
                st.write(f"**Mood:** {result['mood']}")
                st.write(f"**Progress:** {result['progress_summary']}")
                
    with col_right:
        todo_list()


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
        subjects = st.text_input("Study Subjects (comma-separated)", goals.get("subjects") or "")
        other = st.text_input("Other", goals.get("other_goal") or "")
        persona = st.radio(
            "Coach style",
            ["supportive", "drill_sergeant", "philosopher", "hype_friend"],
            index=["supportive", "drill_sergeant", "philosopher", "hype_friend"].index(
                goals["persona"]
            ),
        )
        if st.form_submit_button("Save changes"):
            db.save_goals(ex, sd, bk, persona, other=other, subjects=subjects)
            st.success("Saved.")


def main():
    load_css()
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
