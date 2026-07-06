import logging
from typing import Any
from dataclasses import replace

from google.genai import types

from app.conversation.conversation_state import PendingRequest
from app.conversation.conversation_manager import (
    build_final_prompt,
    is_complete,
    is_schedule_related_message,
    merge_pending_request,
    message_mentions_subject,
    next_clarification_question,
    start_pending_request,
)
from app.gemini import get_client
from app.agent.prompts import SYSTEM_PROMPT
from app.guardrails.request_validator import ValidationResult, validate_request
from app.tools.rsa_tools import RSA_TOOLS
from app.tools.date_helpers import get_current_date_info

logger = logging.getLogger(__name__)

class Chatbot:
    def __init__(self, api_key: str | None = None):
        self.client = get_client(api_key)
        self.current_model: str | None = None
        self.pending_request: PendingRequest | None = None
        self.last_completed_request: PendingRequest | None = None
        self.chat_session = None
        self.last_response: Any | None = None
        self.last_chat_context: dict[str, Any] | None = None
        self.last_automatic_function_calling_history: list[dict[str, Any]] = []
        self.last_turn_was_clarification = False
        self.config = types.GenerateContentConfig()
        self.config.system_instruction = SYSTEM_PROMPT
        self.config.tools = RSA_TOOLS + [get_current_date_info]

    def set_api_key(self, api_key: str | None) -> None:
        resolved_api_key = (api_key or "").strip() or None

        self.client = get_client(resolved_api_key)
        self.chat_session = None
        self.current_model = None
        self.last_response = None
        self.last_chat_context = None
        self.last_automatic_function_calling_history = []

    def has_pending_request(self) -> bool:
        return self.pending_request is not None

    def _ensure_chat_session(self, model: str) -> None:
        if self.chat_session is None or self.current_model != model:
            logger.info("Creating new chat session with model: %s", model)
            self.chat_session = self.client.chats.create(
                model=model,
                config=self.config,
            )
            self.current_model = model

    def reset_chat_session(self) -> None:
        logger.info("Resetting chat session.")
        self.chat_session: Any | None = None
        self.current_model = None
        self.pending_request = None
        self.last_completed_request = None
        self.last_response = None
        self.last_chat_context = None
        self.last_automatic_function_calling_history = []
        self.last_turn_was_clarification = False

    def _serialize_content(self, content: Any) -> dict[str, Any]:
        if hasattr(content, "model_dump"):
            return content.model_dump(mode="json", exclude_none=True)

        if isinstance(content, dict):
            return content

        return {"value": str(content)}

    def _tool_metadata(self) -> list[dict[str, Any]]:
        tools: list[Any] = RSA_TOOLS + [get_current_date_info]
        metadata: list[dict[str, Any]] = []

        for tool in tools:
            metadata.append(
                {
                    "name": getattr(tool, "__name__", "unknown"),
                    "description": (getattr(tool, "__doc__", "") or "").strip(),
                }
            )

        return metadata

    def _build_chat_context(self, message: str) -> dict[str, Any]:
        curated_history: list[dict[str, Any]] = []

        if self.chat_session and hasattr(self.chat_session, "get_history"):
            curated_history = [
                self._serialize_content(content)
                for content in self.chat_session.get_history(curated=True)
            ]

        return {
            "system_instruction": SYSTEM_PROMPT,
            "model": self.current_model,
            "input_message": message,
            "curated_history": curated_history,
            "tools": self._tool_metadata(),
        }

    def _extract_automatic_function_calling_history(
        self,
        response: Any,
    ) -> list[dict[str, Any]]:
        history: list[dict[str, Any]] = []
        response_history = getattr(response, "automatic_function_calling_history", None) or []

        for content in response_history:
            content_entry: dict[str, Any] = {
                "role": getattr(content, "role", None),
                "parts": [],
            }

            for part in getattr(content, "parts", None) or []:
                part_entry: dict[str, Any] = {}

                function_call = getattr(part, "function_call", None)
                function_response = getattr(part, "function_response", None)
                text = getattr(part, "text", None)

                if function_call is not None:
                    part_entry = {
                        "type": "function_call",
                        "id": getattr(function_call, "id", None),
                        "name": getattr(function_call, "name", None),
                        "args": getattr(function_call, "args", None),
                    }
                elif function_response is not None:
                    part_entry = {
                        "type": "function_response",
                        "id": getattr(function_response, "id", None),
                        "name": getattr(function_response, "name", None),
                        "response": getattr(function_response, "response", None),
                    }
                elif text is not None:
                    part_entry = {
                        "type": "text",
                        "text": text,
                    }

                if part_entry:
                    content_entry["parts"].append(part_entry)

            if content_entry["parts"]:
                history.append(content_entry)

        return history

    def _send_message_to_model(self, message: str, model: str) -> str:
        self._ensure_chat_session(model)

        logger.debug("Sending message to model %s: %s", model, message)

        if not self.chat_session:
            raise RuntimeError("Chat session is not initialized.")

        self.last_chat_context = self._build_chat_context(message)
        response = self.chat_session.send_message(message)
        self.last_response = response
        self.last_automatic_function_calling_history = (
            self._extract_automatic_function_calling_history(response)
        )

        if response.text:
            return response.text.strip()

        raise RuntimeError("Model returned neither text nor a valid tool response.")

    def _can_reuse_last_completed_request(self, message: str) -> bool:
        if self.last_completed_request is None:
            return False

        if self.last_completed_request.doctor is None:
            return False

        return (
            is_schedule_related_message(message)
            and self.pending_request is None
            and not message_mentions_subject(message)
        )

    def chat(self, message: str, model: str) -> str:
        self.last_turn_was_clarification = False
        normalized_message = message.lower()

        if self.pending_request is None and not is_schedule_related_message(message):
            self.last_response = None
            self.last_automatic_function_calling_history = []
            self.last_chat_context = None
            self.pending_request = None
            return self._send_message_to_model(message, model)

        if self.pending_request is not None:
            incoming_request = merge_pending_request(self.pending_request, message)
        elif self._can_reuse_last_completed_request(message):
            last_completed_request = self.last_completed_request
            if last_completed_request is None:
                incoming_request = start_pending_request(message)
            else:
                incoming_request = merge_pending_request(last_completed_request, message)
        else:
            incoming_request = start_pending_request(message)

        self.pending_request = incoming_request

        validation = validate_request(incoming_request)

        if validation != ValidationResult.VALID:
            self.last_response = None
            self.last_chat_context = None
            self.last_automatic_function_calling_history = []
            self.last_turn_was_clarification = True
            return next_clarification_question(incoming_request)

        if not is_complete(incoming_request):
            self.last_response = None
            self.last_chat_context = None
            self.last_automatic_function_calling_history = []
            self.last_turn_was_clarification = True
            return next_clarification_question(incoming_request)

        final_prompt = build_final_prompt(incoming_request)

        if "terdekat" in normalized_message and "terdekat" not in final_prompt:
            final_prompt = f"{final_prompt} terdekat".strip()

        response_text = self._send_message_to_model(final_prompt, model)
        self.last_completed_request = replace(incoming_request)
        self.pending_request = None
        self.last_turn_was_clarification = False
        return response_text