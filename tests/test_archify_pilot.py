"""The adapter must not turn a display projection into new evidence."""
import copy
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("archify_pilot", Path(__file__).parents[1] / "scripts/archify_pilot.py")
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


@pytest.fixture
def sample():
    ref = {"source_id": "s1", "start_line": 10, "end_line": 11}
    report = {"schema_version": "plainchange.system-flow.v2", "commit": "a" * 40,
              "working_tree_excluded": True,
              "sources": [{"id": "s1", "path": "app.py", "start_line": 10, "end_line": 11,
                           "text": 'if x < 0:\n    raise ValueError("<unsafe>")'}],
              "flows": [{"id": "flow", "title": "test", "entry_node": "a", "nodes": [
                  {"id": "a", "title": "Start", "evidence": [ref]},
                  {"id": "b", "title": "End", "evidence": [ref]}], "edges": [
                  {"id": "e1", "from": "a", "to": "b", "condition": "x < 0 and permission granted",
                   "test_input": "x=-1", "expected_result": "stop", "test_status": "not_run",
                   "runtime_status": "not_verified", "evidence": [ref]}]}],
              "connections": [], "product_review": {}, "unknowns": ["No runtime evidence"],
              "coverage": {"read_files": 1, "eligible_files": 9}}
    profile = {"flow_id": "flow", "lanes": [{"id": "main", "label": "main"}], "mainPath": ["a", "b"],
               "nodes": {k: {"lane": "main", "col": i, "type": "backend"} for i, k in enumerate(("a", "b"))},
               "edges": {"e1": {"label": "negative + authorized"}}}
    return report, profile


def test_projection_preserves_full_claims_and_never_mutates_source(sample):
    report, profile = sample
    original = copy.deepcopy(report)
    graph, evidence = pilot.convert(report, profile)
    assert report == original
    assert evidence["flow"] == original["flows"][0]
    assert evidence["unknowns"] == original["unknowns"]
    assert evidence["flow"]["edges"][0]["test_status"] == "not_run"
    assert [(e["id"], e["from"], e["to"]) for e in graph["edges"]] == [("e1", "a", "b")]
    assert "condition" not in graph["edges"][0]  # summary has an explicitly separate evidence copy


def test_profile_cannot_drop_a_branch(sample):
    report, profile = sample
    profile["edges"].clear()
    with pytest.raises(ValueError, match="cover every"):
        pilot.convert(report, profile)


def test_profile_cannot_rewire_topology(sample):
    report, profile = sample
    profile["edges"]["e1"]["to"] = "a"
    with pytest.raises(ValueError, match="topology"):
        pilot.convert(report, profile)


def test_rejects_citation_outside_saved_excerpt(sample):
    report, profile = sample
    report["flows"][0]["edges"][0]["evidence"][0]["end_line"] = 12
    with pytest.raises(ValueError, match="Out-of-range"):
        pilot.convert(report, profile)


def test_evidence_html_escapes_code_and_preserves_line_numbers(sample):
    report, profile = sample
    _, evidence = pilot.convert(report, profile)
    rendered = pilot.render_evidence(evidence)
    assert "10: if x &lt; 0:" in rendered
    assert "&lt;unsafe&gt;" in rendered
    assert "x &lt; 0 and permission granted" in rendered
    assert 'diagram.html#relation=e1' in rendered
    assert 'id="e1"' in rendered
    assert "未执行" in rendered
