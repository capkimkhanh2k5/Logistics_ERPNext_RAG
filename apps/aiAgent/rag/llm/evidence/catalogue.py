"""Resolve local proof references without letting a missing graph poison other jobs."""

from collections import Counter
from copy import deepcopy

from rag.llm.contracts.errors import ContractIssue


def expand_proofs(value) -> tuple[dict, list[str]]:
    if not isinstance(value, dict) or "proof_catalogue" not in value:
        return value, []  # Explicit inline proofs remain readable for stored canonical payloads.
    result = deepcopy(value)
    errors: list[str] = []
    entries = result.pop("proof_catalogue")
    graphs, duplicate = {}, set()
    uses: Counter[str] = Counter()

    def count(node):
        if isinstance(node, list):
            for child in node:
                count(child)
        elif isinstance(node, dict):
            for name, child in node.items():
                if name in {"proof_key", "reason_proof_key"} and isinstance(child, str):
                    uses[child] += 1
                else:
                    count(child)

    count(result)
    for entry in entries if isinstance(entries, list) else []:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("key"), str)
            or not isinstance(entry.get("proof"), dict)
        ):
            continue
        key = entry["key"]
        if key in graphs:
            duplicate.add(key)
        graphs[key] = entry["proof"]
        consumer_bound = (
            "root_node" in entry["proof"] or entry["proof"].get("target") == "$CONSUMER"
        )
        if consumer_bound and uses[key] > 1:
            duplicate.add(key)  # A consumer-bound conclusion cannot change across slots.

    def bind(node, path):
        if isinstance(node, list):
            return [bind(child, f"{path}/{index}") for index, child in enumerate(node)]
        if not isinstance(node, dict):
            return node
        bound = {
            key: bind(child, f"{path}/{key}")
            for key, child in node.items()
            if key not in {"proof_key", "reason_proof_key"}
        }
        for field in ("proof", "reason_proof"):
            if field + "_key" not in node:
                continue
            key = node[field + "_key"]
            if not isinstance(key, str) or key not in graphs or key in duplicate or field in node:
                errors.append(
                    ContractIssue(
                        "Tham chiếu proof cục bộ thiếu hoặc mâu thuẫn; mỗi consumer cần key/graph riêng, không tái dùng graph v2 cho nhiều mệnh đề.",
                        code="PROOF_REF_INVALID",
                        path=f"{path}/{field}",
                        expected="Một key có graph riêng cho consumer này",
                        actual=key,
                    )
                )
                bound[field] = None
            else:
                proof = deepcopy(graphs[key])
                if "root_node" in proof:
                    from rag.llm.validation.answer import schema_errors
                    from rag.prompts.schemas.proof import WIRE_PROOF_SCHEMA

                    failures = schema_errors(proof, WIRE_PROOF_SCHEMA)
                    if failures or any(n.get("key") == "$ROOT" for n in proof.get("nodes", [])):
                        errors.append(
                            ContractIssue(
                                "Proof wire hoặc root node không hợp lệ.",
                                code="PROOF_INVALID",
                                path=f"{path}/{field}",
                            )
                        )
                        bound[field] = None
                        continue
                    root = proof.pop("root_node")
                    proof.update(target="$CONSUMER", root="$ROOT")
                    proof["nodes"].append({**root, "key": "$ROOT", "text": "$CONSUMER"})
                bound[field] = proof
        return bound

    return bind(result, ""), errors
