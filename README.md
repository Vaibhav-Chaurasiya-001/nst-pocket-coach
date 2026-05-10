<p align="center">
  <img src="https://www.tribuneindia.com/sortd-service/imaginary/v22-01/jpg/large/high?url=dGhldHJpYnVuZS1zb3J0ZC1wcm8tcHJvZC1zb3J0ZC9tZWRpYWVkNmQxYzUwLTE1M2ItMTFmMC05YzRkLWExYjFjMjMzZTcyMi5qcGc=" alt="Newton School of Technology" width="640">
</p>

<h1 align="center">Pocket Coach</h1>

<p align="center">
  <em>A 2-hour AI workshop by <a href="https://newtonschool.tech">Newton School of Technology</a></em><br>
  Build a real AI lifestyle coach that runs on your laptop — Streamlit + SQLite + Google AI.
</p>

<p align="center">
  <a href="#quick-start-do-this-now"><img src="https://img.shields.io/badge/start%20here-Quick%20start-225CDB" alt="Quick start"></a>
  <a href="#license"><img src="https://img.shields.io/badge/license-MIT-0D8C59" alt="MIT licensed"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-737380" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B" alt="Streamlit">
</p>

---

## What you'll build

A working AI app on **your** laptop that:

- 📋 Remembers your personal lifestyle goals (exercise, study, books)
- 💬 Lets you check in daily about how things went
- 🔗 Runs a 3-step prompt chain (extract mood → evaluate progress → encourage) backed by SQLite memory
- 🎭 Replies in a coaching persona you pick (`supportive`, `drill_sergeant`, `philosopher`, `hype_friend`)
- 🌐 Pushes to your own GitHub fork — yours forever

By the end you'll have touched every layer of an AI product: **frontend, backend, database, prompt chain, deployment**.

---

## Quick start (do this NOW)

You need **Python 3.10+** and **Git**.

```bash
git clone https://github.com/YOUR-USERNAME/nst-pocket-coach.git
cd nst-pocket-coach

# Recommended: virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Open .env and fill in ONE backend (see next section)

streamlit run app.py
```

A browser tab opens with **"Hello, world!"** — you're ready.

---

## Pick ONE LLM backend

### Option A — Google AI Studio (recommended for laptops under 12GB RAM)

1. Go to <https://aistudio.google.com/apikey>
2. Click **"Get API key" → "Create API key in new project"** (no credit card needed)
3. Copy the key
4. In `.env`:
   ```
   GOOGLE_API_KEY=paste-your-key-here
   ```

That's it. The app will use **Gemini 2.5 Flash** via Google's free tier.

> **Why not Gemma 4 on the cloud path?** As of May 2026, Gemma 4 isn't yet stable on Google AI Studio's free tier (returns 500 INTERNAL). Gemini 2.5 Flash is the same Google AI family and works reliably. Once Gemma 4 stabilises on free tier, set `GOOGLE_MODEL=gemma-4-26b-a4b-it` in `.env`.

### Option B — Local Ollama (best on 12GB+ RAM laptops, fully offline)

1. Install Ollama: <https://ollama.com/download>
2. Pull the Gemma 4 model:
   ```bash
   ollama pull gemma4:e2b   # ~7 GB download — do this on home Wi-Fi
   ```
3. Make sure Ollama is running (it auto-starts after install)
4. Leave `GOOGLE_API_KEY` blank in `.env`. The app uses Ollama automatically.

---

## Workshop structure — 5 checkpoints

You'll work through five checkpoints. **Each is a working app** — fall behind, you still ship something.

| # | Goal | What you add |
|---|---|---|
| **CP1** | Make Gemma reply on screen | A text input + button + `generate()` call |
| **CP2** | Persist your goals to a database | First-run setup wizard + SQLite save/load |
| **CP3** | Personalised daily check-in | A goal-aware single-prompt encouragement |
| **CP4** | 3-step prompt chain that uses your past entries | `prompts.run_daily_chain()` + a "See what Gemma saw" page |
| **CP5** | Polish, push, demo | Pick one polish (streak counter, persona swap…) → `git push` → demo to a neighbour |

Each step in `app.py` is marked `# TODO (CPn)`.

### 🌟 Extra mile (stretch — only if you finish CP5 early)

Use [Open Design](https://github.com/nexu-io/open-design) (the open-source AI design tool) to generate a v2 mockup of your app and drop the resulting HTML into `docs/`. Write your design brief in `docs/v2-vision.md` (template included). This is the bridge from "Streamlit MVP" to "real product" — it's optional and showcases what's possible when AI joins the design process too.

---

## Falling behind? Use the catch-up snippets

Each checkpoint has a complete reference in `solutions/CPn/app.py`. To leap to the start of any checkpoint:

```bash
cp solutions/CP3/app.py app.py    # example: jump to CP3
```

Then keep going from there.

---

## Run the tests (optional but cool)

We've included **15 pytest tests** for `db.py`, `ai.py`, and `prompts.py` so you can see how testable modules look:

```bash
pip install -r requirements-dev.txt
pytest -v
```

Expect: `15 passed`. The tests don't require Google AI or Ollama installed — they mock the LLM call.

---

## File map

```
app.py            ← what you edit during the workshop
db.py             ← SQLite layer (read it, don't change it)
ai.py             ← LLM backend selector (read it, don't change it)
prompts.py        ← Prompt templates + the daily chain
tests/            ← 15 pytest tests for the three modules above
solutions/        ← reference solution per checkpoint (CP1–CP4 + CP5)
data/             ← your coach.db lives here at runtime (gitignored)
docs/             ← v2-vision.md template for the Extra mile section
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `streamlit: command not found` | Activate your venv: `source .venv/bin/activate` |
| Connection refused on Ollama | Start it manually: `ollama serve` in another terminal |
| Google AI returns 403 / 429 | Free-tier rate limit — switch to Ollama, or wait a minute |
| Windows `pip install` fails on `ollama` | Skip it if using Google AI: `pip install streamlit google-genai python-dotenv` |
| `coach.db` won't open | Delete `data/coach.db` and rerun — the app recreates it |
| Tests fail with `ModuleNotFoundError: db` | You're running from the wrong dir. `cd` into the repo root, then `pytest -v` |

---

## After the workshop

This repo is **yours**. Some directions:

- 🎙 **Multimodal** — Gemma 4 has audio + vision; point your phone camera at your run, get praise
- 🌐 **Deploy** — [Hugging Face Spaces](https://huggingface.co/spaces) free tier hosts Streamlit apps in 5 minutes
- ⚛ **Replace Streamlit** with React + FastAPI; use the v2 design you generated as the brief
- 📅 **Calendar integration** — auto-tag check-ins with what was on your calendar that day
- 🧪 **Add evals** — write a few test conversations and assert the coach reply quality with another LLM call

> File a GitHub issue on this repo if you get stuck after the workshop. Pull requests welcome.

---

## License

MIT — see [LICENSE](LICENSE). Copyright © 2026 Newton School of Technology.

You're free to fork, modify, deploy, and use this project for any purpose, commercial or otherwise. The branding (logo, "Newton School of Technology" name) is **not** licensed under MIT — please don't reuse it for unrelated workshops.

---

<p align="center">
  Built with care for <a href="https://newtonschool.tech">Newton School of Technology</a> · Powered by Streamlit, SQLite, and Google AI · 2026
</p>
