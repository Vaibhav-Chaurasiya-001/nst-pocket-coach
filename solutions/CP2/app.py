import streamlit as st
import db

db.init_db()
st.set_page_config(page_title="Pocket Coach", page_icon="🤖")
st.title("Pocket Coach 🤖")

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
else:
    st.success(f"Welcome back! Persona: {goals['persona']}")
    st.write(f"Exercise: {goals['exercise_hours_per_week']} hrs/wk")
    st.write(f"Study: {goals['study_hours_per_week']} hrs/wk")
    st.write(f"Books: {goals['books_per_month']}/month")
