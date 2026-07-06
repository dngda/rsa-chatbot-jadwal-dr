import re

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

def sanitize_query(query: str) -> str:
    query = query.lower()
    query = re.sub(r"[.,]", " ", query)
    query = re.sub(r"\s+", " ", query)

    return query.strip()

def normalize_query(query: str) -> str:
    normalized = sanitize_query(query)

    for canonical, aliases in SPECIALTY_ALIASES.items():

        if normalized == canonical:
            return canonical

        for alias in aliases:
            if alias == normalized:
                return canonical

    normalized = re.sub(r"\bdr\b\.?", "", normalized)
    normalized = re.sub(r"\bdokter\b", "", normalized)

    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()