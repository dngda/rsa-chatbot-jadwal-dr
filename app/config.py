from typing import Any

import streamlit as st
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    rsa_api_base_url: str = "https://api.rsa.example.com"
    gemini_api_key: str = "YOUR_GEMINI_API_KEY"
    app_title: str = "RSA Chatbot Jadwal Dokter"
    max_tool_iterations: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()


def _get_secret_value(key: str) -> Any:
    try:
        return st.secrets.get(key)
    except Exception:
        return None


def get_gemini_api_key() -> str:
    secret_value = _get_secret_value("GEMINI_API_KEY")
    if isinstance(secret_value, str) and secret_value.strip():
        return secret_value.strip()

    return settings.gemini_api_key


def get_rsa_api_base_url() -> str:
    secret_value = _get_secret_value("RSA_API_BASE_URL")
    if isinstance(secret_value, str) and secret_value.strip():
        return secret_value.strip()

    return settings.rsa_api_base_url