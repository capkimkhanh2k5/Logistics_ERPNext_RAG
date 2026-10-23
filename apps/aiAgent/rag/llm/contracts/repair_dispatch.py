"""Route repair only where semantic reconsideration is needed, never fabricate coverage."""

from copy import deepcopy

from rag.llm.contracts.diagnostics import diagnostic


def canonicalize(value, context_codes=()) -> tuple[dict, list[dict]]:
    result, changes = deepcopy(value), []
    allowed = set(context_codes)

    def visit(node, path):
        if isinstance(node, list):
            for index, child in enumerate(node):
                visit(child, f"{path}/{index}")
        elif isinstance(node, dict):
            for key, child in list(node.items()):
                location = f"{path}/{key}"
                if (
                    key
                    in {
                        "evidence_ids",
                        "fact_ids",
                        "condition_ids",
                        "ledger_ids",
                        "decisive_evidence_ids",
                    }
                    and isinstance(child, list)
                    and all(isinstance(v, str) for v in child)
                ):
                    unique = list(dict.fromkeys(child))
                    if unique != child:
                        node[key] = unique
                        changes.append(
                            {"path": location, "action": "DEDUPLICATE_IDENTICAL_REFERENCES"}
                        )
                elif key in {"code", "selected_code", "suggested_hs_code"} and isinstance(
                    child, str
                ):
                    compact = child.replace(".", "").strip()
                    if compact != child and compact in allowed:
                        node[key] = compact
                        changes.append(
                            {"path": location, "action": "NORMALIZE_REGISTERED_CODE_FORMAT"}
                        )
                else:
                    visit(child, location)

    visit(result, "")
    return result, changes


def dispatch(errors: list[str], phase: str, *, allow_rebind: bool = False) -> dict:
    terminal, repair = [], []
    for error in errors:
        detail = diagnostic(error, phase)
        if detail["cause"] in {"BINDING", "COVERAGE"} and not allow_rebind:
            terminal.append(error)
        else:
            repair.append(error)
    return {
        "withhold": terminal,
        "repair": repair,
        "issues": [diagnostic(e, phase) for e in errors],
    }
