# Pocket Coach — starter file
# A Newton School of Technology AI workshop.
#
# Each `# TODO (CPn)` block marks where you'll add code during checkpoint n.
# Don't delete the markers — they're your map. If you fall behind, copy the
# matching solutions/CPn/app.py over this file and keep going.

import streamlit as st
import db

db.init_db()
st.set_page_config(page_title="Pocket Coach", page_icon="🤖")
st.title("Pocket Coach 🤖")

# ---------------------------------------------------------------------------
# TODO (CP1): import generate from ai, add a text input + Send button,
#             call generate() with the input, and st.write the reply.
#             See README for the snippet if you're stuck.
# ---------------------------------------------------------------------------

st.info(
    "Hello, world! Your starter is running. "
    "Open this file and look for `# TODO (CP1)` to begin."
)

# ---------------------------------------------------------------------------
# TODO (CP2): replace the hello-world above with a setup wizard that asks
#             for goals on first run and saves them via db.save_goals().
#             On reruns, show "Welcome back" with the saved persona.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# TODO (CP3): add a "How was today?" text area and a "Check in" button that
#             calls generate() with a goal-aware prompt and saves a row to
#             daily_logs + prompt_runs.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# TODO (CP4): replace the single prompt above with prompts.run_daily_chain()
#             and add a "🔍 See what Gemma saw" sidebar page that lists
#             rows from prompt_runs.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# TODO (CP5): pick ONE polish — streak counter, persona swap, edit-goals
#             page, or your own tweak. Then commit and push to your fork.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Extra mile (stretch — only if you finish CP5 early):
#             Use Open Design (https://github.com/nexu-io/open-design) to
#             generate a v2 mock for your app and commit it to docs/v2-vision.md.
#             See the README's "Extra mile" section.
# ---------------------------------------------------------------------------
