"""JSON-format instructions for providers without native schema support."""

import json

JSON_SCHEMA_PROMPT = (
    "Return only a JSON object matching this JSON schema, without "
    "Markdown fences or extra text: {schema}"
)


def format_json_schema_prompt(schema: dict) -> str:
    return JSON_SCHEMA_PROMPT.format(schema=json.dumps(schema, ensure_ascii=False))
