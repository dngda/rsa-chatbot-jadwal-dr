from dataclasses import dataclass


@dataclass(slots=True)
class PendingRequest:
    intent: str | None = None

    doctor: str | None = None
    clinic: str | None = None
    specialty: str | None = None
    date: str | None = None