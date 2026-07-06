from google import genai

from app.config import get_gemini_api_key


def get_client(api_key: str | None = None) -> genai.Client:
    resolved_api_key = (api_key or "").strip() or get_gemini_api_key()

    return genai.Client(
        api_key=resolved_api_key
    )