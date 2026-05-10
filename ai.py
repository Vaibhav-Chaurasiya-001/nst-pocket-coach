"""Single function `generate()` that routes to Google AI Studio or local Ollama.

Backend selection is by env var:
- GOOGLE_API_KEY set  -> Google AI Studio (default: gemini-2.5-flash)
- otherwise           -> local Ollama (default: gemma4:e2b)

The cloud default is Gemini 2.5 Flash because Gemma 4 is not yet reliably
available on Google AI Studio's free tier (returns 500 INTERNAL as of 2026-05).
Override with GOOGLE_MODEL env var when Gemma 4 becomes stable on free tier.
The local default stays Gemma 4 via Ollama.
"""
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")


def generate(prompt: str) -> str:
    """Send a prompt to the configured LLM backend and return the reply."""
    if os.getenv("GOOGLE_API_KEY"):
        return _generate_google(prompt)
    return _generate_ollama(prompt)


def _generate_google(prompt: str) -> str:
    """Call Google AI Studio with the prompt and return the text reply."""
    from google import genai
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    response = client.models.generate_content(
        model=GOOGLE_MODEL,
        contents=prompt,
    )
    return response.text


def _generate_ollama(prompt: str) -> str:
    """Call the local Ollama server with the prompt and return the text reply."""
    import ollama
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.message.content
