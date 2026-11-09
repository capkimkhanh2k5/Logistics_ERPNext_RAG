"""Unit tests for Unified Graph Service & Dual-Engine Architecture."""

from rag.graph.age_adapter import parse_agtype
from rag.graph.service import UnifiedGraphService, get_graph_service, get_rag_graph_context


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
    # Expand Chapter 84 (using short alias or full canonical ID)
    res = svc.get_knowledge_graph(root_id="SXVI-CH-84", depth=1)

    assert res["success"] is True
    assert len(res["elements"]["nodes"]) >= 2
    parent_node = next(
        (
            n
            for n in res["elements"]["nodes"]
            if n["data"]["id"] in {"SXVI-CH-84", "tt31:SXVI-CH-84"}
        ),
        None,
    )
    assert parent_node is not None
    assert parent_node["data"]["type"] == "chapter"
    assert parent_node["data"]["children_count"] >= 80


def test_all_sections_and_chapters_connected():
    svc = get_graph_service()
    for sec in ("XIV", "XVI", "XVII"):
        res = svc.get_knowledge_graph(section=sec, limit=50)
        assert res["success"] is True
        assert len(res["elements"]["nodes"]) >= 2, f"Section {sec} should have connected nodes"
        assert len(res["elements"]["edges"]) >= 1, f"Section {sec} should have connected edges"

    for ch in ("71", "84", "85", "86", "87", "88", "89"):
        res = svc.get_knowledge_graph(chapter=ch, limit=50)
        assert res["success"] is True
        assert len(res["elements"]["nodes"]) >= 2, f"Chapter {ch} should have connected nodes"
        assert len(res["elements"]["edges"]) >= 1, f"Chapter {ch} should have connected edges"


def test_unified_graph_service_search_query():
    svc = get_graph_service()
    res = svc.get_knowledge_graph(query="8413", limit=20)

    assert res["success"] is True
    assert len(res["elements"]["nodes"]) > 0
    codes = [str(n["data"].get("code", "")) for n in res["elements"]["nodes"]]
    assert any("8413" in c for c in codes)


def test_parse_agtype_vertex_and_edge():
    raw_vertex = (
        '{"id": 844424930131969, "label": "GraphNode", '
        '"properties": {"id": "tt31:SXVI-CH-84", "code": "84", "node_type": "chapter"}}::vertex'
    )
    parsed_v = parse_agtype(raw_vertex)
    assert isinstance(parsed_v, dict)
    assert parsed_v["properties"]["id"] == "tt31:SXVI-CH-84"

    raw_edge = (
        '{"id": 1125899906842625, "label": "CONTAINS", "end_id": 2, "start_id": 1, '
        '"properties": {"relation": "CONTAINS"}}::edge'
    )
    parsed_e = parse_agtype(raw_edge)
    assert isinstance(parsed_e, dict)
    assert parsed_e["label"] == "CONTAINS"


def test_rag_graph_context_bridge():
    graph_ctx = get_rag_graph_context()
    assert len(graph_ctx.nodes) >= 7000
    ancestors = graph_ctx.ancestors("tt31:SXVI-T-8413")
    assert "tt31:SXVI-CH-84" in ancestors


def test_apache_age_graceful_fallback_when_db_down():
    # Attempting Apache AGE with an unreachable DB URL should gracefully fall back to inmemory
    svc = UnifiedGraphService(engine="apache_age")
    svc.age_adapter.db_url = "postgresql://invalid:invalid@localhost:99999/dummy"
    svc.age_adapter._is_available = None

    res = svc.get_knowledge_graph(limit=25)
    assert res["success"] is True
    assert res["engine"] == "inmemory"
    assert len(res["elements"]["nodes"]) > 0
