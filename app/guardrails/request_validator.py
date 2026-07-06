from enum import Enum

from app.conversation.conversation_state import PendingRequest
from app.conversation.conversation_manager import is_complete


class ValidationResult(Enum):
    VALID = "valid"
    MISSING_INFORMATION = "missing_information"


def validate_request(pending_request: PendingRequest | None) -> ValidationResult:
    if pending_request is None:
        return ValidationResult.MISSING_INFORMATION

    if is_complete(pending_request):
        return ValidationResult.VALID

    return ValidationResult.MISSING_INFORMATION