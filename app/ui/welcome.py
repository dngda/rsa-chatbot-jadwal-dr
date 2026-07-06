import streamlit as st


def show_welcome_screen() -> None:
    """Display welcome screen when chat history is empty."""

    st.markdown(
        """
        ### Halo, selamat datang di chatbot jadwal dokter RS Akademik UGM 👋

        Saya dapat membantu mencari:

        • Jadwal dokter
        • Dokter spesialis
        • Klinik
        • Jadwal praktik berikutnya

        #### Contoh:

        *"Dokter Endy praktik kapan?"*

        *"Dokter anak hari ini"*

        *"Besok ada dokter THT?"*

        *"klinik apa aja di RS Akademik UGM?"*
        """
    )


def show_suggested_prompts() -> str | None:
    """Display suggested prompts and return the selected one if clicked."""
    st.divider()
    st.markdown("**Atau coba pertanyaan berikut:**")

    cols = st.columns(3)
    suggestions = ["Jadwal dokter hari ini", "Jadwal dokter anak hari ini", "Jadwal dokter THT besok", "Jadwal dokter mata besok", "Jadwal dokter besok", "Jadwal klinik kandungan terdekat"]
    selected_prompt = None

    for i, suggestion in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(suggestion, key=f"prompt_{i}", use_container_width=True):
                selected_prompt = suggestion

    return selected_prompt
