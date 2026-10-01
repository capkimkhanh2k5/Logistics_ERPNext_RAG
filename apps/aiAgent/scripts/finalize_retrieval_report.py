#!/usr/bin/env python3
"""Finalize the measured v2 handoff; refuse incomplete ablation/QA artifacts."""

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENT_ROOT))

from rag.data import ROOT, load_corpus, read, write_json  # noqa: E402
from rag.db import connect  # noqa: E402
from rag.retrieval import Retriever  # noqa: E402
from scripts.run_retrieval_experiment import (  # noqa: E402
    cache_identity,
    compute_metrics,
    load_cases,
    paired_cluster_interval,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="run_generic_graph_v2_budget")
    args = parser.parse_args()
    folder = ROOT / "artifacts/experiments" / args.run_id
    cases, bundle = load_cases(), load_corpus()
    manifest = read(folder / "manifest.json")
    outputs = {
        m: read(folder / f"{m}_predictions.json")
        for m in ("B0", "B1", "B2")
        if (folder / f"{m}_predictions.json").exists()
    }
    ids = {c["record_id"] for c in cases}
    with connect() as conn:
        current_identity = cache_identity(Retriever(conn), cases)
    for result in outputs.values():
        assert set(result["predictions"]) == ids, "Incomplete predictions"
        assert result["identity"] == current_identity, "Stale experiment identity"
    predictions = {m: v["predictions"] for m, v in outputs.items()}
    policy = outputs["B1"]["policy"]
    production = policy["default_method"]
    qa = read(folder / "qa_runtime_regression.json")
    latency = read(folder / "fresh_runtime_latency.json")
    assert qa["snapshot"] == latency["snapshot"] == bundle["snapshot"]
    assert qa["profile"] == latency["profile"] == current_identity["profile"]
    assert latency["policy"] == policy, "Latency measured with a different policy"
    assert sum(s["count"] for s in qa["splits"].values()) == 650
    assert not any(r["query_cache_hit"] for r in latency["rows"])
    stages = defaultdict(Counter)
    for c in cases:
        p, gold = predictions[production][c["record_id"]], c["expected_hs_8"]
        ranked = [r["code"] for r in p["ranked"]]
        if gold not in p["pool_codes"]:
            stage = "absent_top100"
        elif gold not in p["pool_codes"][: policy["rerank_pool"]]:
            stage = "outside_rerank40"
        elif gold not in ranked:
            stage = "rank_after10"
        else:
            rank = ranked.index(gold) + 1
            stage = "top1" if rank == 1 else "rank2to5" if rank <= 5 else "rank6to10"
        stages[c["section"]][stage] += 1
        stages["ALL"][stage] += 1
    all_metrics = {
        m: compute_metrics(cases, p, policy["rerank_pool"]) for m, p in predictions.items()
    }
    splits = {
        split: compute_metrics(
            [c for c in cases if c["split"] == split],
            predictions[production],
            policy["rerank_pool"],
        )
        for split in ("train", "test", "holdout")
    }
    paired = paired_cluster_interval(cases, manifest, predictions["B0"], predictions[production])
    old_metrics_path = ROOT / "artifacts/experiments/run_hs_grouped_cv_v1/M5_metrics.json"
    old_metrics = read(old_metrics_path) if old_metrics_path.exists() else None
    previous_folder = ROOT / "artifacts/experiments/run_generic_graph_v2_final"
    previous_metrics = {
        m: read(previous_folder / f"{m}_metrics.json")
        for m in ("B0", "B1", "B2")
        if (previous_folder / f"{m}_metrics.json").exists()
    }
    verification_path = folder / "verification.json"
    verification = read(verification_path) if verification_path.exists() else None
    cleanup_path = folder / "cleanup_validation.json"
    cleanup = read(cleanup_path) if cleanup_path.exists() else None
    latest_checks = cleanup or verification
    payload = {
        "snapshot": bundle["snapshot"],
        "policy": policy,
        "metrics": all_metrics,
        "production_method": production,
        "production_splits": splits,
        "failure_stages": dict(stages),
        "paired": paired,
        "historical_M5_reference": old_metrics,
        "previous_v2_diagnostic": previous_metrics,
        "verification": verification,
        "cleanup": cleanup,
        "qa_splits": qa["splits"],
        "latency": {k: v for k, v in latency.items() if k != "rows"},
    }
    write_json(folder / "handoff_summary.json", payload)
    lines = [
        "# Báo cáo triển khai Retrieval v2",
        "",
        "## 1. Thay đổi đã triển khai",
        "",
        "- Đăng ký nguồn/schema bằng manifest; Phần/Chương lấy từ corpus active và đối chiếu taxonomy.",
        "- Một policy hybrid + Cross-Encoder cho mọi Chương đã nạp; bỏ product keyword → danh sách mã và penalty theo prefix HS.",
        "- Context/Notes từ NODE/EDGE, ancestor, nhãn nguồn và annotation có locator; node ảo không tạo wording pháp lý.",
        "- Các nhãn legacy thiếu ranh giới được giới hạn theo cấu trúc được khai báo. Ưu tiên bổ sung CONTEXT_FOR đúng phạm vi trong dữ liệu nguồn.",
        "- Snapshot cũ, source/code/policy và notebook lịch sử được giữ để đối chiếu.",
        "",
        f"Snapshot `{bundle['snapshot']}`: {len(bundle['records']):,} records / {len(bundle['nodes']):,} nodes / {len(bundle['edges']):,} edges.",
        "",
        "## 2. Giao thức và kết quả HS",
        "",
        f"{len(cases)} câu / {manifest['total_groups']} groups. Query name_and_spec được làm sạch; không fine-tune model, không ingest gold, không tune theo Phần/Chương. Cấu hình khóa trước lượt rerun; B1 được chọn làm mặc định từ lượt regression v2 trước.",
        "",
        "Đây là regression trên bộ đã được xem. Folds được lưu nhưng không dùng học tham số; không gọi lượt này là nested OOF hoặc kiểm định mù.",
        "",
        "| Method | Macro Hit@1 | Macro R@5 | Hit@1 toàn bộ | R@5 toàn bộ | MRR@10 | Cand@40 | Cand@100 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method, metric in all_metrics.items():
        a, m = metric["ALL"], metric["MACRO"]
        lines.append(
            f"| {method} | {m['hit@1']:.1%} | {m['recall@5']:.1%} | {a['hit@1']:.1%} | {a['recall@5']:.1%} | {a['mrr@10']:.3f} | {a['cand@rerank_pool']:.1%} | {a['cand@100']:.1%} |"
        )
    lines += [
        "",
        "B0 = source hierarchy + shared hybrid/reranker; B1 = thêm graph context retrieval với ngân sách nguồn chung; B2 = thử thêm Notes vào reranker. Production B1 trả Notes riêng để đọc sau xếp hạng. Trọng số/ngân sách giữ nguyên.",
        "",
        "Lượt hiện tại chấm đủ B0 và B1. B2 đủ 940 ca nằm ở run_generic_graph_v2_final, trước khi sửa phân bổ kênh; bản B2 dở trong partial_notes_diagnostic không dùng kết luận.",
        "",
        "### Production B1 theo Phần",
        "",
        "| Phần | Số ca | Hit@1 | R@5 | R@10 | MRR@10 | Cand@40 | Cand@100 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for s, r in all_metrics[production]["sections"].items():
        lines.append(
            f"| {s} | {r['count']} | {r['hit@1']:.1%} | {r['recall@5']:.1%} | {r['recall@10']:.1%} | {r['mrr@10']:.3f} | {r['cand@rerank_pool']:.1%} | {r['cand@100']:.1%} |"
        )
    lines += [
        "",
        "### Production B1 theo Chương",
        "",
        "| Chương | Số ca | Hit@1 | R@5 | R@10 | MRR@10 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for chapter, r in all_metrics[production]["chapters"].items():
        lines.append(
            f"| {chapter} | {r['count']} | {r['hit@1']:.1%} | {r['recall@5']:.1%} | {r['recall@10']:.1%} | {r['mrr@10']:.3f} |"
        )
    lines += [
        "",
        "### Production B1 theo các partition cũ",
        "",
        "| Partition | Số ca | Hit@1 | R@5 | R@10 |",
        "|---|---:|---:|---:|---:|",
    ]
    for split, m in splits.items():
        r = m["ALL"]
        lines.append(
            f"| {split} | {r['count']} | {r['hit@1']:.1%} | {r['recall@5']:.1%} | {r['recall@10']:.1%} |"
        )
    lines += [
        "",
        "### Phễu lỗi production B1 (số ca)",
        "",
        "| Phần | Thiếu Top100 | Ngoài rerank40 | Rank >10 | Rank 6–10 | Rank 2–5 | Top1 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for s, counts in sorted(stages.items()):
        lines.append(
            "| "
            + s
            + " | "
            + " | ".join(
                str(counts[k])
                for k in (
                    "absent_top100",
                    "outside_rerank40",
                    "rank_after10",
                    "rank6to10",
                    "rank2to5",
                    "top1",
                )
            )
            + " |"
        )
    lines += [
        "",
        "### Production B1 so với B0: bootstrap ghép cặp nguyên group",
        "",
        f"Top1 thắng {paired['wins_top1']} / thua {paired['losses_top1']} ca; {paired['groups']} groups; 2.000 resamples. Point estimate và CI cùng đo query-weighted delta.",
        "",
        "| Chỉ số | Delta | CI95 |",
        "|---|---:|---:|",
    ]
    for k, r in paired["metrics"].items():
        lines.append(f"| {k} | {r['micro_delta']:.4f} | [{r['ci95'][0]:.4f}, {r['ci95'][1]:.4f}] |")
    if previous_metrics:
        lines += [
            "",
            "### Chẩn đoán phân bổ kênh và vai trò Notes",
            "",
            "Ở lượt v2 đầu, hợp nhất RRF đơn thuần với direct .75/graph .25 và k=60 khiến ứng viên chỉ có ở graph không vào Top100: điểm graph tốt nhất .25/61 nhỏ hơn direct thứ 100 .75/160. Đây là lỗi cơ hội của kênh, không phải đặc tính của một sản phẩm.",
            "",
            "Sửa bằng ngân sách kênh nguồn chung trong mọi prefix: khoảng 10 graph/40 và 25 graph/100, khử trùng và trả chỗ dư khi thiếu kết quả. Không có quota theo Chương, vật liệu, CKD/CBU hoặc danh sách mã.",
            "",
            "| B1 | Hit@1 | R@5 | Cand@100 | XIV Cand@100 |",
            "|---|---:|---:|---:|---:|",
        ]
        before, after = previous_metrics["B1"], all_metrics[production]
        for name, metric in (("Trước sửa phân bổ kênh", before), ("Hiện tại", after)):
            a = metric["ALL"]
            lines.append(
                f"| {name} | {a['hit@1']:.1%} | {a['recall@5']:.1%} | {a['cand@100']:.1%} | {metric['sections']['XIV']['cand@100']:.1%} |"
            )
        if "B2" in previous_metrics:
            b1, b2 = previous_metrics["B1"]["ALL"], previous_metrics["B2"]["ALL"]
            lines += [
                "",
                f"Ở lượt trước, thêm Notes vào reranker: Hit@1 {b1['hit@1']:.1%} → {b2['hit@1']:.1%}, R@5 {b1['recall@5']:.1%} → {b2['recall@5']:.1%}. Vì vậy B1 được chọn từ regression đã xem; Notes được giữ riêng sau xếp hạng. Chưa suy ra rằng mọi cách dùng Notes đều kém hoặc B2 hiện tại đã được đo đủ.",
            ]
    if old_metrics:
        lines += [
            "",
            "### Tham chiếu M5 cũ → B1 hiện tại",
            "",
            "Cùng bộ ca/query đã làm sạch; source views và policy khác nhau. Đây là tham chiếu lịch sử, không phải ablation chỉ thay một thành phần. Số M5 lấy từ artifact hiện có, có thể khác báo cáo đã dán trước đó.",
            "",
            "| Phạm vi | M5 Hit@1 | B1 Hit@1 | M5 R@5 | B1 R@5 |",
            "|---|---:|---:|---:|---:|",
        ]
        for scope in ("XIV", "XVI", "XVII", "ALL"):
            before = old_metrics[scope]
            after = (
                all_metrics[production]["ALL"]
                if scope == "ALL"
                else all_metrics[production]["sections"][scope]
            )
            lines.append(
                f"| {scope} | {before['hit@1']:.1%} | {after['hit@1']:.1%} | {before['recall@5']:.1%} | {after['recall@5']:.1%} |"
            )
    lines += [
        "",
        "CI mô tả tính ổn định có điều kiện trên bộ hồi quy; không chứng minh tổng quát hóa trên một miền chưa đo.",
        "",
        "## 3. QA pháp lý và latency",
        "",
        "QA dùng policy đã khóa trước nâng cấp, không retune:",
        "",
        "| Split | Số câu | Đủ primary chunks Top10 | Package đủ |",
        "|---|---:|---:|---:|",
    ]
    for s, r in qa["splits"].items():
        lines.append(
            f"| {s} | {r['count']} | {r['all_groups@10_correct']}/{r['count']} ({r['all_groups@10']:.1%}) | {r['package_all']:.1%} |"
        )
    timing = latency["overall"]
    lines += [
        "",
        f"Latency runtime B1, {timing['count']} câu cân bằng theo Phần, query/reranker caches bị bypass, model/index đã warm: p50 {timing['p50_ms']:.0f} ms, p95 {timing['p95_ms']:.0f} ms. Đo sau khi chấm B0/B1 xong, một worker RAG hoạt động. Không là startup/concurrency SLA. Latency replay trong metrics không được dùng thay con số này.",
        "",
        "## 4. Nhận xét và giới hạn",
        "",
        "Cấu hình chung đủ dùng cho luồng hỗ trợ tìm shortlist có người/reader kiểm tra nguồn. Chưa đủ căn cứ cho tự quyết định mã HS: XIV chỉ đúng Top1 dưới một nửa ca và vẫn thiếu nhiều mã đúng trong Top5. XVII có shortlist tốt hơn nhưng Top1 còn sai đáng kể. Không có ngưỡng Hit@1 chung nào chứng nhận mọi ứng dụng là đạt chuẩn.",
        "",
        "Đã kiểm chứng đường mở rộng: fixture nguồn Chương 72/Phần XV đi qua adapter → ingest PostgreSQL → routing → hybrid → graph context → reranker → metrics mà không viết bộ luật riêng. Fixture dùng model doubles, không đo accuracy của Chương 72.",
        "",
        "Điểm Retrieval trong bảng là khả năng đưa mã đúng vào shortlist, không phải độ chính xác quyết định HS. Node/edge/citation đúng scope là điều kiện dữ liệu cần kiểm tra khi thêm Chương. Chương mới thật chưa có benchmark trong lượt này.",
        "",
        "Runtime trả REQUIRES_SOURCE_REASONING. Chưa có reader pháp lý hoàn chỉnh, LLM trích điều kiện, calibration/abstention theo confidence, bộ đối chiếu số/đơn vị hoặc tự hỏi đủ mọi thuộc tính.",
        "",
        "Ưu tiên XIV: bổ sung CONTEXT_FOR đúng phạm vi/locator cho nhãn nguồn còn thiếu, kiểm tra các ca thiếu Top100 và các ca có mã đúng trong pool nhưng không được rerank. Ưu tiên XVII/Chương 87: phân tích các ca đã có mã trong Top40 nhưng xếp 2–5, giữ nhãn assembly/đặc tính có nguồn. Mọi sửa thuật toán phải dùng ngân sách/cấu hình chung và chấm toàn bộ bộ hồi quy đã khóa; không thêm danh sách mã để vá từng câu.",
        "",
        "### Kiểm chứng triển khai",
        "",
        f"{latest_checks['tests']['passed']} tests passed, {latest_checks['tests']['skipped']} skipped, gồm PostgreSQL integration."
        if latest_checks
        else "Xem verification.json để biết phạm vi kiểm thử.",
        "",
        "Ruff check/format toàn rag/scripts/tests; phạm vi Mypy xem verification.json và cleanup_validation.json; Bandit mức medium/high không phát hiện lỗi. Hai notebooks hợp lệ và code cells compile; chưa chạy toàn bộ hai notebook từ đầu đến cuối. Runtime, ingest và đánh giá được chạy bằng scripts/tests thực tế.",
        "",
        "Mypy các module mới chạy với --follow-imports=skip. Lượt theo import mặc định còn 3 lỗi typing ở rag/data.py (hai container thiếu annotation và một biến Optional dùng lại); chưa có bằng chứng full-repo typecheck sạch. Giữ nguyên code đã khóa trong benchmark; các lỗi typing được ghi ở mypy.log.",
        "",
        "## 5. Hồ sơ bàn giao",
        "",
        "- frozen_protocol.json, manifest.json, folds.json: giao thức/hashes và groups.",
        "- B0_predictions.json, B1_predictions.json và metrics.json: đủ 940 ca mỗi method, candidate pools và citation/omitted trace.",
        "- qa_runtime_regression.json, fresh_runtime_latency.json, handoff_summary.json: runtime/regression.",
        "- tests_final.log, bandit_medium_high.json, verification.json: kiểm thử và phạm vi static checks.",
        "- ../run_generic_graph_v2_final/: lượt v2 đầu đủ B0/B1/B2, dùng chẩn đoán Notes/phân bổ kênh.",
        "- ../run_generic_graph_v2/baseline/: code/config/corpus/notebooks trước sửa.",
        "- ../../../docs/retrieval/source-contract-v2.md: contract và cách thêm Chương.",
    ]
    if cleanup:
        lines += [
            "",
            "## 6. Dọn file chưa commit sau bàn giao",
            "",
            "Đã xóa hai kế hoạch trùng/lỗi thời và rag/facts.py chưa tích hợp runtime; bỏ một test chỉ kiểm tra helper đã xóa. Các kết quả Retrieval giữ nguyên vì policy, nguồn và code được hash trong benchmark không đổi.",
            "",
            f"Kiểm thử sau dọn: {cleanup['tests']['passed']} passed, {cleanup['tests']['skipped']} skipped, gồm PostgreSQL integration; giảm một test do helper được loại bỏ. Xem cleanup_validation.json và cleanup_tests.log.",
        ]
    (folder / "IMPLEMENTATION_REPORT_V2.md").write_text("\n".join(lines) + "\n")
    print(folder / "IMPLEMENTATION_REPORT_V2.md")


if __name__ == "__main__":
    main()
