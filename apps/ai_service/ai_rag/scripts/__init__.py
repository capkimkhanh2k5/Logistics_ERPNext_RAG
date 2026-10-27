"""Scripts module for aiAgent."""

import importlib
import sys

# Subpackage convenience imports & backward compatibility aliases
_SCRIPT_ALIASES = {
    "run_retrieval_experiment": "scripts.benchmark.run_retrieval_experiment",
    "tune_shared_retrieval": "scripts.benchmark.tune_shared_retrieval",
    "benchmark_pdf_rerankers": "scripts.benchmark.benchmark_pdf_rerankers",
    "benchmark_unified_retrieval": "scripts.benchmark.benchmark_unified_retrieval",
    "finalize_retrieval_report": "scripts.benchmark.finalize_retrieval_report",
    "diagnose_retrieval_flow": "scripts.benchmark.diagnose_retrieval_flow",
    "measure_fresh_runtime_latency": "scripts.benchmark.measure_fresh_runtime_latency",
    "audit_pdf_sources": "scripts.ingestion.audit_pdf_sources",
    "build_pdf_graph": "scripts.ingestion.build_pdf_graph",
    "register_legal_sources": "scripts.ingestion.register_legal_sources",
    "prepare_dev_test": "scripts.maintenance.prepare_dev_test",
    "run_runtime_regression": "scripts.maintenance.run_runtime_regression",
    "init_cliproxyapi": "scripts.maintenance.init_cliproxyapi",
}

for _old, _new in _SCRIPT_ALIASES.items():
    _full = f"scripts.{_old}"
    if _full not in sys.modules:
        try:
            sys.modules[_full] = importlib.import_module(_new)
        except Exception:
            pass
