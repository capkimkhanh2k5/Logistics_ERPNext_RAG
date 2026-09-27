"""Revision-pinned BGE-M3 encoding with content-addressed batch checkpoints."""

import json
from pathlib import Path

import numpy as np

from rag.data import ROOT, config, digest, write_json


def validate_vectors(vectors: np.ndarray, count: int) -> np.ndarray:
    vectors = np.asarray(vectors, dtype=np.float32)
    if vectors.shape != (count, 1024) or not np.isfinite(vectors).all():
        raise ValueError(f"Invalid dense vectors: {vectors.shape}")
    norm = np.linalg.norm(vectors, axis=1, keepdims=True)
    if (norm < 1e-8).any():
        raise ValueError("Zero embedding vector")
    return vectors / norm


class Embedder:
    def __init__(self, cfg: dict | None = None) -> None:
        from FlagEmbedding import BGEM3FlagModel
        from huggingface_hub import snapshot_download

        self.cfg = cfg or config()
        model_path = snapshot_download(
            self.cfg["model"], revision=self.cfg["revision"], ignore_patterns=["*.onnx", "onnx/*"]
        )
        revision = Path(model_path).name
        self.profile = {
            "model": self.cfg["model"],
            "revision": revision,
            "max_length": self.cfg["max_length"],
            "sparse": self.cfg["sparse"],
            "strategy": self.cfg["chunk_strategy"],
            "dtype": "float32",
            "device": self.cfg["device"],
        }
        self.profile_id = digest(self.profile)[:24]
        self.model = BGEM3FlagModel(model_path, devices=self.cfg["device"], use_fp16=False)
        self.cache = ROOT / "artifacts/embeddings" / self.profile_id
        self.cache.mkdir(parents=True, exist_ok=True)
        write_json(self.cache / "profile.json", self.profile)

    def encode(self, texts: list[str], use_cache: bool = True) -> dict:
        lengths = [len(ids) for ids in self.model.tokenizer(texts, truncation=False)["input_ids"]]
        if lengths and max(lengths) > self.cfg["max_length"]:
            raise ValueError(f"Input requires {max(lengths)} tokens; refusing silent truncation")
        key = digest({"profile": self.profile, "texts": texts})
        target = self.cache / f"{key}.npz"
        sparse_path = self.cache / f"{key}.json"
        cache_hit = (
            use_cache and target.exists() and (not self.cfg["sparse"] or sparse_path.exists())
        )
        if cache_hit:
            with np.load(target, allow_pickle=False) as saved:
                dense = validate_vectors(saved["dense"], len(texts))
            sparse = json.loads(sparse_path.read_text()) if self.cfg["sparse"] else []
        else:
            output = self.model.encode(
                texts,
                batch_size=self.cfg["batch_size"],
                max_length=self.cfg["max_length"],
                return_dense=True,
                return_sparse=self.cfg["sparse"],
                return_colbert_vecs=False,
            )
            dense = validate_vectors(output["dense_vecs"], len(texts))
            sparse = [
                {str(k): float(v) for k, v in weights.items()}
                for weights in (output.get("lexical_weights") or [])
            ]
            temp = target.with_suffix(".tmp.npz")
            np.savez_compressed(temp, dense=dense)
            temp.replace(target)
            if self.cfg["sparse"]:
                write_json(sparse_path, sparse)
        return {"dense": dense, "sparse": sparse, "token_lengths": lengths, "cache_hit": cache_hit}

    def corpus(self, bundle: dict) -> dict:
        rows = bundle["records"]
        batches = []
        sparse = []
        lengths = []
        step = self.cfg["checkpoint_size"]
        for start in range(0, len(rows), step):
            output = self.encode([r["embedding_text"] for r in rows[start : start + step]])
            batches.append(output["dense"])
            sparse.extend(output["sparse"])
            lengths.extend(output["token_lengths"])
            print(f"Embedded {min(start + step, len(rows))}/{len(rows)}", flush=True)
        dense = validate_vectors(np.concatenate(batches), len(rows))
        np.savez_compressed(self.cache / f"{bundle['snapshot']}.npz", dense=dense)
        manifest = {
            "snapshot": bundle["snapshot"],
            "profile": self.profile,
            "profile_id": self.profile_id,
            "ids": [r["id"] for r in rows],
            "input_hashes": [r["input_hash"] for r in rows],
            "max_tokens": max(lengths),
            "count": len(rows),
        }
        write_json(self.cache / f"{bundle['snapshot']}.json", manifest)
        if self.cfg["sparse"]:
            write_json(self.cache / f"{bundle['snapshot']}.sparse.json", sparse)
        write_json(ROOT / "artifacts/embedding_manifest.json", manifest)
        return manifest


def load_embeddings(bundle: dict) -> tuple[dict, np.ndarray, list]:
    manifest = json.loads((ROOT / "artifacts/embedding_manifest.json").read_text())
    assert manifest["snapshot"] == bundle["snapshot"], "Embedding snapshot mismatch"
    assert manifest["ids"] == [r["id"] for r in bundle["records"]], "Embedding order mismatch"
    assert manifest["input_hashes"] == [r["input_hash"] for r in bundle["records"]]
    base = ROOT / "artifacts/embeddings" / manifest["profile_id"]
    with np.load(base / f"{bundle['snapshot']}.npz", allow_pickle=False) as saved:
        dense = validate_vectors(saved["dense"], len(bundle["records"]))
    sparse = (
        json.loads((base / f"{bundle['snapshot']}.sparse.json").read_text())
        if manifest["profile"]["sparse"]
        else []
    )
    return manifest, dense, sparse
