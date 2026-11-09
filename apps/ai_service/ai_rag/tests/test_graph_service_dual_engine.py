"""Unit tests for Unified Graph Service & Dual-Engine Architecture."""

import pytest
from rag.graph.service import UnifiedGraphService, get_graph_service


def test_unified_graph_service_inmemory_loads_successfully():
    svc = UnifiedGraphService(engine="inmemory")
    res = svc.get_knowledge_graph(limit=40)

    assert res["success"] is True
    assert res["engine"] == "inmemory"
    assert "elements" in res
    assert len(res["elements"]["nodes"]) > 0
    assert len(res["elements"]["edges"]) > 0

    # Ensure Root node or sections exist
    node_ids = {n["data"]["id"] for n in res["elements"]["nodes"]}
    assert "ROOT_CUSTOMS_TARIFF" in node_ids or any("SXVI" in nid for nid in node_ids)


def test_unified_graph_service_lazy_expansion():
    svc = get_graph_service()
    # Expand Chapter 84
    res = svc.get_knowledge_graph(root_id="SXVI-CH-84", depth=1)

    assert res["success"] is True
    assert len(res["elements"]["nodes"]) >= 2
    parent_node = next(
        (n for n in res["elements"]["nodes"] if n["data"]["id"] == "SXVI-CH-84"), None
    )
    assert parent_node is not None
    assert parent_node["data"]["type"] == "chapter"


def test_unified_graph_service_search_query():
    svc = get_graph_service()
    res = svc.get_knowledge_graph(query="8413", limit=20)

    assert res["success"] is True
    assert len(res["elements"]["nodes"]) > 0
    # Must contain nodes related to 8413
    codes = [str(n["data"].get("code", "")) for n in res["elements"]["nodes"]]
    assert any("8413" in c for c in codes)


def test_apache_age_graceful_fallback_when_db_down():
    # Attempting Apache AGE with an unreachable DB URL should gracefully fall back to inmemory
    svc = UnifiedGraphService(engine="apache_age")
    # Temporarily point to invalid port
    svc.age_adapter.db_url = "postgresql://invalid:invalid@localhost:99999/dummy"
    svc.age_adapter._is_available = None

    res = svc.get_knowledge_graph(limit=25)
    assert res["success"] is True
    assert res["engine"] == "inmemory"
    assert len(res["elements"]["nodes"]) > 0
