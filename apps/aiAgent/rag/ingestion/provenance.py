"""Recognize the exact processor fingerprints of the package relocation.

Stored PDF proofs retain the fingerprint of the code that produced them. A
relocation is compatible only with the explicitly recorded before/after hashes;
other code changes, versions and extraction-library changes still fail closed.
"""

import json
from pathlib import Path


def same_processor(recorded: object, current: dict) -> bool:
    if recorded == current:
        return True
    if not isinstance(recorded, dict) or recorded.keys() != current.keys():
        return False
    registry = json.loads(Path(__file__).with_name("provenance_relocations.json").read_text())
    for relocation in registry["processors"]:
        key = relocation["hash_field"]
        if (
            recorded.get(key) == relocation["before_sha256"]
            and current.get(key) == relocation["after_sha256"]
            and {k: v for k, v in recorded.items() if k != key}
            == {k: v for k, v in current.items() if k != key}
        ):
            return True
    return False
