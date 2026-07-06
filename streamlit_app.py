import streamlit as st
import logging
import time

from app.agent.chatbot import Chatbot
from app.ui.sidebar import render_sidebar
from app.ui.chat import (
    display_chat_history,
    get_chat_input,
    show_typing_indicator,
    display_user_message,
    show_toast,
)
from app.ui.welcome import show_welcome_screen, show_suggested_prompts
from app.ui.developer import show_debug_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _is_quota_error(error: Exception) -> bool:
    error_text = str(error).lower()

    return any(
        hint in error_text
        for hint in (
            "429",
            "quota",
            "resource exhausted",
            "too many requests",
        )
    )

st.set_page_config(
    page_title="RSA Jadwal Dokter Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "chatbot" not in st.session_state:
    st.session_state.chatbot = Chatbot(st.session_state.get("gemini_api_key", ""))

if "messages" not in st.session_state:
    st.session_state.messages = []

if "model" not in st.session_state:
    st.session_state.model = "gemini-2.5-flash"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.2

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 2048

if "developer_mode" not in st.session_state:
    st.session_state.developer_mode = False

if "show_tool_calls" not in st.session_state:
    st.session_state.show_tool_calls = True

if "show_latency" not in st.session_state:
    st.session_state.show_latency = True

def reset_chat() -> None:
    """Reset chat session and clear history."""
    st.session_state.chatbot.reset_chat_session()
    st.session_state.messages = []
    show_toast("Percakapan baru dimulai", "🗑")


def handle_model_change(new_model: str) -> None:
    """Handle model change with toast notification."""
    if new_model != st.session_state.model:
        st.session_state.model = new_model
        st.session_state.chatbot.reset_chat_session()
        show_toast(f"Model diganti ke {new_model}", "🔄")


def handle_api_key_change(new_api_key: str) -> None:
    if new_api_key != st.session_state.get("gemini_api_key_last_applied", ""):
        st.session_state.chatbot.set_api_key(new_api_key)
        st.session_state.gemini_api_key_last_applied = new_api_key
        show_toast("Konfigurasi Gemini diperbarui", "🔑")


def send_message_to_chatbot(user_message: str) -> None:
    """
    Send message to chatbot and handle response.

    Args:
        user_message: The user's input message
    """

    st.session_state.messages.append({
        "role": "user",
        "content": user_message,
    })

    display_user_message(user_message)

    try:
        start_time = time.time()

        response_placeholder = show_typing_indicator("Memproses permintaan...")
        response = st.session_state.chatbot.chat(
            user_message,
            st.session_state.model,
        )
        response_placeholder.markdown(response)

        latency = time.time() - start_time

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
        })

        if st.session_state.get("developer_mode", False) and not st.session_state.chatbot.last_turn_was_clarification:
            show_debug_info(
                chat_context=st.session_state.chatbot.last_chat_context,
                model=st.session_state.model,
                latency=latency,
                tool_calls=(
                    st.session_state.chatbot.last_automatic_function_calling_history
                    if st.session_state.get("show_tool_calls", True)
                    else None
                ),
            )

        if not st.session_state.chatbot.last_turn_was_clarification:
            show_toast("Jadwal berhasil ditemukan", "✅")

    except Exception as e:
        logger.error(f"Error sending message to chatbot: {e}")

        if _is_quota_error(e):
            st.error(
                "Kuota Gemini habis atau request ditolak. Coba ganti model lain atau isi Gemini API Key sendiri di sidebar, atau tunggu quota tersedia kembali."
            )
        else:
            st.error(f"Terjadi kesalahan: {str(e)}")

def main() -> None:
    """Main application entry point."""

    sidebar_settings = render_sidebar()

    handle_api_key_change(sidebar_settings["gemini_api_key"])

    if sidebar_settings["new_chat"]:
        reset_chat()
        st.rerun()

    handle_model_change(sidebar_settings["model"])

    st.markdown("## 🏥 RSA UGM Doctor Schedule Assistant")
    st.caption("Cari jadwal dokter, spesialis, ataupun klinik menggunakan AI.")
    st.divider()

    if not st.session_state.messages:
        show_welcome_screen()
        suggested = show_suggested_prompts()
        if suggested:
            send_message_to_chatbot(suggested)
    else:
        display_chat_history(st.session_state.messages)

    user_input = get_chat_input()
    if user_input:
        send_message_to_chatbot(user_input)

if __name__ == "__main__":
    main()
