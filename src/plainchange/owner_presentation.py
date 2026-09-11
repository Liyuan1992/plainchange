"""Language-neutral descriptors for PlainChange-owned owner-facing messages.

The canonical software-control document remains a source-bound Chinese projection.
This module records which presentation strings PlainChange owns and renders an
English projection from stable semantic keys. Project declarations and evidence
are deliberately left in their source language unless a reviewed translation
pack overrides them.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping, Sequence

from .models import ManifestError


SCHEMA = "plainchange.owner-presentation.v1"
BLOCKED_PATH_PARTS = frozenset(
    {
        "basis",
        "control_identity",
        "id",
        "source",
        "source_identity",
        "source_refs",
        "statement_state",
        "validation",
        "presentation",
    }
)
ALLOWED_LEAVES = frozenset(
    {
        "answer",
        "affected_people",
        "audience",
        "boundary_label",
        "boundary_note",
        "change_points",
        "current_change",
        "description",
        "evidence_label",
        "evidence_note",
        "explanation",
        "headline",
        "instructions",
        "internal_concept_label",
        "label",
        "meaning",
        "overview",
        "order_label",
        "order_note",
        "owner_checks",
        "purpose",
        "question",
        "software_steps",
        "state_explanation",
        "state_label",
        "text",
        "title",
        "unknowns",
        "visible_result",
    }
)


def _behavior_phrase(kind: str) -> str:
    return {
        "stop_or_failure": "a branch that can stop processing early or return a failure status",
        "exception_stop": "a branch that can raise an error and stop processing early",
        "failure_stop": "a branch that can return a failure status and stop processing early",
        "call_signature": "a code change that may require callers to adjust their input",
    }.get(kind, "a code change whose behavioral effect still needs interpretation")


def _message_change(args: Mapping[str, Any]) -> str:
    behavior = _behavior_phrase(str(args["behavior_kind"]))
    step = str(args.get("step_label") or "")
    mapped = bool(args.get("mapped"))
    stop = bool(args.get("stop"))
    capability = args.get("map_kind") == "capability_map"
    if mapped:
        if stop:
            return (
                f"Fixed code differences show that {behavior} was added near “{step}”. "
                "It triggers only under specific conditions; runtime behavior and user impact "
                "have not been verified."
            )
        return (
            f"Fixed code differences show {behavior} near “{step}”. "
            "Whether existing callers need to change has not been verified."
        )
    target = "a software capability" if capability else "a user-facing workflow step"
    if stop:
        return (
            f"Fixed code differences show that {behavior} was added, but it cannot yet be "
            f"reliably mapped to {target}. Runtime behavior and user impact have not been verified."
        )
    return (
        f"Fixed code differences show {behavior}, but it cannot yet be reliably mapped to "
        f"{target}. Whether existing callers need to change has not been verified."
    )


def _message_location(args: Mapping[str, Any]) -> str:
    step = str(args.get("step_label") or "")
    if step:
        suffix = (
            "Deterministic checks have not yet explained the exact behavior, and the actual "
            "result has not been run or verified."
            if args.get("no_model_semantics")
            else "The software has not been run to verify the actual result."
        )
        return f"Fixed source locations suggest that this change most likely belongs to “{step}”. {suffix}"
    target = "capability structure" if args.get("map_kind") == "capability_map" else "project workflow"
    return f"Code changes were found, but they cannot yet be reliably mapped to an item in the {target}."


def _message_behavior_claim(args: Mapping[str, Any]) -> str:
    kind = str(args["behavior_kind"])
    if kind == "stop_or_failure":
        subject = "branches that can raise an error or return a failure status"
        pronoun = "They trigger"
    elif kind == "exception_stop":
        subject = "a branch that can raise an error and stop processing early"
        pronoun = "It triggers"
    elif kind == "failure_stop":
        subject = "a branch that can return a failure status and stop processing early"
        pronoun = "It triggers"
    else:
        return (
            "Fixed code differences show a change to the accepted input of a callable function; "
            "whether callers need to adjust has not been verified."
        )
    return (
        f"Fixed code differences show that this update added {subject}. {pronoun} only under "
        "specific conditions; runtime behavior and user impact have not been verified."
    )


def _message_risk(args: Mapping[str, Any]) -> str:
    parts = ["The target software has not been run to verify actual behavior."]
    if args.get("no_model_semantics"):
        parts.append("A complete behavioral interpretation has not been performed either.")
    count = int(args.get("unsupported_count") or 0)
    if count:
        example = str(args.get("unsupported_example") or "an additional changed file")
        unsupported_lead = (
            "One additional documentation or configuration change was"
            if count == 1
            else f"Another {count} documentation or configuration changes were"
        )
        parts.append(
            f"{unsupported_lead} collected but could "
            f"not be connected to the structure. One example is {example}; it must be checked "
            "against the code and cannot be treated as a verified fact by itself."
        )
    return " ".join(parts)


def _message_unsupported(args: Mapping[str, Any]) -> str:
    count = int(args["unsupported_count"])
    example = str(args["unsupported_example"])
    unsupported_lead = (
        "One additional documentation or configuration change was"
        if count == 1
        else f"Another {count} documentation or configuration changes were"
    )
    return (
        f"{unsupported_lead} collected but could not "
        f"be connected to the structure. One example is {example}; it must be checked against "
        "the code and cannot be treated as a verified fact by itself."
    )


def _message_unknowns_answer(args: Mapping[str, Any]) -> str:
    text = _message_risk(args)
    map_name = "capability map" if args.get("map_kind") == "capability_map" else "software workflow"
    return f"{text} The automatically generated {map_name} has not been confirmed by the owner."


def _message_owner_action(args: Mapping[str, Any]) -> str:
    if args.get("stop"):
        return "Check the normal case and the newly added stop or failure condition separately."
    if args.get("has_behavior"):
        return "Check the normal case, then confirm that existing callers are still compatible."
    return "First confirm where this change belongs, then run the most important real usage path."


def _message_check_normal(args: Mapping[str, Any]) -> str:
    step = str(args.get("step_label") or "")
    if step:
        return f"Complete one normal operation in “{step}” and confirm that it still produces the expected result"
    return "Complete one normal operation and confirm that it still produces the expected result"


def _message_software_answer(args: Mapping[str, Any]) -> str:
    product = str(args["product_name"])
    if args.get("purpose_is_source"):
        purpose = str(args.get("purpose") or "")
        return f"This is {product}. Project description in its source language: {purpose}"
    return (
        f"This is {product}. The automatic draft can confirm only its static structure; "
        "the project's business purpose still needs owner confirmation."
    )


def _message_working_title(args: Mapping[str, Any]) -> str:
    product = str(args["product_name"])
    return f"Main capabilities in {product}" if args.get("map_kind") == "capability_map" else f"How {product} turns input into results"


def _message_screen_headline(args: Mapping[str, Any]) -> str:
    product = str(args["product_name"])
    return f"See what {product} can do" if args.get("map_kind") == "capability_map" else f"Understand {product} in four stages"


def _message_boundary(args: Mapping[str, Any]) -> str:
    order_note = _message_order_note(args)
    kind = "call graph or runtime trace" if args.get("map_kind") == "capability_map" else "runtime trace"
    return (
        "This map starts from project documentation at the fixed revision and then checks code locations. "
        f"Project order statement in its source language: {order_note} It is not a {kind} and must not be "
        "treated as verified fact before owner confirmation."
    )


RESPONSIBILITIES = {
    "input": ("Receive input and session context", "Accept content from the caller and maintain the session information needed for this interaction."),
    "context": ("Prepare context and existing information", "Assemble the context, prompts, memory, or saved information needed for this work."),
    "decision": ("Decide how to handle the request", "Use rules, permissions and current state to decide which capabilities may be used next."),
    "execution": ("Run the actual processing work", "Invoke the processing capabilities and coordinate tasks, tools or parallel work."),
    "delivery": ("Prepare and deliver the result", "Prepare the result in a form the caller can receive and complete any required handoff."),
    "state": ("Record state and progress", "Record state, events, caches or traceable progress produced during processing."),
}

CATEGORIES = {
    "entry": ("Calls and user entry points", "Receive input supplied by users, programs or external systems."),
    "data": ("Data and state", "Organize data the software reads, stores or passes on."),
    "core": ("Core functions", "Perform the software's main work."),
    "quality": ("Testing and quality", "Check whether the main functions still work as expected."),
    "delivery": ("Documentation and engineering support", "Contain documentation, examples, build support and maintenance tools."),
    "unclassified": ("Unclassified implementation", "The automatic draft cannot yet determine the role of this code."),
}

EVIDENCE = {
    "declared_and_code_supported": (
        "Matching code found",
        "A matching entry or implementation location was found in the fixed source for this project-described item; runtime behavior has not been verified.",
    ),
    "partially_supported": (
        "Some matching code found",
        "Only some project-described items in this stage have matching locations in the fixed source.",
    ),
    "declared_only": (
        "From project documentation only",
        "The project describes this item, but no stable matching location was found in the bounded source scope.",
    ),
    "generated_candidate": (
        "Automatic candidate",
        "This is an automatic candidate and still needs owner confirmation.",
    ),
    "model_interpreted_code_supported": (
        "Model interpretation with matching code",
        "A configured model interpreted this item from project material, and matching locations were found in the fixed source. It is still not runtime proof.",
    ),
    "model_interpreted_only": (
        "Model interpretation; code location not found",
        "A configured model interpreted this item from project material, but the bounded source check did not find a stable matching location.",
    ),
}


def _message_generated_node(args: Mapping[str, Any]) -> str:
    kind = str(args["kind"])
    identifier = str(args["identifier"])
    field = str(args["field"])
    values = RESPONSIBILITIES if kind == "responsibility" else CATEGORIES
    try:
        pair = values[identifier]
    except KeyError as exc:
        raise ManifestError("unknown generated owner-node message") from exc
    return pair[0 if field == "label" else 1]


def _message_evidence(args: Mapping[str, Any]) -> str:
    status = str(args["status"])
    field = str(args["field"])
    if status == "code_discovered" and args.get("internal_responsibility"):
        pair = (
            "Discovered from code structure",
            "Within the code scope explicitly referenced by this capability, fixed-version file and identifier names support this candidate responsibility. It is not a project declaration or runtime verification and still needs owner confirmation.",
        )
    elif status == "code_discovered":
        pair = (
            "Discovered from code structure",
            "This type of implementation exists in the fixed source, but its business meaning still needs project documentation or owner confirmation.",
        )
    else:
        try:
            pair = EVIDENCE[status]
        except KeyError as exc:
            raise ManifestError("unknown owner evidence presentation state") from exc
    return pair[0 if field == "label" else 1]


def _message_order_label(args: Mapping[str, Any]) -> str:
    return {
        "code_supported": "Order supported by code",
        "partially_supported": "Order partially supported",
        "conflicting": "Order conflict",
        "unverified": "Order not verified",
        "not_applicable": "No fixed order",
    }.get(str(args["order_status"]), "Order not verified")


def _message_order_note(args: Mapping[str, Any]) -> str:
    status = str(args["order_status"])
    project_declared = bool(args.get("project_declared"))
    if status == "not_applicable":
        return (
            "Project documentation describes these as parallel capabilities; it does not establish call order or runtime sequence."
            if project_declared
            else "These are parallel implementation areas found in code; current evidence does not support arranging them as a business workflow."
        )
    return {
        "code_supported": "The declared order has matching orchestration evidence in the fixed source, but runtime execution has not been verified.",
        "partially_supported": "Only part of the declared order has matching orchestration evidence in the fixed source.",
        "conflicting": "The project description and fixed-source orchestration do not agree, so documentation order cannot be treated as runtime order.",
        "unverified": "The order of these steps has not been verified against runtime behavior.",
    }.get(status, "The order of these steps has not been verified against runtime behavior.")


STATIC_MESSAGES = {
    "summary.internal_area": "Area containing this change",
    "state.confirmed": "Confirmed",
    "state.code_evidence": "Code evidence from the fixed Git revisions supports this conclusion.",
    "state.unassessed": "Not assessed yet",
    "state.unassessed_explanation": "Behavioral interpretation was not run, so an unassessed impact cannot be labelled as 'not found'.",
    "state.not_found": "Not found so far",
    "state.not_found_explanation": "Not finding an impact is not proof that none exists.",
    "state.possible": "Possibly affected",
    "state.possible_explanation": "This role is a source-bound candidate for attention, not verified evidence of actual user impact.",
    "state.supported": "Evidence-supported assessment",
    "state.supported_explanation": "This impact assessment comes from a bounded explanation and retains its evidence and limitations.",
    "state.not_verified": "Not verified",
    "state.runtime_explanation": "Static code facts cannot replace an actual runtime check.",
    "state.next_action": "Next action",
    "state.next_action_explanation": "This recommendation follows from the current evidence gaps; it does not mean the check has been completed.",
    "question.software": "What is this software?",
    "question.change": "What did AI mainly change?",
    "question.audience": "Who may notice a change?",
    "question.unknowns": "What do we still not know?",
    "question.next": "What should I check next?",
    "question.from_project": "From project documentation",
    "question.auto_candidate": "Automatic candidate",
    "question.located": "Evidence-supported assessment",
    "question.unmapped": "Not mapped yet",
    "question.minimum_checks": "Complete these two minimum checks first:",
    "impact.unassessed": "Only code and structure were checked; whether ordinary users may notice a change has not been assessed.",
    "impact.not_found": "There is not enough evidence to confirm that ordinary users have directly noticed a change.",
    "audience.users": "Ordinary users of the analyzed software",
    "audience.systems": "Other systems that depend on this software",
    "audience.integration_stop": "Integration behavior has not been run or verified; the code signal only shows a newly added stop or failure branch.",
    "audience.integration_callers": "Existing callers have not been verified for compatibility with the changed calling convention.",
    "audience.integration_unknown": "Integration behavior has not been run or verified.",
    "unknown.runtime": "Whether actual runtime behavior changed",
    "unknown.semantic": "A complete behavioral interpretation has not yet been performed",
    "unknown.capability_map": "Whether the automatic capability map matches the project's real business behavior",
    "unknown.workflow": "Whether the automatic software workflow matches the project's real business behavior",
    "check.stop": "Try a case likely to trigger the new stop or failure branch, and confirm that its message and exit behavior are appropriate",
    "check.callers": "Check the information supplied by existing callers and confirm that the changed calling convention remains compatible",
    "check.location": "Confirm that the highlighted capability is where this change belongs",
    "check.runtime": "Run the most important real usage path",
    "action.normal.title": "Check the normal case",
    "action.stop.title": "Check the stop condition",
    "action.callers.title": "Check existing callers",
    "action.map.capability.title": "Confirm the software capability map",
    "action.map.workflow.title": "Confirm the software workflow",
    "action.map.capability.instructions": "Have someone who knows the project review the capability structure and correct omissions or mismatches. Do not add an order that lacks evidence.",
    "action.map.workflow.instructions": "Have someone who knows the project review the four-stage workflow and correct anything that does not match the real software.",
    "action.runtime.title": "Verify actual behavior",
    "action.runtime.instructions": "Run one user path or interface most relevant to this change and record the actual result.",
    "node.capability.result": "This capability provides a result to its users or other functions; the current evidence does not declare a fixed next step.",
    "node.workflow.result": "The result of this stage is passed to the next stage.",
    "node.unchanged": "There is no current evidence that this change modified this step.",
    "node.audience_unknown": "The available material is insufficient to identify who may be directly affected.",
    "node.runtime_boundary": "Neither project documentation nor a code location can replace runtime verification.",
    "node.check_project": "Check whether the project documentation still matches the software's current purpose",
    "node.check_capability_use": "Check which entry points or other functions normally use this capability",
    "node.check_workflow_order": "Run or inspect the real orchestration path when step order matters",
    "map.capability.description": "Start with the project's main capabilities, then expand their documentation and code locations. These capabilities have no fixed order.",
    "map.workflow.description": "Start with four stages, then expand the detailed project-declared steps and their evidence status.",
    "map.capability.overview": "This capability structure is derived from fixed project documentation and code locations. Different entry points may combine these capabilities; their placement does not imply runtime order.",
    "map.workflow.overview": "The workflow comes from project documentation at a fixed revision. Step order and runtime behavior remain separate evidence questions.",
    "map.capability.boundary_label": "Capability description checked against code",
    "map.workflow.boundary_label": "Project description checked against code",
    "map.capability.overview_title": "Main capabilities (no fixed order)",
    "map.workflow.overview_title": "Understand this software in four stages",
    "layer.control.label": "Software control layer",
    "layer.control.purpose": "Answer how the software works, what changed, and what to check next.",
    "layer.explanation.label": "Explanation layer",
    "layer.explanation.purpose": "Separate confirmed, not found so far, and not verified.",
    "layer.technical.label": "Technical evidence layer",
    "layer.technical.purpose": "Expand fixed revisions, files, and static relationships on demand.",
}

DYNAMIC_MESSAGES: dict[str, Callable[[Mapping[str, Any]], str]] = {
    "change.behavior": _message_change,
    "change.location": _message_location,
    "claim.behavior": _message_behavior_claim,
    "claim.changed_files": lambda args: f"Fixed code differences show changes in {int(args['count'])} files.",
    "risk.runtime": _message_risk,
    "risk.unsupported": _message_unsupported,
    "risk.unknowns_answer": _message_unknowns_answer,
    "action.summary": _message_owner_action,
    "check.normal": _message_check_normal,
    "question.software_answer": _message_software_answer,
    "product.purpose_unknown": lambda args: f"The business purpose of {args['product_name']} still needs owner confirmation.",
    "map.title": _message_working_title,
    "map.headline": _message_screen_headline,
    "map.boundary": _message_boundary,
    "node.generated": _message_generated_node,
    "evidence.presentation": _message_evidence,
    "order.label": _message_order_label,
    "order.note": _message_order_note,
}


def message(path: Sequence[str | int], key: str, **args: Any) -> dict[str, Any]:
    return {"path": list(path), "key": key, "args": args}


def _resolve(value: Any, path: Sequence[str | int]) -> Any:
    current = value
    for part in path:
        if isinstance(part, int):
            if not isinstance(current, list) or part < 0 or part >= len(current):
                raise ManifestError("owner presentation path references a missing array item")
            current = current[part]
        else:
            if not isinstance(current, Mapping) or part not in current:
                raise ManifestError("owner presentation path references a missing field")
            current = current[part]
    return current


def _set(value: Any, path: Sequence[str | int], replacement: str) -> None:
    parent = _resolve(value, path[:-1])
    final = path[-1]
    if isinstance(final, int):
        parent[final] = replacement
    else:
        parent[final] = replacement


def _render(key: str, args: Mapping[str, Any]) -> str:
    if key in STATIC_MESSAGES:
        if args:
            raise ManifestError(f"owner presentation static message does not accept arguments: {key}")
        return STATIC_MESSAGES[key]
    renderer = DYNAMIC_MESSAGES.get(key)
    if renderer is None:
        raise ManifestError(f"unsupported owner presentation message: {key}")
    try:
        result = renderer(args)
    except (KeyError, TypeError, ValueError) as exc:
        raise ManifestError(f"invalid owner presentation arguments: {key}") from exc
    if not isinstance(result, str) or not result.strip():
        raise ManifestError(f"empty owner presentation result: {key}")
    return result


def validate_owner_presentation(control: Mapping[str, Any]) -> dict[str, Any] | None:
    raw = control.get("presentation")
    if raw is None:
        return None
    if not isinstance(raw, Mapping) or raw.get("schema_version") != SCHEMA:
        raise ManifestError("software control owner presentation schema is invalid")
    if raw.get("source_language") != "zh-CN":
        raise ManifestError("software control owner presentation source language is unsupported")
    messages = raw.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ManifestError("software control owner presentation messages must not be empty")
    seen: set[tuple[str | int, ...]] = set()
    for descriptor in messages:
        if not isinstance(descriptor, Mapping):
            raise ManifestError("owner presentation message must be an object")
        path = descriptor.get("path")
        key = descriptor.get("key")
        args = descriptor.get("args")
        if (
            not isinstance(path, list)
            or not path
            or any(not isinstance(part, (str, int)) or isinstance(part, bool) for part in path)
            or not isinstance(key, str)
            or not isinstance(args, Mapping)
        ):
            raise ManifestError("owner presentation message descriptor is invalid")
        if any(isinstance(part, str) and part in BLOCKED_PATH_PARTS for part in path):
            raise ManifestError("owner presentation cannot target evidence, identity, state or topology")
        final = path[-1]
        leaf = path[-2] if isinstance(final, int) and len(path) > 1 else final
        if not isinstance(leaf, str) or leaf not in ALLOWED_LEAVES:
            raise ManifestError(f"owner presentation path is not an approved text field: {path}")
        path_key = tuple(path)
        if path_key in seen:
            raise ManifestError("owner presentation cannot target one field twice")
        seen.add(path_key)
        source = _resolve(control, path)
        if not isinstance(source, str) or not source.strip():
            raise ManifestError("owner presentation target must be existing non-empty text")
        _render(key, args)
    source_paths = raw.get("source_language_paths", [])
    if not isinstance(source_paths, list):
        raise ManifestError("owner presentation source-language paths must be an array")
    for path in source_paths:
        if not isinstance(path, list) or not path or not isinstance(_resolve(control, path), str):
            raise ManifestError("owner presentation source-language path is invalid")
    return deepcopy(dict(raw))


def localized_owner_control(control: Mapping[str, Any], language: str = "en") -> dict[str, Any] | None:
    """Return a derived projection, or ``None`` for legacy/non-automatic reports."""
    if language != "en":
        raise ManifestError("automatic owner presentation currently supports English only")
    spec = validate_owner_presentation(control)
    if spec is None:
        return None
    result = deepcopy(dict(control))
    for descriptor in spec["messages"]:
        _set(result, descriptor["path"], _render(descriptor["key"], descriptor["args"]))
    return result
