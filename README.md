# RSA Chatbot Jadwal Dokter

Chatbot Streamlit untuk mencari jadwal dokter, klinik, dan spesialis di RSA UGM.

## Fitur

- Cari jadwal dokter berdasarkan nama dokter, spesialis, atau klinik
- Slot filling untuk percakapan lanjutan
- Dukungan input tanggal relatif dan tanggal eksplisit
- Opsi API key Gemini dari sidebar, dengan fallback ke environment

## Persyaratan

- Python 3.11+
- Akun dan API key Gemini

## Instalasi

```bash
pip install -r requirements.txt
```

Atau jika memakai `uv`/`pip` sesuai workflow proyek Anda.

## Konfigurasi

### Opsi 1: `secrets.toml` untuk Streamlit

Buat file `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
RSA_API_BASE_URL = "https://api.rsa.example.com"
```

### Opsi 2: environment variable

Kalau Anda tidak memakai `secrets.toml`, set `GEMINI_API_KEY` dan `RSA_API_BASE_URL` di environment atau file `.env`.

Jika key di sidebar dikosongkan, aplikasi akan memakai nilai dari `st.secrets` terlebih dulu, lalu fallback ke environment.

## Menjalankan Aplikasi

```bash
streamlit run streamlit_app.py
```

## Cara Pakai

Contoh input:

- `jadwal dokter besok`
- `anak`
- `dr Endy`
- `jadwal dokter mata lain pada tanggal 6 juli 2026`
- `jika besok`

Jika user hanya memberi sebagian informasi, chatbot akan melanjutkan percakapan untuk melengkapi request. Jika user menyebut dokter spesifik tanpa tanggal, chatbot akan langsung lanjut ke pencarian nearest schedule.

## Struktur Proyek

- `streamlit_app.py` - entry point UI Streamlit
- `app/agent/` - chatbot orchestration
- `app/conversation/` - state dan slot filling percakapan
- `app/guardrails/` - validasi request
- `app/tools/` - tool Gemini dan helper tanggal
- `app/ui/` - komponen UI Streamlit

## Catatan

Jika Gemini mengembalikan error 429 atau kuota habis, aplikasi akan menyarankan user untuk memakai Gemini API key sendiri dari sidebar.
