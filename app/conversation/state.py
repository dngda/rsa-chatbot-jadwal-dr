from dataclasses import dataclass

from app.conversation.conversation_state import PendingRequest


@dataclass(slots=True)
class ConversationState:
    pending_request: PendingRequest | None = None