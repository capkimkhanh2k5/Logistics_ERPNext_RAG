"""Revision-pinned BGE-M3 encoding with content-addressed batch checkpoints."""

import json
from pathlib import Path

import numpy as np

from config.retrieval import retrieval_config
from rag.data import ROOT, digest, write_json


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
        import torch
        from FlagEmbedding import BGEM3FlagModel
        from huggingface_hub import snapshot_download

        self.cfg = cfg or retrieval_config()
        torch.set_num_threads(self.cfg.get("torch_num_threads", 4))
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
        # Reuse unchanged records from the prior snapshot, even if batch boundaries moved.
        previous = ROOT / "artifacts/embedding_manifest.json"
        reused = {}
        if previous.exists():
            old = json.loads(previous.read_text())
            if old["profile_id"] == self.profile_id:
                base = self.cache / old["snapshot"]
                with np.load(base.with_suffix(".npz"), allow_pickle=False) as saved:
                    old_dense = saved["dense"]
                old_sparse = json.loads(base.with_suffix(".sparse.json").read_text())
                reused = {
                    h: (v, w)
                    for h, v, w in zip(old["input_hashes"], old_dense, old_sparse, strict=True)
                }
        batches: list[np.ndarray] = []
        sparse: list[dict] = []
        lengths: list[int] = []
        step = self.cfg["checkpoint_size"]
        for start in range(0, len(rows), step):
            batch = rows[start : start + step]
            missing = [r for r in batch if r["input_hash"] not in reused]
            if missing:
                encoded = self.encode([r["embedding_text"] for r in missing])
                for r, v, w in zip(missing, encoded["dense"], encoded["sparse"], strict=True):
                    reused[r["input_hash"]] = (v, w)
            texts = [r["embedding_text"] for r in batch]
            token_lengths = [
                len(ids) for ids in self.model.tokenizer(texts, truncation=False)["input_ids"]
            ]
            if max(token_lengths) > self.cfg["max_length"]:
                raise ValueError("Corpus contains an oversized chunk")
            output: dict = {
                "dense": np.stack([reused[r["input_hash"]][0] for r in batch]),
                "sparse": [reused[r["input_hash"]][1] for r in batch],
                "token_lengths": token_lengths,
            }
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

    def source_context_vectors(self, snapshot: str, views: list[dict]) -> np.ndarray:
        """Index only cited source views; evaluation questions never enter this index."""
        identity = {
            "representation": "source-hierarchy-context-v1",
            "snapshot": snapshot,
            "profile": self.profile,
            "ids": [r["id"] for r in views],
            "text_hashes": [digest(r["rerank_text"]) for r in views],
        }
        directory = ROOT / "artifacts/context_embeddings"
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / (digest(identity) + ".npz")
        if target.exists():
            with np.load(target, allow_pickle=False) as saved:
                return validate_vectors(saved["dense"], len(views))
        # Reuse identical source text under the same embedding profile across views.
        # This does not reuse an embedding after source text or model settings change.
        reused = {}
        needed = set(identity["text_hashes"])
        for metadata_path in directory.glob("*.json"):
            old = json.loads(metadata_path.read_text())
            old_vectors = metadata_path.with_suffix(".npz")
            if old.get("profile") != self.profile or not old_vectors.exists():
                continue
            if not needed.intersection(old.get("text_hashes", [])):
                continue
            with np.load(old_vectors, allow_pickle=False) as saved:
                vectors = validate_vectors(saved["dense"], len(old["text_hashes"]))
            for h, vector in zip(old["text_hashes"], vectors, strict=True):
                if h in needed:
                    reused[h] = vector
        batches = []
        step = self.cfg["checkpoint_size"]
        for start in range(0, len(views), step):
            texts = [r["rerank_text"] for r in views[start : start + step]]
            missing = list(dict.fromkeys(t for t in texts if digest(t) not in reused))
            if missing:
                encoded = self.encode(missing)["dense"]
                reused.update({digest(t): v for t, v in zip(missing, encoded, strict=True)})
            batches.append(np.stack([reused[digest(t)] for t in texts]))
            print(
                f"Source context embedded {min(start + step, len(views))}/{len(views)}", flush=True
            )
        dense = validate_vectors(np.concatenate(batches), len(views))
        temporary = target.with_suffix(".tmp.npz")
        np.savez_compressed(temporary, dense=dense)
        temporary.replace(target)
        write_json(target.with_suffix(".json"), identity)
        return dense


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

    # Defined below as a module helper to keep dense/sparse profile compatibility.


def multivectors(embedder: Embedder, texts: list[str]) -> list[np.ndarray]:
    targets = [
        embedder.cache
        / (
            digest({"profile": embedder.profile, "text": text, "representation": "colbert"})
            + ".colbert.npy"
        )
        for text in texts
    ]
    pending = {
        target: text for target, text in zip(targets, texts, strict=True) if not target.exists()
    }
    missing = list(pending.items())
    for start in range(0, len(missing), 32):
        batch = missing[start : start + 32]
        inputs = [text for _, text in batch]
        lengths = embedder.model.tokenizer(inputs, truncation=False)["input_ids"]
        if max(map(len, lengths)) > embedder.cfg["max_length"]:
            raise ValueError("Multi-vector input exceeds max_length")
        output = embedder.model.encode(
            inputs,
            batch_size=embedder.cfg["batch_size"],
            max_length=embedder.cfg["max_length"],
            return_dense=False,
            return_sparse=False,
            return_colbert_vecs=True,
        )
        for (target, _), vector in zip(batch, output["colbert_vecs"], strict=True):
            np.save(target, np.asarray(vector, dtype=np.float32), allow_pickle=False)
    return [np.load(target, allow_pickle=False) for target in targets]


class CrossEncoder:
    def __init__(
        self,
        model: str,
        revision: str,
        device: str = "cpu",
        backend: str = "cross_encoder",
        batch_size: int | None = None,
        max_length: int = 1152,
        instruction: str | None = None,
        last_token_only: bool = False,
    ) -> None:
        from FlagEmbedding import FlagLLMReranker, FlagReranker
        from huggingface_hub import snapshot_download

        self.model_id, self.revision, self.backend, self.device = model, revision, backend, device
        self.batch_size = batch_size or (8 if backend == "qwen" else 4)
        self.max_length, self.instruction = max_length, instruction
        self.last_token_only = last_token_only
        path = snapshot_download(model, revision=revision, ignore_patterns=["*.onnx", "onnx/*"])
        if backend == "cross_encoder":
            self.model = FlagReranker(path, use_fp16=False, devices=device)
        elif backend == "flag_llm":
            self.model = FlagLLMReranker(path, use_fp16=device != "cpu", devices=device)
            if last_token_only:
                import torch

                self.model.tokenizer.padding_side = "left"
                full_forward = self.model.model.forward

                def last_forward(*args, **kwargs):
                    mask = kwargs["attention_mask"]
                    kwargs["position_ids"] = torch.clamp(mask.long().cumsum(-1) - 1, min=0)
                    kwargs.update(logits_to_keep=1, output_hidden_states=False, use_cache=False)
                    return full_forward(*args, **kwargs)

                self.model.model.forward = last_forward
        elif backend == "qwen":
            from types import SimpleNamespace

            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(
                path, revision=revision, local_files_only=True, padding_side="left"
            )
            self.network = (
                AutoModelForCausalLM.from_pretrained(
                    path,
                    revision=revision,
                    local_files_only=True,
                    torch_dtype=torch.float16 if device != "cpu" else torch.float32,
                )
                .to(device)
                .eval()
            )
            self.model = SimpleNamespace(tokenizer=tokenizer)
        else:
            raise ValueError(f"Unsupported reranker backend: {backend}")
        self.cache = ROOT / "artifacts/reranker"
        self.cache.mkdir(parents=True, exist_ok=True)

    def identity(self, query: str) -> dict:
        identity: dict = {"model": self.model_id, "revision": self.revision, "query": query}
        if getattr(self, "max_length", 1152) != 1152:
            identity["max_length"] = self.max_length
        if getattr(self, "instruction", None) is not None:
            identity["instruction"] = self.instruction
        if getattr(self, "last_token_only", False):
            identity["logit_layout"] = "last-token-left-pad-explicit-position-v1"
        if self.batch_size != (8 if self.backend == "qwen" else 4):
            identity["batch_size"] = self.batch_size
        if self.backend != "cross_encoder":
            identity.update(
                backend=self.backend,
                prompt_version="source-relevance-v1",
                device=self.device,
                dtype="float16" if self.device != "cpu" else "float32",
            )
        return identity

    def score_many(self, requests: list[tuple[str, list[str]]]) -> list[list[float]]:
        """Batch independent evaluation pairs; each query retains its own content cache."""
        saved, targets = {}, {}
        missing: dict[tuple[str, str], str] = {}
        for query, texts in requests:
            target = self.cache / (
                digest({**self.identity(query), "cache": "per-pair"}) + ".pairs.json"
            )
            if query not in saved:
                saved[query] = json.loads(target.read_text()) if target.exists() else {}
                targets[query] = target
            for text in texts:
                h = digest(text)
                if h not in saved[query]:
                    missing[(query, h)] = text
        if missing:
            pairs = [[q, text] for (q, _), text in missing.items()]
            lengths = self.model.tokenizer(pairs, truncation=False)["input_ids"]
            if max(map(len, lengths)) > getattr(self, "max_length", 1152):
                raise ValueError("Evaluation pair exceeds reranker budget")
            scores = self.compute_scores(pairs)
            for (q, h), value in zip(missing, np.atleast_1d(scores), strict=True):
                saved[q][h] = float(value)
            for query, target in targets.items():
                write_json(target, saved[query])
        return [[saved[q][digest(text)] for text in texts] for q, texts in requests]

    def score(self, query: str, texts: list[str], use_cache: bool = True) -> list[float]:
        if not texts:
            return []
        identity = self.identity(query)
        key = digest({**identity, "texts": texts})
        target = self.cache / (key + ".json")
        pair_target = self.cache / (digest({**identity, "cache": "per-pair"}) + ".pairs.json")
        saved = json.loads(pair_target.read_text()) if use_cache and pair_target.exists() else {}
        hashes = [digest(text) for text in texts]
        if use_cache and target.exists():
            result = json.loads(target.read_text())
            saved.update(dict(zip(hashes, result, strict=True)))
            write_json(pair_target, saved)
            return result
        missing = {h: text for h, text in zip(hashes, texts, strict=True) if h not in saved}
        if missing:
            inputs = [[query, text] for text in missing.values()]
            lengths = self.model.tokenizer(inputs, truncation=False)["input_ids"]
            if max(map(len, lengths)) > getattr(self, "max_length", 1152):
                raise ValueError(
                    "Cross-encoder pair exceeds max_length; refusing silent truncation"
                )
            scores = self.compute_scores(inputs)
            saved.update(
                {h: float(score) for h, score in zip(missing, np.atleast_1d(scores), strict=True)}
            )
        result = [saved[h] for h in hashes]
        write_json(target, result)
        write_json(pair_target, saved)
        return result

    def compute_scores(self, pairs: list[list[str]]) -> list[float]:
        if self.backend != "qwen":
            return self.model.compute_score(
                pairs, batch_size=self.batch_size, max_length=getattr(self, "max_length", 1152)
            )
        import torch

        tokenizer = self.model.tokenizer
        prefix = '<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n'
        suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        instruction = (
            getattr(self, "instruction", None)
            or "Retrieve the tariff entry whose cited description and hierarchy match the product described in the query."
        )
        texts = [
            prefix + f"<Instruct>: {instruction}\n<Query>: {q}\n<Document>: {d}" + suffix
            for q, d in pairs
        ]
        result = []
        for start in range(0, len(texts), self.batch_size):
            encoded = tokenizer(
                texts[start : start + self.batch_size],
                padding=True,
                truncation=False,
                return_tensors="pt",
            )
            if encoded["input_ids"].shape[1] > getattr(self, "max_length", 1152):
                raise ValueError("Qwen prompt exceeds reranker budget; refusing truncation")
            encoded = {k: v.to(self.device) for k, v in encoded.items()}
            with torch.inference_mode():
                logits = (
                    self.network(**encoded, logits_to_keep=1, use_cache=False)
                    .logits[:, -1, :]
                    .float()
                )
                difference = (
                    logits[:, tokenizer.convert_tokens_to_ids("yes")]
                    - logits[:, tokenizer.convert_tokens_to_ids("no")]
                )
                result.extend(difference.cpu().tolist())
        return result


def colbert_scores(
    embedder: Embedder, query: str, texts: list[str], use_cache: bool = True
) -> list[float]:
    target = embedder.cache / (
        digest({"profile": embedder.profile, "query": query, "scores": "colbert-v1"})
        + ".colbert-scores.json"
    )
    saved = json.loads(target.read_text()) if use_cache and target.exists() else {}
    hashes = [digest(text) for text in texts]
    missing = {h: text for h, text in zip(hashes, texts, strict=True) if h not in saved}
    if missing:
        if use_cache:
            q = multivectors(embedder, [query])[0]
        else:
            if (
                len(embedder.model.tokenizer(query, truncation=False)["input_ids"])
                > embedder.cfg["max_length"]
            ):
                raise ValueError("ColBERT query exceeds max_length")
            encoded = embedder.model.encode(
                [query],
                batch_size=1,
                max_length=embedder.cfg["max_length"],
                return_dense=False,
                return_sparse=False,
                return_colbert_vecs=True,
            )
            q = np.asarray(encoded["colbert_vecs"][0], dtype=np.float32)
        passages = multivectors(embedder, list(missing.values()))
        saved.update(
            {
                h: float(embedder.model.colbert_score(q, passage))
                for h, passage in zip(missing, passages, strict=True)
            }
        )
    result = [saved[h] for h in hashes]
    write_json(target, saved)
    return result
