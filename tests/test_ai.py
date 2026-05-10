from unittest.mock import patch
import ai


def test_generate_uses_google_when_api_key_set(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    with patch("ai._generate_google", return_value="google reply") as mock_google, \
         patch("ai._generate_ollama") as mock_ollama:
        result = ai.generate("hello")
    assert result == "google reply"
    mock_google.assert_called_once_with("hello")
    mock_ollama.assert_not_called()


def test_generate_uses_ollama_when_no_api_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with patch("ai._generate_ollama", return_value="ollama reply") as mock_ollama, \
         patch("ai._generate_google") as mock_google:
        result = ai.generate("hello")
    assert result == "ollama reply"
    mock_ollama.assert_called_once_with("hello")
    mock_google.assert_not_called()


def test_generate_returns_string(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with patch("ai._generate_ollama", return_value="reply"):
        assert isinstance(ai.generate("anything"), str)
