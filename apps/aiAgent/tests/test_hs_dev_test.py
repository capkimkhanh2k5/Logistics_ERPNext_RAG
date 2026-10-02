"""Verify the exported evaluation boundary on the real HS questions."""

import hashlib
import json

import pytest

from rag.data import ROOT, read
from scripts.prepare_dev_test import export_split


def test_export_retains_all_cases_and_isolates_groups_and_dev_folds(tmp_path):
    manifest = export_split(tmp_path)
    dev = read(tmp_path / manifest["files"]["dev"]["path"])
    test = read(tmp_path / manifest["files"]["test"]["path"])
    originals = [
        row for path in manifest["original_file_archive"].values() for row in read(ROOT / path)
    ]
    assert len(dev) == 752 and len(test) == 188
    assert manifest["section_counts"] == {
        "XIV": {"dev": 195, "test": 49},
        "XVI": {"dev": 341, "test": 85},
        "XVII": {"dev": 216, "test": 54},
    }
    assert {r["record_id"] for r in dev + test} == {r["record_id"] for r in originals}
    assert len({r["record_id"] for r in dev + test}) == len(dev + test)
    assert not {r["eval_group_id"] for r in dev} & {r["eval_group_id"] for r in test}
    assert all(r["dev_fold"] is None for r in test)
    assert {r["dev_fold"] for r in dev} == set(range(5))
    for fold in range(5):
        validation = {r["eval_group_id"] for r in dev if r["dev_fold"] == fold}
        development = {r["eval_group_id"] for r in dev if r["dev_fold"] != fold}
        assert not validation & development
    by_id = {r["record_id"]: r for r in originals}
    for row in dev + test:
        original = by_id[row["record_id"]]
        assert row["original_split"] == original["split"]
        assert all(row[k] == v for k, v in original.items() if k != "split")
    for path, expected in manifest["source_file_sha256"].items():
        assert (
            hashlib.sha256(
                (ROOT / manifest["original_file_archive"][path]).read_bytes()
            ).hexdigest()
            == expected
        )
    for info in manifest["files"].values():
        assert hashlib.sha256((tmp_path / info["path"]).read_bytes()).hexdigest() == info["sha256"]


def test_export_is_reproducible_and_rejects_modified_frozen_files(tmp_path):
    export_split(tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    export_split(tmp_path)
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    path = tmp_path / "HS_RAG_TEST.jsonl"
    path.write_text(json.dumps({"record_id": "modified"}) + "\n")
    with pytest.raises(ValueError, match="Frozen split differs"):
        export_split(tmp_path)
    assert path.read_text() == json.dumps({"record_id": "modified"}) + "\n"


def test_qa_export_retains_questions_and_isolates_groups(tmp_path):
    manifest = export_split(tmp_path, dataset="qa")
    dev = read(tmp_path / manifest["files"]["dev"]["path"])
    test = read(tmp_path / manifest["files"]["test"]["path"])
    original = [r for path in manifest["original_file_archive"].values() for r in read(ROOT / path)]
    assert len(dev) == 520 and len(test) == 130
    assert len({r["id"] for r in dev + test}) == 650
    assert {r["id"] for r in dev + test} == {r["id"] for r in original}
    assert not {r["eval_group_id"] for r in dev} & {r["eval_group_id"] for r in test}
    by_id = {r["id"]: r for r in original}
    for row in dev + test:
        source = by_id[row["id"]]
        assert row["query"] == source["query"]
        assert row["gold_primary_chunk_ids"] == source["gold_primary_chunk_ids"]
    assert all(not (ROOT / path).exists() for path in manifest["original_file_archive"])
