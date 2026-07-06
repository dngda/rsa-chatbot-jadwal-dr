import streamlit as st
from typing import Any, Optional


def display_chat_history(messages: list[dict[str, str]]) -> None:
    """
    Display chat history using Streamlit chat messages.

    Args:
        messages: List of message dicts with 'role' and 'content' keys
    """
    for message in messages:
        role = message.get("role")
        content = message.get("content")

        if role == "user":
            with st.chat_message("user", avatar="🙂"):
                st.markdown(content)
        elif role == "assistant":
            with st.chat_message("assistant", avatar="🏥"):
                st.markdown(content)


def get_chat_input() -> Optional[str]:
    """
    Get user input from chat input field.

    Returns:
        User input string or None if no input
    """
    return st.chat_input("Tanya jadwal dokter atau klinik...")


def show_typing_indicator(message: str = "Sedang mencari jadwal dokter...") -> Any:
    """
    Show a typing indicator inside a fresh assistant bubble.

    Args:
        message: Message to display

    Returns:
        Placeholder that can be updated with the final assistant response
    """
    bubble = st.chat_message("assistant", avatar="🏥")
    placeholder = bubble.empty()
    placeholder.markdown(message)
    return placeholder


def display_assistant_message(content: str) -> None:
    """
    Display assistant message in chat.

    Args:
        content: Message content to display
    """
    with st.chat_message("assistant", avatar="🏥"):
        st.markdown(content)


def display_user_message(content: str) -> None:
    """
    Display user message in chat.

    Args:
        content: Message content to display
    """
    with st.chat_message("user", avatar="🙂"):
        st.markdown(content)


def show_toast(message: str, icon: str = "ℹ️") -> None:
    """
    Show a toast notification.

    Args:
        message: Toast message
        icon: Icon/emoji for the toast
    """
    st.toast(f"{icon} {message}")
