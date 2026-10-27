"""Deterministic turn handling and validation; no separate model request."""

import re

from jsonschema import validate

from rag.prompts.planning.conversation import CONVERSATION_SCHEMA

# Ask for an explicit command instead of guessing from a truncated conversation.
MAX_ROUTING_CHARS = 16000
NEW_PREFIX = re.compile(r"^(?:câu hỏi mới|new question)\s*:", re.IGNORECASE)
FOLLOW_UP_PREFIX = re.compile(
    r"^(?:bổ sung(?: thông tin)?|đính chính|additional information|correction)\s*:",
    re.IGNORECASE,
)


def explicit_turn(question: str, message: str, forced_action: str | None = None) -> dict | None:
    """Return a backend-owned decision, or None when semantic planning is needed."""
    if forced_action is not None and forced_action not in {"NEW_QUESTION", "FOLLOW_UP"}:
        raise ValueError("Invalid conversation override")
    if forced_action == "FOLLOW_UP" and not question:
        raise ValueError("A follow-up needs an active question")
    if forced_action or not question:
        return {
            "action": forced_action or "NEW_QUESTION",
            "method": "COMMAND" if forced_action else "FIRST_TURN",
            "elapsed_ms": 0.0,
        }
    if NEW_PREFIX.match(message) or FOLLOW_UP_PREFIX.match(message):
        return {
            "action": "NEW_QUESTION" if NEW_PREFIX.match(message) else "FOLLOW_UP",
            "method": "PREFIX",
            "elapsed_ms": 0.0,
        }
    return None


def validate_turn(
    decision: dict,
    question: str,
    supplements: list[str],
    message: str,
    pending_questions: list[str],
) -> None:
    validate(decision, CONVERSATION_SCHEMA)
    if decision["action"] != "CLARIFY":
        anchor = decision["message_anchor"]
        if not anchor.strip() or anchor not in message:
            raise ValueError("invalid_message_anchor")
    if decision["action"] == "FOLLOW_UP":
        anchor = decision["context_anchor"]
        if not anchor.strip() or not any(
            anchor in text for text in [question, *supplements, *pending_questions]
        ):
            raise ValueError("invalid_context_anchor")
    elif decision["action"] == "NEW_QUESTION" and decision["context_anchor"]:
        raise ValueError("unexpected_context_anchor")


def turn_context(
    question: str, supplements: list[str], message: str, action: str
) -> tuple[str, list[str]]:
    if action == "NEW_QUESTION":
        return message, []
    if action == "FOLLOW_UP" and question:
        return question, [*supplements, message]
    raise ValueError("An unresolved turn cannot select retrieval context")
