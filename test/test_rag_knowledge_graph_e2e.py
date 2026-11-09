"""End-to-End Acceptance Tests for Customs Knowledge Graph & Cytoscape.js Integration.

Validates:
1. UnifiedGraphService & In-Memory / Apache AGE Dual-Run Engine
2. Lazy Loading node expansion
3. Search filtering
4. Whitelisted Frappe API endpoint contract
5. UI template elements & Cytoscape DOM container integration
"""

import os
import sys
from pathlib import Path
import pytest

BENCH_ROOT = Path(__file__).resolve().parent.parent
AI_RAG_PATH = BENCH_ROOT / "apps" / "ai_service" / "ai_rag"
LOGISTICS_PATH = BENCH_ROOT / "apps" / "logistics_wizard"

sys.path.insert(0, str(AI_RAG_PATH))
sys.path.insert(0, str(LOGISTICS_PATH))


def test_unified_graph_service_initialization():
    from rag.graph.service import get_graph_service

    svc = get_graph_service()
    data = svc.get_knowledge_graph(limit=50)

    assert data["success"] is True
    assert data["engine"] in {"inmemory", "apache_age"}
    elements = data["elements"]
    assert "nodes" in elements and len(elements["nodes"]) > 0
    assert "edges" in elements and len(elements["edges"]) > 0

    # Validate node schema for Cytoscape.js
    sample_node = elements["nodes"][0]
    assert "data" in sample_node
    assert "id" in sample_node["data"]
    assert "label" in sample_node["data"]
    assert "type" in sample_node["data"]

    # Validate edge schema for Cytoscape.js
    sample_edge = elements["edges"][0]
    assert "data" in sample_edge
    assert "source" in sample_edge["data"]
    assert "target" in sample_edge["data"]


def test_graph_lazy_loading_expansion():
    from rag.graph.service import get_graph_service

    svc = get_graph_service()
    # Expand Chapter 84
    res = svc.get_knowledge_graph(root_id="SXVI-CH-84", depth=1, limit=50)
    assert res["success"] is True

    node_ids = {n["data"]["id"] for n in res["elements"]["nodes"]}
    assert "SXVI-CH-84" in node_ids or "tt31:SXVI-CH-84" in node_ids
    assert len(node_ids) > 1, "Expanded node must include its child headings"


def test_graph_search_by_code_and_text():
    from rag.graph.service import get_graph_service

    svc = get_graph_service()
    res = svc.get_knowledge_graph(query="8471", limit=30)
    assert res["success"] is True
    assert len(res["elements"]["nodes"]) > 0

    codes_or_labels = [
        str(n["data"].get("code", "")) + " " + str(n["data"].get("label", ""))
        for n in res["elements"]["nodes"]
    ]
    assert any("8471" in text for text in codes_or_labels)


def test_whitelisted_frappe_api_get_knowledge_graph():
    from logistics_wizard.api import get_knowledge_graph

    api_res = get_knowledge_graph(chapter="84", depth=1, limit=20)
    assert api_res["success"] is True
    assert "elements" in api_res
    assert len(api_res["elements"]["nodes"]) > 0


def test_ui_template_and_js_integration():
    for page_dir in ("rag_knowledge_base", "rag_admin_center"):
        html_path = (
            LOGISTICS_PATH
            / "logistics_wizard"
            / "page"
            / page_dir
            / f"{page_dir}.html"
        )
        js_path = (
            LOGISTICS_PATH
            / "logistics_wizard"
            / "page"
            / page_dir
            / f"{page_dir}.js"
        )
        css_path = (
            LOGISTICS_PATH
            / "logistics_wizard"
            / "page"
            / page_dir
            / f"{page_dir}.css"
        )

        # 1. HTML checks
        html_content = html_path.read_text(encoding="utf-8")
        assert 'data-tab="graph"' in html_content
        assert 'id="btn-tab-graph"' in html_content
        assert 'id="tab-pane-graph"' in html_content
        assert 'id="rag-cytoscape-canvas"' in html_content
        assert 'id="rag-graph-node-details"' in html_content
        assert 'id="btn-node-expand-children"' in html_content
        for ch in ("71", "84", "85", "86", "87", "88", "89"):
            assert f'value="{ch}"' in html_content

        # 2. JS checks
        js_content = js_path.read_text(encoding="utf-8")
        assert "init_or_refresh_graph" in js_content
        assert "ensure_cytoscape" in js_content
        assert "logistics_wizard.api.get_knowledge_graph" in js_content
        assert "render_cytoscape" in js_content
        assert "expand_selected_node" in js_content

        # 3. CSS checks
        css_content = css_path.read_text(encoding="utf-8")
        assert "#tab-pane-graph" in css_content
        assert "#rag-cytoscape-canvas" in css_content
        assert ".rag-graph-canvas-wrapper" in css_content
