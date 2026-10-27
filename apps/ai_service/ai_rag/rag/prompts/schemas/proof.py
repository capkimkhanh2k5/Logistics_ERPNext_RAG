"""Product-independent ledger and finite proof graph wire contracts."""

from copy import deepcopy


def _object(properties: dict) -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(properties),
    }


def _strings() -> dict:
    return {"type": "array", "uniqueItems": True, "items": {"type": "string"}}


FACT_LEDGER_SCHEMA: dict = {
    "type": "array",
    "maxItems": 256,
    "items": _object(
        {
            "key": {"type": "string", "minLength": 1},
            "item_id": {"type": "string"},
            "attribute": {"type": "string", "minLength": 1},
            "value": {"type": "string"},
            "polarity": {"enum": ["AFFIRMED", "NEGATED", "UNSPECIFIED"]},
            "modality": {"enum": ["ASSERTED", "UNKNOWN", "HYPOTHETICAL", "QUESTION"]},
            "fact_id": {"type": "string"},
            "quote": {"type": "string"},
            "supersedes": _strings(),
            "correction_quote": {"type": "string"},
        }
    ),
}

PROOF_SCHEMA: dict = _object(
    {
        "target": {"type": "string", "minLength": 1},
        "decomposition_review": {"enum": ["FAITHFUL_COMPLETE", "UNVERIFIED"]},
        "ledger_review": {"enum": ["CONSISTENT", "UNVERIFIED"]},
        "root": {"type": "string", "minLength": 1},
        "nodes": {
            "type": "array",
            "minItems": 1,
            "maxItems": 128,
            "items": _object(
                {
                    "key": {"type": "string", "minLength": 1},
                    "operator": {
                        "enum": ["ATOM", "ALL", "ANY", "NOT", "SCOPE", "EXCEPT", "COMPARE"]
                    },
                    "kind": {
                        "enum": [
                            "PRODUCT_FACT",
                            "LEGAL_RULE",
                            "PREDICATE",
                            "RELATION",
                            "SCOPE",
                            "QUANTITY",
                        ]
                    },
                    "text": {"type": "string", "minLength": 1},
                    "attribute": {"type": "string"},
                    "item_ids": _strings(),
                    "children": _strings(),
                    "evidence_ids": _strings(),
                    "condition_ids": _strings(),
                    "ledger_ids": _strings(),
                    "assessment": {"enum": ["PROVEN", "CONTRADICTED", "UNKNOWN"]},
                    "cause": {
                        "enum": [
                            "NONE",
                            "MISSING_PRODUCT_FACT",
                            "MISSING_LEGAL_RULE",
                            "UNRESOLVED_APPLICATION",
                            "INVALID_PROOF",
                        ]
                    },
                    "comparison": _object(
                        {
                            "left": {"type": "string"},
                            "right": {"type": "string"},
                            "left_unit": {"type": "string"},
                            "right_unit": {"type": "string"},
                            "operator": {"enum": ["NONE", "EQ", "LT", "LE", "GT", "GE"]},
                        }
                    ),
                }
            ),
        },
    }
)

# The conclusion is the consumer slot itself, never a second model-written copy.
WIRE_PROOF_SCHEMA = deepcopy(PROOF_SCHEMA)
for _field in ("target", "root"):
    WIRE_PROOF_SCHEMA["properties"].pop(_field)
    WIRE_PROOF_SCHEMA["required"].remove(_field)
WIRE_PROOF_SCHEMA["properties"]["root_node"] = deepcopy(
    PROOF_SCHEMA["properties"]["nodes"]["items"]
)
for _field in ("key", "text"):
    WIRE_PROOF_SCHEMA["properties"]["root_node"]["properties"].pop(_field)
    WIRE_PROOF_SCHEMA["properties"]["root_node"]["required"].remove(_field)
WIRE_PROOF_SCHEMA["properties"]["nodes"]["minItems"] = 0
WIRE_PROOF_SCHEMA["properties"]["nodes"]["maxItems"] = 127
WIRE_PROOF_SCHEMA["required"].append("root_node")

WIRE_LEDGER_SCHEMA = deepcopy(FACT_LEDGER_SCHEMA)
for _field in ("value", "quote", "correction_quote"):
    WIRE_LEDGER_SCHEMA["items"]["properties"].pop(_field)
    WIRE_LEDGER_SCHEMA["items"]["required"].remove(_field)
WIRE_LEDGER_SCHEMA["items"]["properties"]["source_mode"] = {"enum": ["STATEMENT"]}
WIRE_LEDGER_SCHEMA["items"]["required"].append("source_mode")


def ledger_schema(schema: dict, item_ids: list[str]) -> dict:
    value = deepcopy(schema)
    value["properties"]["fact_ledger"] = deepcopy(WIRE_LEDGER_SCHEMA)
    item = value["properties"]["fact_ledger"]["items"]["properties"]["item_id"]
    if item_ids and "" not in item_ids:
        item["enum"] = item_ids
    if "fact_ledger" not in value["required"]:
        value["required"].append("fact_ledger")
    return value


def proof_schema(schema: dict) -> dict:
    value = deepcopy(schema)
    if "proof_catalogue" in value.get("properties", {}):
        return value

    def visit(node):
        if isinstance(node, list):
            for child in node:
                visit(child)
        elif isinstance(node, dict):
            properties = node.get("properties", {})
            if "assessment" in properties and (
                "fact_ids" in properties or "product_fact_indices" in properties
            ):
                properties["proof"] = deepcopy(PROOF_SCHEMA)
                if "proof" not in node.setdefault("required", []):
                    node["required"].append("proof")
            if {"question", "attribute", "evidence_ids"} <= properties.keys():
                properties["proof"] = deepcopy(PROOF_SCHEMA)
                if "proof" not in node.setdefault("required", []):
                    node["required"].append("proof")
            if {"kind", "text", "evidence_ids", "fact_ids"} <= properties.keys():
                properties["proof"] = deepcopy(PROOF_SCHEMA)
                if "proof" not in node.setdefault("required", []):
                    node["required"].append("proof")
            if {"condition_checks", "reason", "status"} <= properties.keys():
                properties["reason_proof"] = deepcopy(PROOF_SCHEMA)
                if "reason_proof" not in node.setdefault("required", []):
                    node["required"].append("reason_proof")
            for key, child in list(node.items()):
                if key == "properties":
                    for name, field in list(child.items()):
                        if name not in {"proof", "reason_proof"}:
                            visit(field)
                elif key not in {"required", "enum"}:
                    visit(child)

    visit(value)
    return value


def catalogue_schema(schema: dict) -> dict:
    """Send one graph definition contract, with small references at each use site."""
    value = deepcopy(schema)
    if "proof_catalogue" in value.get("properties", {}):
        return value

    def visit(node):
        if isinstance(node, list):
            for child in node:
                visit(child)
        elif isinstance(node, dict):
            properties = node.get("properties", {})
            for name in ("proof", "reason_proof"):
                if name in properties:
                    properties.pop(name)
                    properties[name + "_key"] = {"type": "string", "minLength": 1}
                    node["required"] = [
                        name + "_key" if field == name else field
                        for field in node.get("required", [])
                    ]
            for child in list(node.values()):
                visit(child)

    visit(value)
    value["properties"]["proof_catalogue"] = {
        "type": "array",
        "maxItems": 256,
        "items": _object(
            {"key": {"type": "string", "minLength": 1}, "proof": deepcopy(WIRE_PROOF_SCHEMA)}
        ),
    }
    value["required"].append("proof_catalogue")
    return value
