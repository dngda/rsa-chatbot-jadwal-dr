from dataclasses import replace
from datetime import datetime
import re

from app.conversation.conversation_state import PendingRequest
from app.utils.query_normalizer import SPECIALTY_ALIASES

DATE_WORDS = (
    "hari ini",
    "besok",
    "lusa",
    "senin",
    "selasa",
    "rabu",
    "kamis",
    "jumat",
    "sabtu",
    "minggu",
)

MONTHS = {
    "januari": 1,
    "februari": 2,
    "maret": 3,
    "april": 4,
    "mei": 5,
    "juni": 6,
    "juli": 7,
    "agustus": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "desember": 12,
}

SCHEDULE_HINTS = (
    "jadwal",
    "praktik",
    "praktek",
)

DOCTOR_HINTS = (
    r"\bdr\.?\s+([a-z][a-z.'-]*(?:\s+[a-z][a-z.'-]*)*)",
    r"\bdokter\s+([a-z][a-z.'-]*(?:\s+[a-z][a-z.'-]*)*)",
    r"\bprof\.?\s+([a-z][a-z.'-]*(?:\s+[a-z][a-z.'-]*)*)",
    r"\bprofesor\s+([a-z][a-z.'-]*(?:\s+[a-z][a-z.'-]*)*)",
)

CLINIC_HINTS = (
    r"\bklinik\s+([a-z][a-z0-9.'-]*(?:\s+[a-z0-9.'-]*)*)",
    r"\bpoli\s+([a-z][a-z0-9.'-]*(?:\s+[a-z0-9.'-]*)*)",
)

DOCTOR_PREFIXES = {
    "dr",
    "dokter",
    "prof",
    "profesor",
    "sp",
    "spa",
    "spa.",
    "spog",
    "sp.og",
    "spog.",
    "spm",
    "sp.m",
}

NON_DOCTOR_START_WORDS = {
    *SPECIALTY_ALIASES.keys(),
    "lain",
    "pada",
    "tanggal",
    "hari",
    "ini",
    "besok",
    "lusa",
}


def _normalize_text(message: str) -> str:
    normalized = message.lower().strip()
    normalized = re.sub(r"[.,;:!?]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _format_iso_date(day: int, month_name: str, year: int | None = None) -> str | None:
    month = MONTHS.get(month_name)
    if month is None:
        return None

    resolved_year = year or datetime.now().year

    try:
        return datetime(resolved_year, month, day).strftime("%Y-%m-%d")
    except ValueError:
        return None


def _extract_date(message: str) -> str | None:
    normalized = _normalize_text(message)

    explicit_date_pattern = re.compile(
        r"(?:tanggal\s+)?(?P<day>\d{1,2})\s+"
        r"(?P<month>januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)"
        r"(?:\s+(?P<year>\d{4}))?"
    )

    match = explicit_date_pattern.search(normalized)
    if match:
        day = int(match.group("day"))
        month = match.group("month")
        year = int(match.group("year")) if match.group("year") else None
        iso_date = _format_iso_date(day, month, year)
        if iso_date:
            return iso_date

    for date_word in DATE_WORDS:
        if re.search(rf"(?<!\w){re.escape(date_word)}(?!\w)", normalized):
            return date_word

    return None


def _extract_specialty(message: str) -> str | None:
    normalized = _normalize_text(message)

    for canonical, aliases in SPECIALTY_ALIASES.items():
        candidates = (canonical, *aliases)

        for candidate in candidates:
            if re.search(rf"(?<!\w){re.escape(candidate)}(?!\w)", normalized):
                return canonical

    return None


def _clean_name(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\b(pada|tanggal|untuk|di|ke)\b.*$", "", value)
    value = re.sub(r"\b(hari ini|besok|lusa|senin|selasa|rabu|kamis|jumat|sabtu|minggu)\b.*$", "", value)
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" .,-")

    tokens = value.split()
    while tokens:
        first_token = tokens[0].strip(" .,-")
        if first_token not in DOCTOR_PREFIXES:
            break
        tokens.pop(0)

    return " ".join(tokens).strip(" .,-")


def _extract_doctor(message: str) -> str | None:
    normalized = _normalize_text(message)

    for pattern in DOCTOR_HINTS:
        match = re.search(pattern, normalized)
        if match:
            doctor = _clean_name(match.group(1))
            if doctor:
                first_token = doctor.split()[0]
                if first_token in NON_DOCTOR_START_WORDS:
                    continue

                return doctor

    return None


def _extract_clinic(message: str) -> str | None:
    normalized = _normalize_text(message)

    for pattern in CLINIC_HINTS:
        match = re.search(pattern, normalized)
        if match:
            clinic = _clean_name(match.group(1))
            if clinic:
                return clinic

    return None


def _has_schedule_hint(message: str) -> bool:
    normalized = _normalize_text(message)

    return any(
        re.search(rf"(?<!\w){re.escape(hint)}(?!\w)", normalized)
        for hint in SCHEDULE_HINTS
    )


def _extract_pending_request(message: str) -> PendingRequest:
    doctor = _extract_doctor(message)
    clinic = _extract_clinic(message)
    specialty = _extract_specialty(message)
    date = _extract_date(message)

    intent = "schedule" if _has_schedule_hint(message) or any((doctor, clinic, specialty, date)) else None

    return PendingRequest(
        intent=intent,
        doctor=doctor,
        clinic=clinic,
        specialty=specialty,
        date=date,
    )


def is_schedule_related_message(message: str) -> bool:
    return any(
        (
            _has_schedule_hint(message),
            _extract_date(message) is not None,
            _extract_specialty(message) is not None,
            _extract_doctor(message) is not None,
            _extract_clinic(message) is not None,
        )
    )


def message_mentions_subject(message: str) -> bool:
    return any(
        (
            _extract_doctor(message) is not None,
            _extract_clinic(message) is not None,
            _extract_specialty(message) is not None,
        )
    )


def start_pending_request(message: str) -> PendingRequest:
    return _extract_pending_request(message)


def merge_pending_request(pending: PendingRequest, message: str) -> PendingRequest:
    extracted = _extract_pending_request(message)
    merged = replace(pending)

    if extracted.intent and not merged.intent:
        merged.intent = extracted.intent

    if extracted.doctor:
        merged.doctor = extracted.doctor

    if extracted.clinic:
        merged.clinic = extracted.clinic

    if extracted.specialty:
        merged.specialty = extracted.specialty

    if extracted.date:
        merged.date = extracted.date

    if merged.intent is None and any((merged.doctor, merged.clinic, merged.specialty, merged.date)):
        merged.intent = "schedule"

    return merged


def is_complete(pending: PendingRequest) -> bool:
    if pending.doctor:
        return pending.intent == "schedule"

    has_subject = any((pending.clinic, pending.specialty))

    return pending.intent == "schedule" and has_subject and bool(pending.date)


def build_final_prompt(pending: PendingRequest) -> str:
    subject = "dokter"

    if pending.doctor:
        subject = f"dokter {pending.doctor}"
    elif pending.clinic:
        subject = f"klinik {pending.clinic}"
    elif pending.specialty:
        subject = f"dokter {pending.specialty}"

    prompt_parts = ["jadwal", subject]

    if pending.date:
        prompt_parts.append(pending.date)

    return " ".join(prompt_parts).strip()


def next_clarification_question(pending: PendingRequest) -> str:
    if pending.doctor:
        return ""

    if not any((pending.clinic, pending.specialty)):
        return "Dokter atau klinik apa yang ingin Anda cari?"

    if not pending.date:
        return "Hari apa yang ingin dicari?"

    return "Informasi yang diminta belum lengkap."