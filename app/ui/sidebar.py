import streamlit as st
from typing import Any


def render_sidebar() -> dict[str, Any]:
    """
    Render sidebar with settings and controls.

    Returns:
        Dictionary containing sidebar settings
    """
    with st.sidebar:
        st.markdown("## 🏥 Jadwal Dokter Chatbot")
        st.caption("AI Assistant Jadwal Dokter RS Akademik UGM")

        st.markdown("### Model")
        model = st.selectbox(
            "Pilih model Gemini:",
            options=[
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite",
                "gemini-2.5-pro",
                "gemini-3.1-flash-lite",
                "gemini-3.5-flash",
                ],
            index=3,
            label_visibility="collapsed",
            key="model_select",
        )

        st.markdown("### Gemini API Key")
        gemini_api_key = st.text_input(
            "Gunakan API key sendiri jika quota default habis:",
            type="password",
            value=st.session_state.get("gemini_api_key", ""),
            placeholder="AQ.*********************",
            help="Jika diisi, aplikasi akan memakai key ini untuk Gemini. Jika kosong, key dari environment tetap dipakai.",
            label_visibility="collapsed",
            key="gemini_api_key",
        )

        st.caption("Kosongkan untuk tetap memakai konfigurasi dari environment.")

        st.markdown("### Temperature")
        temperature = st.slider(
            "Kreativitas respon (0.0 - 2.0):",
            min_value=0.0,
            max_value=2.0,
            value=0.2,
            step=0.1,
            label_visibility="collapsed",
            key="temperature_slider",
        )

        st.markdown("### Max Output Tokens")
        max_tokens = st.slider(
            "Panjang maksimal respon:",
            min_value=512,
            max_value=8192,
            value=2048,
            step=256,
            label_visibility="collapsed",
            key="max_tokens_slider",
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            new_chat = st.button(
                "🗑 New Chat",
                use_container_width=True,
                key="new_chat_btn",
            )

        st.divider()

        st.markdown("### Developer Mode")
        developer_mode = st.checkbox(
            "Aktifkan Developer Mode",
            value=st.session_state.developer_mode,
            key="developer_mode",
        )

        if developer_mode:
            st.markdown("#### Debug Options")
            show_tool_calls = st.checkbox(
                "Show Tool Calls",
                value=st.session_state.show_tool_calls,
                key="show_tool_calls",
            )
            show_latency = st.checkbox(
                "Show Latency",
                value=st.session_state.show_latency,
                key="show_latency",
            )
        else:
            show_tool_calls = st.session_state.show_tool_calls
            show_latency = st.session_state.show_latency

        st.markdown(
            """
            <div style="
                text-align: center;
                font-size: 0.8em;
                color: gray;
                margin-top: 50px;
            ">
            RSA UGM<br/>
            Powered by<br/>
            <strong>Gemini</strong> • <strong>Streamlit</strong> • <strong>Python</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return {
            "model": model,
            "gemini_api_key": gemini_api_key,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "new_chat": new_chat,
            "developer_mode": developer_mode,
            "show_tool_calls": show_tool_calls,
            "show_latency": show_latency,
        }
