import re
from dataclasses import dataclass

SPECIALTY_ALIASES: dict[str, tuple[str, ...]] = {
    "anak": (
        "pediatrics",
        "spesialis anak",
        "klinik anak",
        "poli anak",
        "spa",
        "sp.a",
        "sp a",
    ),
    "obsgin": (
        "kandungan",
        "obgyn",
        "obgin",
        "obsgyn",
        "spog",
        "sp.og",
        "sp og",
    ),
    "mata": (
        "optometry",
        "spesialis mata",
        "klinik mata",
        "poli mata",
        "spm",
        "sp.m",
    ),
    "tht": (
        "telinga hidung tenggorokan",
        "tht-kl",
        "tht kl",
        "klinik tht",
        "poli tht",
    ),
    "saraf": (
        "neurologi",
        "spesialis saraf",
    ),
    "jantung": (
        "kardiologi",
        "spesialis jantung",
    ),
    "kulit": (
        "spesialis kulit",
    ),
    "bedah": (
        "spesialis bedah",
    ),
}


@dataclass(slots=True)
class QueryNormalization:
    original: str
    normalized: str
    fallback: str | None = None


def sanitize_query(query: str) -> str:
    query = query.lower()
    query = re.sub(r"[.,]", " ", query)
    query = re.sub(r"\s+", " ", query)

    return query.strip()

def replace_specialty_tokens(query: str) -> str:
    normalized = query

    for canonical, aliases in SPECIALTY_ALIASES.items():
        for alias in sorted(aliases, key=len, reverse=True):
            pattern = rf"\b{re.escape(alias)}\b"
            normalized = re.sub(pattern, canonical, normalized)

    return re.sub(r"\s+", " ", normalized).strip()

def normalize_query(query: str) -> str:
    return normalize_query_with_fallback(query).normalized


def normalize_query_with_fallback(query: str) -> QueryNormalization:
    original = query
    normalized = sanitize_query(query)
    normalized = replace_specialty_tokens(normalized)

    normalized = re.sub(r"\bdr\b\.?", "", normalized)
    normalized = re.sub(r"\bdokter\b", "", normalized)

    normalized = re.sub(r"\s+", " ", normalized)

    normalized = normalized.strip()

    fallback = None

    for canonical in SPECIALTY_ALIASES:
        if re.search(rf"(?<!\w){re.escape(canonical)}(?!\w)", normalized):
            fallback = canonical
            break

    if fallback is None:
        if normalized.startswith("klinik "):
            fallback = normalized.replace("klinik ", "", 1).strip() or None
        elif normalized.startswith("poli "):
            fallback = normalized.replace("poli ", "", 1).strip() or None

    return QueryNormalization(
        original=original,
        normalized=normalized,
        fallback=fallback,
    )