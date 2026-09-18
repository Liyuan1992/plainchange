from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from conftest import run_git
from plainchange.model_adapter import ModelGenerationError
from plainchange.system_flow import (
    create_flow_output, read_excerpt, source_inventory, understand_system,
    validate_flow, render_flow,
)


@pytest.fixture
def flow_repo(tmp_path):
    repo = tmp_path / "source"
    repo.mkdir()
    run_git(repo, "init", "-b", "main")
    run_git(repo, "config", "user.email", "test@example.invalid")
    run_git(repo, "config", "user.name", "Test")
    (repo / "app.py").write_text("from worker import process\n\ndef submit(value):\n    if not value:\n        return 'invalid'\n    return process(value)\n", encoding="utf-8")
    (repo / "worker.py").write_text("def process(value):\n    return value.upper()\n", encoding="utf-8")
    (repo / "README.md").write_text("This app processes input.\n", encoding="utf-8")
    (repo / "credentials.py").write_text("DO_NOT_READ = 'secret fixture'\n", encoding="utf-8")
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-m", "single version")
    return repo


def raw_map(sources):
    app = next(s for s in sources if s["path"] == "app.py")
    worker = next(s for s in sources if s["path"] == "worker.py")
    def ref(source, start, end):
        return [{"source_id": source["id"], "start_line": start, "end_line": end}]
    def node(id, title, kind, refs):
        return {"id": id, "title": title, "kind": kind, "description": "检查输入并确定下一步。",
                "inputs": "用户输入", "outputs": "处理结果", "state_changes": "无持久化写入", "evidence": refs}
    def edge(id, target, condition, refs):
        return {"id": id, "from": "check", "to": target, "condition": condition,
                "explanation": "根据是否提供内容选择返回值。", "evidence": refs,
                "test_input": "提交空字符串" if target == "invalid" else "提交 hello",
                "expected_result": "invalid" if target == "invalid" else "HELLO"}
    return {"title": "任务处理", "summary": "检查输入并调用工作函数。", "interview_summary": "系统由输入检查与内容处理两个部分构成。",
            "unknowns": ["未执行运行验证"], "flows": [{"id": "submit", "title": "提交任务", "purpose": "处理输入", "entry_node": "check",
            "nodes": [node("check", "输入是否为空", "decision", ref(app, 3, 4)), node("invalid", "返回无效", "end", ref(app, 5, 5)),
                      node("process", "处理有效输入", "end", ref(worker, 1, 2))],
            "edges": [edge("empty", "invalid", "输入为空", ref(app, 4, 5)), edge("valid", "process", "输入不为空", ref(app, 4, 6))]}]}


class FixtureProvider:
    name = "test-fixture-not-a-model"

    def complete(self, system, packet, schema, folder):
        folder.mkdir(parents=True)
        if "reads" in schema["properties"]:
            if packet["round"] == 1:
                assert "secret fixture" not in json.dumps(packet)
                assert not any(f["path"] == "credentials.py" for f in packet["files"])
                return {"reads": [{"path": "app.py", "start_line": 1}]}
            if packet["round"] == 2:
                assert packet["sources"][0]["branch_syntax"][0]["kind"] == "If"
                return {"reads": [{"path": "worker.py", "start_line": 1}]}
            return {"reads": []}
        return {**raw_map(packet["sources"]), "connections": []}


def test_single_commit_cross_file_exploration_and_target_preservation(flow_repo, tmp_path):
    (flow_repo / "worker.py").write_text("uncommitted code must not be read", encoding="utf-8")
    before = run_git(flow_repo, "status", "--porcelain")
    result = understand_system(flow_repo, provider=FixtureProvider(), output=tmp_path / "report")
    report = json.loads(Path(result["system_flow"]).read_text(encoding="utf-8"))
    assert report["working_tree_excluded"] is True
    assert report["coverage"]["read_files"] == 2
    assert report["coverage"]["complete"] is False
    assert "uncommitted code" not in json.dumps(report)
    assert report["flows"][0]["edges"][0]["test_status"] == "not_run"
    assert run_git(flow_repo, "status", "--porcelain") == before
    assert Path(result["review_html"]).is_file()
    assert "```mermaid" in Path(result["markdown"]).read_text(encoding="utf-8")
    receipt = json.loads((tmp_path / "report/run-receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "succeeded"
    assert len(receipt["requests"]) == 4


def test_output_never_overwrites_target_or_prior_result(flow_repo, tmp_path):
    with pytest.raises(ModelGenerationError, match="之外"):
        create_flow_output(flow_repo, output=flow_repo / "map")
    report = tmp_path / "old-report"
    report.mkdir()
    (report / "review.html").write_text("keep")
    with pytest.raises(ModelGenerationError, match="已有文件"):
        create_flow_output(flow_repo, output=report)
    assert (report / "review.html").read_text() == "keep"


def fixtures(flow_repo):
    commit = run_git(flow_repo, "rev-parse", "HEAD")
    files, _ = source_inventory(flow_repo, commit)
    sources = [read_excerpt(flow_repo, f, 1) for f in files if f["path"] in {"app.py", "worker.py"}]
    return raw_map(sources), sources


@pytest.mark.parametrize("damage", ["missing_source", "outside_excerpt", "fake_target", "disconnected", "one_branch", "test_passed", "readme_only"])
def test_rejects_hallucinated_evidence_and_graphs(flow_repo, damage):
    raw, sources = fixtures(flow_repo)
    flow = raw["flows"][0]
    if damage == "missing_source":
        flow["nodes"][0]["evidence"][0]["source_id"] = "made-up"
    elif damage == "outside_excerpt":
        flow["edges"][0]["evidence"][0]["end_line"] = 900
    elif damage == "fake_target":
        flow["edges"][0]["to"] = "missing"
    elif damage == "disconnected":
        extra = copy.deepcopy(flow["nodes"][1]); extra["id"] = "disconnected"
        flow["nodes"].append(extra)
    elif damage == "one_branch":
        flow["edges"] = flow["edges"][:1]; flow["nodes"] = flow["nodes"][:2]
    elif damage == "test_passed":
        flow["edges"][0]["test_status"] = "passed"
    else:
        sources[0]["kind"] = "project_declaration"
    with pytest.raises(ModelGenerationError):
        validate_flow(raw, sources)


def test_untrusted_html_is_data_not_script(flow_repo):
    raw, sources = fixtures(flow_repo)
    raw["title"] = '</script><img src=x onerror="alert(1)">'
    document = validate_flow(raw, sources)
    document.update(sources=sources, commit="a" * 40, project="fixture", coverage={})
    rendered = render_flow(document)
    assert "</script><img" not in rendered
    assert "\\u003c/script>" in rendered
    assert "connect-src 'none'" in rendered


def test_cross_excerpt_citations_split_only_existing_same_blob_lines(flow_repo):
    raw, sources = fixtures(flow_repo)
    app = next(s for s in sources if s["path"] == "app.py")
    tail = copy.deepcopy(app)
    tail.update(id="app-tail", start_line=5, text="\n".join(app["text"].splitlines()[4:]))
    app.update(end_line=4, text="\n".join(app["text"].splitlines()[:4]))
    # Keep the end node's entirely-tail citation correct; exercise ranges that
    # actually cross the supplied excerpt boundary on both edges.
    raw["flows"][0]["nodes"][1]["evidence"][0]["source_id"] = tail["id"]
    original = copy.deepcopy(raw)
    normalized = validate_flow(raw, [*sources, tail])
    refs = normalized["flows"][0]["edges"][1]["evidence"]
    assert [(r["start_line"], r["end_line"]) for r in refs] == [(4, 4), (5, 6)]
    assert len(normalized["citation_normalizations"]) == 2
    assert raw == original
    # An unread gap or a different blob must not become supporting evidence.
    tail["start_line"] = 6
    with pytest.raises(ModelGenerationError):
        validate_flow(raw, [*sources, tail])
    tail["start_line"] = 5
    tail["blob"] = "different-version"
    with pytest.raises(ModelGenerationError):
        validate_flow(raw, [*sources, tail])


def test_arbitrary_model_file_reads_fail_and_leave_failure_receipt(flow_repo, tmp_path):
    class InvalidProvider:
        name = "invalid-fixture"
        def complete(self, *args):
            return {"reads": [{"path": "../auth.json", "start_line": 1}]}
    output = tmp_path / "failure"
    with pytest.raises(ModelGenerationError, match="清单之外"):
        understand_system(flow_repo, output=output, provider=InvalidProvider())
    receipt = json.loads((output / "run-receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "failed"
    assert not (output / "review.html").exists()


def test_guided_system_job_uses_same_pipeline_and_serves_only_completed_report(flow_repo, tmp_path, monkeypatch):
    import threading
    import time
    import urllib.request
    import plainchange.system_flow as module
    from plainchange.onboarding import OnboardingServer, OnboardingState
    monkeypatch.setattr("plainchange.flow_provider.codex_status", lambda: {"chatgpt": True})
    original = module.understand_system
    monkeypatch.setattr(module, "understand_system", lambda *a, **kw: original(*a, provider=FixtureProvider(), **kw))
    server = OnboardingServer(("127.0.0.1", 0), OnboardingState(token="test-token"))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    root = f"http://127.0.0.1:{server.server_port}"
    try:
        payload = json.dumps({"repository": str(flow_repo), "output": str(tmp_path / "http-report")}).encode()
        request = urllib.request.Request(root + "/api/understand", data=payload, headers={"Content-Type": "application/json", "X-PlainChange-Token": "test-token"})
        with urllib.request.urlopen(request) as response:
            assert response.status == 202
            job_id = json.load(response)["job"]["id"]
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            request = urllib.request.Request(root + "/api/jobs/" + job_id, headers={"X-PlainChange-Token": "test-token"})
            with urllib.request.urlopen(request) as response:
                job = json.load(response)["job"]
            if job["status"] in {"succeeded", "failed"}:
                break
            time.sleep(.05)
        assert job["status"] == "succeeded", job
        with urllib.request.urlopen(root + job["report_url"] + "?token=test-token") as response:
            assert "系统流程地图" in response.read().decode("utf-8")
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)


def test_large_file_is_readable_and_function_index_locates_deep_code(flow_repo):
    from plainchange.system_flow import source_symbols
    body = '# filler padding\n' * 13000 + 'def deep_branch(value):\n    if value:\n        return 1\n    return 0\n'
    (flow_repo / 'large.py').write_text(body, encoding='utf-8')
    run_git(flow_repo, 'add', 'large.py')
    run_git(flow_repo, 'commit', '-m', 'large source')
    files, _ = source_inventory(flow_repo, run_git(flow_repo, 'rev-parse', 'HEAD'))
    record = next(f for f in files if f['path'] == 'large.py')
    assert record['bytes'] > 180000
    first = read_excerpt(flow_repo, record, 1)
    symbol = next(s for s in first['symbols'] if s['name'] == 'deep_branch')
    deep = read_excerpt(flow_repo, record, symbol['start_line'])
    assert 'if value:' in deep['text']
    assert deep['branch_syntax'][0]['kind'] == 'If'
    assert len(first['text'].splitlines()) == 160
    assert source_symbols('const submit = async (value) => {\n}', 'ui.js')[0]['name'] == 'submit'


def test_cross_flow_connections_validate_nodes_and_evidence(flow_repo):
    from plainchange.system_flow import flow_markdown
    raw, sources = fixtures(flow_repo)
    second = copy.deepcopy(raw['flows'][0]); second['id'] = 'confirmation'
    raw['flows'].append(second)
    ref = copy.deepcopy(raw['flows'][0]['nodes'][0]['evidence'])
    raw['connections'] = [{'id': 'resume', 'from_flow': 'submit', 'from_node': 'process',
        'to_flow': 'confirmation', 'to_node': 'check', 'kind': 'next_request',
        'condition': 'next input', 'explanation': 'separate request', 'evidence': ref}]
    result = validate_flow(raw, sources)
    assert result['connections'][0]['runtime_status'] == 'not_verified'
    result.update(commit='a' * 40, sources=sources, coverage={'read_files': 2, 'eligible_files': 3})
    assert '等待下一轮请求' in flow_markdown(result)
    for field, value in [('to_node', 'missing'), ('to_flow', 'missing'), ('kind', 'invented')]:
        damaged = copy.deepcopy(raw); damaged['connections'][0][field] = value
        with pytest.raises(ModelGenerationError):
            validate_flow(damaged, sources)
    damaged = copy.deepcopy(raw); damaged['connections'][0]['evidence'][0]['end_line'] = 99999
    with pytest.raises(ModelGenerationError):
        validate_flow(damaged, sources)
    damaged = copy.deepcopy(raw); damaged['connections'].append(copy.deepcopy(raw['connections'][0]))
    with pytest.raises(ModelGenerationError):
        validate_flow(damaged, sources)


def test_reference_repair_is_bounded_preserves_claims_and_raw(flow_repo, tmp_path):
    from plainchange.system_flow import repair_flow_references
    raw, sources = fixtures(flow_repo)
    expected = copy.deepcopy(raw['flows'][0]['edges'][0]['evidence'])
    raw['flows'][0]['edges'][0]['evidence'][0]['end_line'] = 1
    original = copy.deepcopy(raw)
    calls = []
    def correct(label, instruction, packet, schema):
        calls.append(packet)
        return {'corrections': [{'key': 'submit/edges/empty', 'evidence': expected}]}
    fixed = repair_flow_references(raw, sources, correct)
    assert raw == original and len(calls) == 1
    assert fixed['flows'][0]['edges'][0]['condition'] == raw['flows'][0]['edges'][0]['condition']
    with pytest.raises(ModelGenerationError):
        repair_flow_references(raw, sources, lambda *args: {'corrections': [{'key': 'submit/edges/empty', 'evidence': []}]})
    class RepairProvider(FixtureProvider):
        def complete(self, system, packet, schema, folder):
            if 'corrections' in schema['properties']:
                folder.mkdir(parents=True)
                return correct(None, None, packet, schema)
            value = super().complete(system, packet, schema, folder)
            if 'flows' in value:
                value['flows'][0]['edges'][0]['evidence'][0]['end_line'] = 1
            return value
    output = tmp_path/'repaired-report'
    understand_system(flow_repo, provider=RepairProvider(), output=output)
    assert json.loads((output/'system-flow.raw.json').read_text(encoding='utf-8'))['flows'][0]['edges'][0]['evidence'][0]['end_line'] == 1
    receipt = json.loads((output/'run-receipt.json').read_text(encoding='utf-8'))
    assert receipt['status'] == 'succeeded' and 'initial_validation_error' in receipt
    assert receipt['requests'][-1]['stage'] == 'repair-references'
    assert (output/'system-flow.repaired.json').exists()
