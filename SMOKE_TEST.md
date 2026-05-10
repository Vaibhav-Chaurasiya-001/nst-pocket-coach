# Workshop Smoke Test

Run this end-to-end at least 2 days before any cohort. About 15 minutes.
Repeat with **both** backends (Google AI Studio and Ollama).

## Setup

```bash
git clone https://github.com/ashwin-tewary/nst-pocket-coach.git /tmp/smoketest
cd /tmp/smoketest
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Run unit tests

```bash
pytest -v
```

**Expected:** `15 passed` across `test_db.py`, `test_ai.py`, `test_prompts.py`.

## Backend A — Google AI Studio

```bash
echo "GOOGLE_API_KEY=<your-test-key>" > .env
cp solutions/CP1/app.py app.py
streamlit run app.py
```

Open the browser. Type "hi". Expect a Gemini reply within ~3 seconds.

## Backend B — Ollama

```bash
rm .env
ollama pull gemma4:e2b   # if not already
streamlit run app.py
```

Type "hi". Expect a reply within ~10 seconds (slower but offline).

## Each checkpoint, end-to-end

For CP in {2, 3, 4, 5}:

```bash
rm -f data/coach.db
cp solutions/CP$CP/app.py app.py
streamlit run app.py
```

For each checkpoint, verify:

- **CP2:** refresh the page → goals persist
- **CP3:** check-in → reply on screen → row in `data/coach.db` `daily_logs` table
- **CP4:** one check-in produces 3 rows in `prompt_runs`; the "See what Gemma saw" page reads them
- **CP5:** streak counter shows N days; persona change visibly affects reply tone; sidebar nav routes to all 3 pages

## Cleanup

```bash
rm -rf /tmp/smoketest
```

If anything fails, file an issue on the repo and fix before the workshop.
