"""Revision-pinned cross encoders and ColBERT source scoring."""

import json

import numpy as np

from config.settings import ROOT
from rag.embedding.bge_m3 import Embedder, multivectors
from rag.utils.files import digest, write_json


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
