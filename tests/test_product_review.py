import copy
import json

import pytest

from plainchange.model_adapter import ModelGenerationError
from plainchange.product_review import validate_review, review_markdown, challenge_product
from plainchange.source_safety import assert_safe_source
from test_system_flow import flow_repo, fixtures, FixtureProvider
from plainchange.system_flow import understand_system


def review_fixture(document):
    source = next(s for s in document["sources"] if s["kind"] == "code")
    refs = [{"source_id": source["id"], "start_line": source["start_line"], "end_line": source["end_line"]}]
    statement = {"text": "输入文字，获得处理结果。", "evidence": refs}
    return {"reader_guide": {k: copy.deepcopy(statement) for k in ("audience", "purpose", "start", "result", "limits")},
            "journey": [{"title": "提交文字", "action": "输入文字并提交", "result": "获得大写文字",
                         "flow_id": document["flows"][0]["id"], "evidence": refs}],
            "findings": [{"id": "unexpected_input", "title": "非文字输入的处理待核查", "category": "verification_gap", "priority": "medium",
                          "observation": "处理函数直接调用 upper。", "trigger": "传入数字时", "impact": "可能无法拿到处理结果。",
                          "uncertainty": "尚未核查上游是否限制了输入类型。", "verification": "检查调用者，再在隔离测试中传入整数，观察是否被拦截。",
                          "recommendation": "确认输入类型约束并记录。", "evidence": refs}],
            "glossary": [], "not_covered": ["未运行输入场景。"]}


@pytest.mark.parametrize("damage", ["source", "range", "readme_only", "duplicate", "fake_flow", "confirmed", "test_passed"])
def test_review_rejects_unsupported_evidence_and_upgrades(flow_repo, damage):
    flow, sources = fixtures(flow_repo)
    document = {**flow, "sources": sources}
    raw = review_fixture(document)
    finding = raw["findings"][0]
    if damage == "source":
        finding["evidence"][0]["source_id"] = "not-read"
    elif damage == "range":
        finding["evidence"][0]["end_line"] = 1000
    elif damage == "readme_only":
        for source in sources:
            source["kind"] = "project_declaration"
    elif damage == "duplicate":
        raw["findings"].append(copy.deepcopy(finding))
    elif damage == "fake_flow":
        raw["journey"][0]["flow_id"] = "fiction"
    elif damage == "confirmed":
        finding["category"] = "confirmed_defect"
    else:
        finding["verification_status"] = "passed"
    with pytest.raises(ModelGenerationError):
        validate_review(raw, document)


def test_review_preserves_unknowns_and_markdown_citations(flow_repo):
    flow, sources = fixtures(flow_repo)
    document = {**flow, "sources": sources}
    raw = review_fixture(document)
    result = validate_review(raw, document)
    assert result["findings"][0]["verification_status"] == "not_run"
    assert "verification_status" not in raw["findings"][0]
    assert result["human_comprehension"] == "not_tested"
    assert "app.py:" in "\n".join(review_markdown(result, sources))
    raw["findings"] = []
    assert "不代表项目没有问题" in "\n".join(review_markdown(validate_review(raw, document), sources))


def test_failed_assessment_keeps_map_and_failure_receipt(flow_repo, tmp_path):
    class BadReview(FixtureProvider):
        def complete(self, system, packet, schema, folder):
            result = super().complete(system, packet, schema, folder)
            if "reader_guide" in result:
                result["journey"][0]["flow_id"] = "not-present"
            return result
    output = tmp_path / "failed-review"
    with pytest.raises(ModelGenerationError):
        understand_system(flow_repo, output=output, provider=BadReview())
    assert (output / "system-map.validated.json").is_file()
    assert not (output / "review.html").exists()
    assert json.loads((output / "run-receipt.json").read_text(encoding="utf-8"))["status"] == "failed"


@pytest.mark.parametrize("value", ["sk-" + "a" * 32, "-----BEGIN PRIVATE KEY-----", "password = 'real-password-123456'", "ghp_" + "a" * 36])
def test_source_guard_does_not_echo_credentials(value):
    with pytest.raises(ModelGenerationError) as exc:
        assert_safe_source(value)
    assert value not in str(exc.value)


@pytest.mark.parametrize("value", ["api_key = os.getenv('API_KEY')", "password = 'your-password-here'", "access_token = '<placeholder>'"])
def test_source_guard_allows_nonliteral_configuration(value):
    assert_safe_source(value)


@pytest.mark.parametrize("damage", ["missing_disposition", "false_dismissal", "new_finding", "false_citation"])
def test_challenge_cannot_hide_or_invent_findings(flow_repo, damage):
    flow, sources = fixtures(flow_repo)
    document = {**flow, "sources": sources, "commit": "a" * 40, "project": "fixture", "coverage": {}}
    raw = review_fixture(document)
    def call(*args):
        result = {"review": copy.deepcopy(raw), "dispositions": [{"candidate_id": "unexpected_input", "decision": "retained",
                  "reason": "输入范围仍需验证。", "evidence": copy.deepcopy(raw["findings"][0]["evidence"])}]}
        if damage == "missing_disposition":
            result["dispositions"] = []
        elif damage == "false_dismissal":
            result["dispositions"][0]["decision"] = "dismissed"
        elif damage == "new_finding":
            result["review"]["findings"][0]["id"] = "invented"
        else:
            result["dispositions"][0]["evidence"][0]["source_id"] = "not-read"
        return result
    with pytest.raises(ModelGenerationError):
        challenge_product(document, raw, call)


def test_challenge_reads_counterevidence_and_records_withdrawal(flow_repo):
    from conftest import run_git
    from plainchange.system_flow import source_inventory
    flow, sources = fixtures(flow_repo)
    # Start with only the caller excerpt; request the implementation to challenge it.
    document = {**flow, "sources": sources[:1], "commit": run_git(flow_repo, "rev-parse", "HEAD"), "project": "fixture",
                "coverage": {"source_bytes": len(sources[0]["text"].encode()), "denied_reads": []}}
    raw = review_fixture(document)
    inventory, _ = source_inventory(flow_repo, document["commit"])
    calls = []
    def call(label, instruction, packet, schema):
        calls.append(label)
        if label == "review-read":
            return {"reads": [{"path": "worker.py", "start_line": 1}]} if packet["round"] == 1 else {"reads": []}
        final = copy.deepcopy(raw)
        final["findings"] = []
        source = next(s for s in packet["sources"] if s["path"] == "worker.py")
        return {"review": final, "dispositions": [{"candidate_id": "unexpected_input", "decision": "dismissed",
                "reason": "本次资料不足以将约定输入以外的行为当成缺陷。", "evidence": [{"source_id": source["id"], "start_line": 1, "end_line": 2}]}]}
    result = challenge_product(document, raw, call, repository=flow_repo, inventory=inventory)
    assert result["findings"] == [] and len(raw["findings"]) == 1
    assert result["challenge"]["dispositions"][0]["decision"] == "dismissed"
    assert document["coverage"]["read_files"] == 2
    assert document["coverage"]["read_excerpts"] == 2
    assert calls == ["review-read", "review-read", "product-review-check"]


def test_sensitive_source_is_withheld_before_model_and_packet_persistence(flow_repo, tmp_path):
    from conftest import run_git
    credential = "sk-" + "z" * 40
    (flow_repo / "app.py").write_text("api_key = '" + credential + "'\n", encoding="utf-8")
    run_git(flow_repo, "add", "app.py")
    run_git(flow_repo, "commit", "-m", "credential regression fixture")
    class InspectProvider:
        name = "inspect-privacy-boundary"
        def complete(self, system, packet, schema, folder):
            assert credential not in json.dumps(packet)
            if packet["round"] == 1:
                return {"reads": [{"path": "app.py", "start_line": 1}]}
            return {"reads": []}
    output = tmp_path / "blocked"
    with pytest.raises(ModelGenerationError, match="未读取到代码"):
        understand_system(flow_repo, provider=InspectProvider(), output=output)
    for path in output.rglob("*.json"):
        assert credential not in path.read_text(encoding="utf-8")
