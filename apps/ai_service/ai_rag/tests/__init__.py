"""Tests package for aiAgent.

Provides backward-compatibility aliases in sys.modules so tests importing
`from tests.test_xyz import ...` will automatically resolve to the reorganized
subpackages (retrieval, generation, workflow, ingestion, core).
"""

import importlib
import sys

_TEST_ALIASES = {
    # Workflow
    "test_goal_workflow": "tests.workflow.test_goal_workflow",
    "test_goal_reselection": "tests.workflow.test_goal_reselection",
    "test_obligation_flow": "tests.workflow.test_obligation_flow",
    "test_generic_proof_engine": "tests.workflow.test_generic_proof_engine",
    "test_proof_contract": "tests.workflow.test_proof_contract",
    "test_contract_transport_sources": "tests.workflow.test_contract_transport_sources",
    "test_condition_protocol": "tests.workflow.test_condition_protocol",
    "test_legal_evidence": "tests.workflow.test_legal_evidence",
    "test_discriminating_facts": "tests.workflow.test_discriminating_facts",
    "test_quantitative_grounding": "tests.workflow.test_quantitative_grounding",
    "test_evidence_recovery": "tests.workflow.test_evidence_recovery",
    "test_final_contracts": "tests.workflow.test_final_contracts",
    # Retrieval
    "test_candidate_disambiguation": "tests.retrieval.test_candidate_disambiguation",
    "test_candidate_ranking": "tests.retrieval.test_candidate_ranking",
    "test_conditional_candidates": "tests.retrieval.test_conditional_candidates",
    "test_database": "tests.retrieval.test_database",
    "test_reranker_batch_cache": "tests.retrieval.test_reranker_batch_cache",
    "test_retrieval_enhancements": "tests.retrieval.test_retrieval_enhancements",
    "test_shared_tuning": "tests.retrieval.test_shared_tuning",
    "test_unified_retrieval": "tests.retrieval.test_unified_retrieval",
    # Generation
    "test_analysis_review": "tests.generation.test_analysis_review",
    "test_decision_review": "tests.generation.test_decision_review",
    "test_decision_review_flow": "tests.generation.test_decision_review_flow",
    "test_generation": "tests.generation.test_generation",
    "test_generation_boundaries": "tests.generation.test_generation_boundaries",
    "test_generation_hardening": "tests.generation.test_generation_hardening",
    "test_generation_scenarios": "tests.generation.test_generation_scenarios",
    "test_generation_timings": "tests.generation.test_generation_timings",
    "test_grouped_candidate_reviews": "tests.generation.test_grouped_candidate_reviews",
    "test_llm_routing": "tests.generation.test_llm_routing",
    "test_model_context_packing": "tests.generation.test_model_context_packing",
    "test_registry_generation": "tests.generation.test_registry_generation",
    "test_review_diagnostics": "tests.generation.test_review_diagnostics",
    "test_review_refinements": "tests.generation.test_review_refinements",
    "test_token_budget": "tests.generation.test_token_budget",
    # Ingestion
    "test_corpus_scope_validation": "tests.ingestion.test_corpus_scope_validation",
    "test_pdf_graph": "tests.ingestion.test_pdf_graph",
    "test_pdf_provenance_relocation": "tests.ingestion.test_pdf_provenance_relocation",
    "test_pdf_wording": "tests.ingestion.test_pdf_wording",
    # Core
    "test_context_compaction": "tests.core.test_context_compaction",
    "test_conversation": "tests.core.test_conversation",
    "test_demo_rag": "tests.core.test_demo_rag",
    "test_hs_dev_test": "tests.core.test_hs_dev_test",
    "test_pipeline": "tests.core.test_pipeline",
    "test_prompt_governance": "tests.core.test_prompt_governance",
    "test_query_planning": "tests.core.test_query_planning",
    "test_quyet_experiments": "tests.core.test_quyet_experiments",
    "test_quyet_full_experiments": "tests.core.test_quyet_full_experiments",
    "test_settings": "tests.core.test_settings",
}

for _old_name, _new_path in _TEST_ALIASES.items():
    _full_old = f"tests.{_old_name}"
    if _full_old not in sys.modules:
        try:
            sys.modules[_full_old] = importlib.import_module(_new_path)
        except Exception:
            pass
