"""Extend registered sources without retuning retrieval or deleting old snapshots."""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rag.chunking.corpus import build_corpus  # noqa: E402
from rag.embedding.bge_m3 import Embedder, load_embeddings  # noqa: E402
from rag.utils.files import write_json  # noqa: E402
from rag.vectordb.postgres import connect, counts, ingest, migrate  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    paths = [
        ROOT / "artifacts/corpus.json",
        ROOT / "artifacts/embedding_manifest.json",
        ROOT / "config/selected_retrieval.json",
        ROOT / "config/unified_retrieval.json",
    ]
    backups = {}
    for index, path in enumerate(paths):
        backup = args.output / f"before-{index}-{path.name}"
        shutil.copy2(path, backup)
        backups[path] = backup
    old = json.loads(backups[paths[0]].read_text())
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "apply": args.apply,
        "previous_snapshot": old["snapshot"],
        "backups": {str(p): str(b.resolve()) for p, b in backups.items()},
        "retrieval_parameters_unchanged": True,
        "quality_status": "SOURCE_EXTENSION_PENDING_FULL_QUALITY_EVAL",
    }
    try:
        bundle = build_corpus()
        new_rows = {r["id"]: r for r in bundle["records"]}
        old_ids = {r["id"] for r in old["records"]}
        for row in old["records"]:
            assert new_rows[row["id"]] == row, f"Existing source drift: {row['id']}"
        added = [r for r in bundle["records"] if r["id"] not in old_ids]
        assert added and all(r["role"] == "evidence" and r["code"] is None for r in added)
        report.update(
            snapshot=bundle["snapshot"],
            previous_records=len(old["records"]),
            new_records=len(added),
            total_records=len(bundle["records"]),
            original_records_unchanged=True,
        )
        if args.apply:
            embedder = Embedder()
            manifest = embedder.corpus(bundle)
            manifest, dense, sparse = load_embeddings(bundle)
            report.update(profile=manifest["profile_id"], max_tokens=manifest["max_tokens"])
            with connect() as conn, conn.transaction():
                active = conn.execute("SELECT snapshot,profile FROM rag.active").fetchone()
                assert active and active["snapshot"] == old["snapshot"], "Active snapshot drift"
                assert active["profile"] == manifest["profile_id"], "Embedding profile changed"
                report["counts_before"] = counts(conn, active["snapshot"], active["profile"])
                report["previous_db_matches_manifest_count"] = report["counts_before"][
                    "chunks"
                ] == len(old["records"])
                migrate(conn)
                report["ingestion"] = ingest(conn, bundle, manifest, dense, sparse, apply=True)
                for path in paths[2:]:
                    policy = json.loads(backups[path].read_text())
                    assert policy["snapshot"] == old["snapshot"]
                    policy.update(
                        snapshot=bundle["snapshot"],
                        profile=manifest["profile_id"],
                        source_extension={
                            "previous_snapshot": old["snapshot"],
                            "records_added": len(added),
                            "original_records_unchanged": True,
                            "retrieval_parameters_unchanged": True,
                            "validation_status": report["quality_status"],
                            "historical_metrics_snapshot": old["snapshot"],
                        },
                    )
                    if "active_source_hashes" in policy:
                        policy["active_source_hashes"] = bundle["manifest"]["source_hashes"]
                        policy["binding_note"] = report["quality_status"]
                        policy["qa_transfer_status"] = report["quality_status"]
                    write_json(path, policy)
                report["counts_after"] = counts(conn, bundle["snapshot"], manifest["profile_id"])
        else:
            for path, backup in backups.items():
                shutil.copy2(backup, path)
        report["ok"] = True
    except BaseException as exc:
        for path, backup in backups.items():
            shutil.copy2(backup, path)
        report.update(ok=False, error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        write_json(args.output / "report.json", report)
        print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
