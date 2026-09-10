from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from .models import ManifestError, canonical_json_bytes, sha256_bytes

SOFTWARE_CONTROL_SCHEMA = "change-passport.software-control.v1"
QUESTION_IDS = (
    "software_operation",
    "current_change",
    "affected_people",
    "unknowns",
    "next_verification",
)
OWNER_VIEW_FIELDS = (
    "meaning",
    "visible_result",
    "current_change",
    "affected_people",
)
WORKFLOW_EVIDENCE_STATES = {
    "declared_and_code_supported",
    "partially_supported",
    "declared_only",
    "code_discovered",
    "generated_candidate",
}
WORKFLOW_ORDER_STATES = {
    "code_supported",
    "partially_supported",
    "conflicting",
    "unverified",
}


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ManifestError(f"{label} must be an object")
    return value


def _sequence(value: Any, label: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise ManifestError(f"{label} must be an array")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{label} must be a non-empty string")
    return value.strip()


def _text_list(value: Any, label: str, *, allow_empty: bool = True) -> list[str]:
    result = [_text(item, f"{label} item") for item in _sequence(value, label)]
    if not allow_empty and not result:
        raise ManifestError(f"{label} must not be empty")
    return result


def _validate_basis(value: Any, label: str) -> Mapping[str, Any]:
    basis = _mapping(value, label)
    for field in ("claim_ids", "evidence_ids", "component_ids", "source_refs"):
        _text_list(basis.get(field), f"{label}.{field}")
    return basis


def _validate_workflow_evidence(value: Mapping[str, Any], label: str) -> None:
    if "evidence_status" not in value:
        return
    status = _text(value.get("evidence_status"), f"{label}.evidence_status")
    if status not in WORKFLOW_EVIDENCE_STATES:
        raise ManifestError(f"{label}.evidence_status is unsupported")
    _text(value.get("evidence_label"), f"{label}.evidence_label")
    _text(value.get("evidence_note"), f"{label}.evidence_note")
    _text_list(value.get("source_refs"), f"{label}.source_refs")


def _validate_source_binding(
    source: Mapping[str, Any],
    *,
    brief: Mapping[str, Any] | None,
    review: Mapping[str, Any] | None,
    system_architecture: Mapping[str, Any] | None,
) -> None:
    if brief is not None:
        if source.get("brief_identity") != brief.get("brief_identity"):
            raise ManifestError("software control brief identity does not match the validated brief")
        change = _mapping(source.get("change_identity"), "software control source change_identity")
        brief_change = _mapping(brief.get("change"), "validated brief change")
        expected = {
            "base_commit": brief_change.get("base_commit"),
            "head_commit": brief_change.get("head_commit"),
            "patch_sha256": brief_change.get("patch_sha256"),
        }
        if dict(change) != expected:
            raise ManifestError("software control change identity does not match the validated brief")
    if review is not None and source.get("review_identity") != review.get("review_identity"):
        raise ManifestError("software control review identity does not match the beginner review")
    if system_architecture is not None:
        working_map = _mapping(source.get("_working_map"), "software control working_map")
        declared = _mapping(working_map.get("source"), "software control working_map.source")
        target_profile = _mapping(system_architecture.get("target_profile"), "system architecture target_profile")
        if declared.get("profile_sha256") != target_profile.get("profile_sha256"):
            raise ManifestError("software control target profile does not match the architecture snapshot")


def validate_software_control(
    value: Any,
    *,
    brief: Mapping[str, Any] | None = None,
    review: Mapping[str, Any] | None = None,
    system_architecture: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    document = _mapping(value, "software control")
    if document.get("schema_version") != SOFTWARE_CONTROL_SCHEMA:
        raise ManifestError("software control schema is invalid")
    _text(document.get("sample_id"), "software control sample_id")
    if brief is not None and document.get("sample_id") != brief.get("sample_id"):
        raise ManifestError("software control sample_id does not match the validated brief")
    product = _mapping(document.get("product"), "software control product")
    _text(product.get("name"), "software control product.name")
    _text(product.get("purpose"), "software control product.purpose")

    summary = _mapping(document.get("first_screen_summary"), "software control first_screen_summary")
    _text(summary.get("headline"), "software control first_screen_summary.headline")
    _text(summary.get("internal_concept_label"), "software control first_screen_summary.internal_concept_label")
    for key in ("confirmed_change", "user_impact", "residual_risk", "owner_action"):
        statement = _mapping(summary.get(key), f"software control first_screen_summary.{key}")
        _text(statement.get("text"), f"software control first_screen_summary.{key}.text")
        _text(statement.get("state_label"), f"software control first_screen_summary.{key}.state_label")
        _text(statement.get("state_explanation"), f"software control first_screen_summary.{key}.state_explanation")
        _validate_basis(statement.get("basis"), f"software control first_screen_summary.{key}.basis")

    questions = _sequence(document.get("five_questions"), "software control five_questions")
    if tuple(item.get("id") for item in questions if isinstance(item, Mapping)) != QUESTION_IDS:
        raise ManifestError("software control five_questions must use the required order")
    for index, raw_question in enumerate(questions):
        question = _mapping(raw_question, f"software control five_questions[{index}]")
        _text(question.get("question"), f"software control five_questions[{index}].question")
        _text(question.get("answer"), f"software control five_questions[{index}].answer")
        _text(question.get("state_label"), f"software control five_questions[{index}].state_label")
        _validate_basis(question.get("basis"), f"software control five_questions[{index}].basis")
        _mapping(question.get("details"), f"software control five_questions[{index}].details")

    working_map = _mapping(document.get("working_map"), "software control working_map")
    _text(working_map.get("title"), "software control working_map.title")
    _text(working_map.get("description"), "software control working_map.description")
    screen_summary = _mapping(working_map.get("screen_summary"), "software control working_map.screen_summary")
    for key in ("headline", "overview", "boundary_label"):
        _text(screen_summary.get(key), f"software control working_map.screen_summary.{key}")
    _text(working_map.get("boundary_note"), "software control working_map.boundary_note")
    if "order_status" in working_map:
        order_status = _text(
            working_map.get("order_status"), "software control working_map.order_status"
        )
        if order_status not in WORKFLOW_ORDER_STATES:
            raise ManifestError("software control working_map.order_status is unsupported")
        _text(working_map.get("order_label"), "software control working_map.order_label")
        _text(working_map.get("order_note"), "software control working_map.order_note")
        _text_list(
            working_map.get("order_source_refs"),
            "software control working_map.order_source_refs",
        )

    nodes = _sequence(working_map.get("nodes"), "software control working_map.nodes")
    available_group_ids = {
        group.get("group_id")
        for group in (system_architecture or {}).get("groups", [])
        if isinstance(group, Mapping)
    }
    node_ids: set[str] = set()
    changed_nodes = 0
    for index, raw_node in enumerate(nodes):
        node = _mapping(raw_node, f"software control working_map.nodes[{index}]")
        node_id = _text(node.get("id"), f"software control working_map.nodes[{index}].id")
        if node_id in node_ids:
            raise ManifestError(f"software control working map has duplicate node: {node_id}")
        node_ids.add(node_id)
        for field in ("label", "description", "type", "statement_state", "change_state"):
            _text(node.get(field), f"software control node {node_id}.{field}")
        _validate_workflow_evidence(node, f"software control node {node_id}")
        implementation_group_ids = _text_list(node.get("implementation_group_ids"), f"software control node {node_id}.implementation_group_ids")
        if system_architecture is not None and any(group_id not in available_group_ids for group_id in implementation_group_ids):
            raise ManifestError(f"software control node {node_id} references an unknown implementation group")
        owner_view = _mapping(node.get("owner_view"), f"software control node {node_id}.owner_view")
        for field in OWNER_VIEW_FIELDS:
            _text(owner_view.get(field), f"software control node {node_id}.owner_view.{field}")
        _text_list(owner_view.get("unknowns"), f"software control node {node_id}.owner_view.unknowns")
        _text_list(owner_view.get("owner_checks"), f"software control node {node_id}.owner_view.owner_checks")
        basis = _validate_basis(owner_view.get("basis"), f"software control node {node_id}.owner_view.basis")
        if node.get("change_state") == "changed":
            changed_nodes += 1
            if not basis.get("claim_ids") or not basis.get("evidence_ids"):
                raise ManifestError("a changed software-control node needs direct claim and evidence IDs")
    if not nodes:
        raise ManifestError("software control working_map.nodes must not be empty")
    if changed_nodes > 1:
        raise ManifestError("software control currently supports at most one changed working-map node")

    flows = _sequence(working_map.get("flows"), "software control working_map.flows")
    for index, raw_flow in enumerate(flows):
        flow = _mapping(raw_flow, f"software control working_map.flows[{index}]")
        source_id = _text(flow.get("from"), f"software control flow {index}.from")
        target_id = _text(flow.get("to"), f"software control flow {index}.to")
        _text(flow.get("label"), f"software control flow {index}.label")
        if source_id not in node_ids or target_id not in node_ids:
            raise ManifestError("software control flow references an unknown node")

    overview_map = _mapping(working_map.get("overview_map"), "software control working_map.overview_map")
    _text(overview_map.get("title"), "software control working_map.overview_map.title")
    overview_nodes = _sequence(overview_map.get("nodes"), "software control working_map.overview_map.nodes")
    if len(overview_nodes) != 4:
        raise ManifestError("software control overview map must contain exactly four owner steps")
    overview_ids: set[str] = set()
    covered_detail_ids: list[str] = []
    changed_overview_nodes: list[Mapping[str, Any]] = []
    for index, raw_node in enumerate(overview_nodes):
        node = _mapping(raw_node, f"software control overview node {index}")
        node_id = _text(node.get("id"), f"software control overview node {index}.id")
        if node_id in overview_ids:
            raise ManifestError(f"software control overview map has duplicate node: {node_id}")
        overview_ids.add(node_id)
        for field in ("label", "description", "statement_state", "change_state"):
            _text(node.get(field), f"software control overview node {node_id}.{field}")
        _validate_workflow_evidence(node, f"software control overview node {node_id}")
        detail_ids = _text_list(
            node.get("detail_node_ids"),
            f"software control overview node {node_id}.detail_node_ids",
            allow_empty=False,
        )
        if any(detail_id not in node_ids for detail_id in detail_ids):
            raise ManifestError(f"software control overview node {node_id} references an unknown detail node")
        covered_detail_ids.extend(detail_ids)
        if node.get("change_state") == "changed":
            changed_overview_nodes.append(node)
    if set(covered_detail_ids) != node_ids or len(covered_detail_ids) != len(node_ids):
        raise ManifestError("software control overview map must cover every detail node exactly once")
    if changed_nodes:
        changed_detail_ids = {
            node.get("id") for node in nodes if isinstance(node, Mapping) and node.get("change_state") == "changed"
        }
        if len(changed_overview_nodes) != 1 or not changed_detail_ids.intersection(changed_overview_nodes[0].get("detail_node_ids", [])):
            raise ManifestError("software control changed overview node must contain the changed detail node")

    overview_flows = _sequence(overview_map.get("flows"), "software control working_map.overview_map.flows")
    for index, raw_flow in enumerate(overview_flows):
        flow = _mapping(raw_flow, f"software control overview flow {index}")
        source_id = _text(flow.get("from"), f"software control overview flow {index}.from")
        target_id = _text(flow.get("to"), f"software control overview flow {index}.to")
        _text(flow.get("label"), f"software control overview flow {index}.label")
        if source_id not in overview_ids or target_id not in overview_ids:
            raise ManifestError("software control overview flow references an unknown node")

    identity = _text(document.get("control_identity"), "software control control_identity")
    payload = dict(document)
    payload.pop("control_identity", None)
    if sha256_bytes(canonical_json_bytes(payload)) != identity:
        raise ManifestError("software control canonical identity is invalid")

    source = dict(_mapping(document.get("source_identity"), "software control source_identity"))
    source["_working_map"] = working_map
    _validate_source_binding(
        source,
        brief=brief,
        review=review,
        system_architecture=system_architecture,
    )
    return deepcopy(dict(document))
