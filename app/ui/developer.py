import streamlit as st
from typing import Any


def show_debug_info(
    chat_context: dict[str, Any] | None,
    model: str,
    latency: float,
    tool_calls: list[dict[str, Any]] | None = None
) -> None:
    """
    Display debug information in an expander.

    Args:
        chat_context: The context and chat history sent to the model
        model: The model used for the response
        latency: Time taken to generate response in seconds
        tool_calls: Automatic function calling history from Gemini
    """
    with st.expander("▼ Debug", expanded=False):
        st.markdown(f"**Model:** `{model}`")
        st.markdown(f"**Latency:** `{latency:.2f} sec`")

        if chat_context:
            with st.expander("Context Sent to Model", expanded=False):
                st.json(chat_context)

        if tool_calls:
            st.markdown("**Gemini Automatic Function Calling:**")
            for index, call in enumerate(tool_calls, start=1):
                if not isinstance(call, dict):
                    continue

                role = call.get("role") or "unknown"
                parts = call.get("parts") or []

                for part in parts:
                    if not isinstance(part, dict):
                        continue

                    part_type = part.get("type", "part")
                    label = part.get("name") or part.get("text") or part_type
                    st.markdown(f"{index}. {role} -> `{part_type}`: `{label}`")

                    if part_type == "function_call" and part.get("args"):
                        with st.expander(f"Function call args: {label}", expanded=False):
                            st.json(part["args"])
                    elif part_type == "function_response" and part.get("response"):
                        with st.expander(f"Function response: {label}", expanded=False):
                            st.json(part["response"])
