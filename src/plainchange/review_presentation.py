"""Language-neutral projection for PlainChange-owned architecture wording.

The review model and lazy architecture snapshot remain canonical source data.
This module emits small, identity-bound path patches for text that PlainChange
can reproduce from stable semantic fields. Project declarations and technical
evidence are deliberately not translated here.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .models import ManifestError
from .owner_presentation import CATEGORIES, RESPONSIBILITIES


SCHEMA = "plainchange.generated-review-presentation.v1"
_ALLOWED_LEAVES = frozenset(
    {
        "action_cost",
        "action_label",
        "after",
        "before",
        "boundary_note",
        "description",
        "evidence_boundary",
        "impact",
        "label",
        "limitation",
        "next_check",
        "question",
        "relation_label",
        "responsibility",
        "role_label",
        "source_label",
        "state_label",
        "status_label",
        "summary",
        "text",
        "title",
        "truth_label",
        "unknown",
        "warning",
    }
)
_BLOCKED_PARTS = frozenset(
    {
        "basis",
        "change",
        "change_identity",
        "control_identity",
        "evidence_refs",
        "group_source",
        "id",
        "node_ids",
        "profile_sha256",
        "review_identity",
        "source_refs",
        "snapshot_identity",
        "statement_state",
        "validation",
    }
)


def _resolve(value: Any, path: Sequence[str | int]) -> Any:
    current = value
    for part in path:
        if isinstance(part, int):
            if not isinstance(current, list) or part < 0 or part >= len(current):
                raise ManifestError("generated review presentation references a missing array item")
            current = current[part]
        else:
            if not isinstance(current, Mapping) or part not in current:
                raise ManifestError("generated review presentation references a missing field")
            current = current[part]
    return current


def _render(key: str, args: Mapping[str, Any]) -> str:
    if key == "summary.question":
        return {
            "summary.what": "What happened",
            "summary.why": "Why this change was made",
            "summary.impact": "Who may be affected",
            "summary.attention": "What needs attention",
        }[str(args["id"])]
    if key == "truth.label":
        return {
            "verified": "Verified",
            "inference": "Evidence-supported inference",
            "context": "Task context available",
            "unknown": "Unknown",
        }.get(str(args["state"]), "Unknown")
    if key == "summary.what":
        return f"AI changed {int(args['changed_files'])} files in the fixed comparison."
    if key == "summary.why":
        roles = set(args.get("roles", []))
        if roles == {"user", "assistant"}:
            return (
                "User task context and an AI response are available. Keep the user's request "
                "separate from the AI's interpretation when checking the reason for this change."
            )
        if "user" in roles:
            return "User task context is available; review it to see whether it explains the reason for this change."
        if "assistant" in roles:
            return "An AI response is available, but it describes the AI's interpretation rather than the user's intent."
        return "No task conversation was provided, so the reason for this change cannot yet be explained."
    if key == "summary.impact":
        count = int(args["count"])
        if count:
            return (
                f"Static code analysis found {count} directly related locations. "
                "This does not prove that these user-facing functions changed at runtime."
            )
        return "The available static evidence does not establish a directly related scope."
    if key == "summary.attention":
        return "A person still needs to review the evidence gaps; no further verifiable conclusion is available yet."
    if key == "summary.next-check":
        return {
            "impact": "To confirm real impact, inspect the runtime path and an independent test receipt.",
            "attention": "Verify the user path or key behavior associated with this change first.",
        }[str(args["kind"])]
    if key == "task-context.state":
        return {
            "unavailable": "Task conversation unavailable",
            "available": "Task context available",
            "ready": "Reason supported by evidence",
        }.get(str(args["state"]), "Task context available")
    if key == "task-context.action":
        return "View available task context"
    if key == "task-context.cost":
        return "No model call or extra tokens"
    if key == "task-context.role":
        return "User quotation" if args["role"] == "user" else "AI response"
    if key == "task-context.source":
        return (
            "What the user actually said"
            if args["role"] == "user"
            else "The AI's interpretation or completion statement"
        )
    if key == "task-context.warning":
        return "An AI explanation may help interpretation, but it cannot replace user confirmation."
    if key == "node.unknown-label":
        return "Responsibility not yet clear"
    if key == "node.status":
        return {
            "added": "Added",
            "removed": "Removed",
            "modified": "Changed",
            "impacted": "Related",
            "unchanged_context": "Unchanged context",
        }.get(str(args["status"]), "Unknown")
    if key == "node.before":
        return {
            "missing": "This responsibility did not exist before the change.",
            "unknown": "The available evidence does not reliably explain its previous business responsibility.",
        }[str(args["state"])]
    if key == "node.after":
        return {
            "missing": "This responsibility no longer exists after the change.",
            "unknown": "The available evidence does not reliably explain its current business responsibility.",
        }[str(args["state"])]
    if key == "node.impact":
        count = int(args["count"])
        if args["status"] == "impacted":
            return (
                f"The code has a direct relationship with {count} changed responsibilit"
                f"{'y' if count == 1 else 'ies'}; static evidence does not prove runtime impact."
            )
        if count:
            return (
                f"Static code analysis found {count} one-hop direct relationship"
                f"{'s' if count != 1 else ''}; runtime impact still needs separate verification."
            )
        return "This item provides context; the available evidence does not establish direct runtime impact."
    if key == "node.evidence-boundary":
        return "The code location and static structural relationship are confirmed; see the technical evidence for exact references."
    if key == "node.unknown":
        return "Dynamic calls, configuration injection and runtime behavior remain outside this static evidence boundary."
    if key == "relation.label":
        return "Direct code relationship"
    if key == "branch.label":
        return "Direct code relationship" if args["id"] == "omitted.impacted" else "Unchanged context"
    if key == "branch.limitation":
        return (
            "This proves only a static code relationship, not runtime impact."
            if args["id"] == "omitted.impacted"
            else "These locations provide dependency context and are not marked as changed in this update."
        )
    if key == "claim.auto":
        claim_id = str(args["id"])
        if claim_id == "function.auto-change":
            return f"AI changed {int(args['changed_files'])} files in the fixed comparison."
        if claim_id == "attention.runtime-unknown":
            return "A person still needs to review the evidence gaps; no further verifiable conclusion is available yet."
        if claim_id == "history.auto-unknown":
            return "There is not enough evidence to relate this change to an approved historical decision."
        if claim_id == "architecture.auto-location":
            labels = [CATEGORIES[item][0] for item in args.get("categories", []) if item in CATEGORIES]
            if labels:
                return f"Static structure places this change mainly in {', '.join(labels)}."
            return "Static structure identifies changed code, but its owner-facing capability location remains unclear."
        raise ManifestError("unknown automatic claim presentation")
    if key == "concept.source":
        return "Product/workflow architecture declared by target configuration"
    if key == "concept.title":
        product = str(args["product_name"])
        if args["map_kind"] == "capability_map":
            return f"Capabilities described in {product}'s project documentation"
        return f"How {product} works according to its project documentation"
    if key == "concept.boundary":
        if args["map_kind"] == "capability_map":
            return (
                "This map derives parallel capabilities from project documentation at the fixed "
                "revision and then checks code locations. It does not show call order or runtime execution."
            )
        return (
            "This map starts from project documentation at the fixed revision and checks its code "
            "locations separately. It is not a runtime trace."
        )
    if key == "concept.purpose_unknown":
        return (
            f"The automatic draft can confirm only the static structure of {args['product_name']}; "
            "its business purpose still needs owner confirmation."
        )
    if key == "architecture.status":
        status = str(args["status"])
        return {
            "candidate_static_snapshot": "Candidate static snapshot; not approved as a long-term baseline",
        }.get(status, "Architecture status not translated")
    if key == "category":
        category = str(args["category"])
        field = str(args["field"])
        if category not in CATEGORIES or field not in {"label", "description"}:
            raise ManifestError("unknown generated architecture category")
        return CATEGORIES[category][0 if field == "label" else 1]
    if key == "responsibility":
        responsibility = str(args["responsibility"])
        field = str(args["field"])
        if responsibility not in RESPONSIBILITIES or field not in {"label", "description"}:
            raise ManifestError("unknown generated architecture responsibility")
        return RESPONSIBILITIES[responsibility][0 if field == "label" else 1]
    if key == "node-rule":
        return {
            "api": "External API entry point",
            "test_": "Behavior check",
            "config": "Runtime configuration",
        }.get(str(args["pattern"]), "Automatically classified code")
    raise ManifestError(f"unsupported generated review presentation message: {key}")


def automatic_review_presentation(model: Mapping[str, Any]) -> dict[str, Any] | None:
    """Create bounded English patches for reproducible PlainChange-owned text."""
    review_identity = model.get("review_identity")
    if not isinstance(review_identity, str) or not review_identity:
        return None
    system = model.get("system_architecture")
    conceptual = model.get("conceptual_architecture")
    if not isinstance(system, Mapping) and not isinstance(conceptual, Mapping):
        return None

    target_profile = system.get("target_profile") if isinstance(system, Mapping) else None
    if not isinstance(target_profile, Mapping):
        target_profile = {}
    profile_id = str(target_profile.get("profile_id") or "")
    automatic_profile = profile_id.startswith("auto-")
    target_concept = target_profile.get("conceptual_architecture")
    if not isinstance(target_concept, Mapping):
        target_concept = {}
    map_kind = str(target_concept.get("architecture_kind") or "workflow")
    product_name = str(
        model.get("header", {}).get("brand", {}).get("name")
        if isinstance(model.get("header"), Mapping)
        else "the software"
    )
    purpose_is_source = target_concept.get("purpose_statement_state") == "project_declared"
    messages: list[dict[str, Any]] = []
    seen: set[tuple[str, tuple[str | int, ...]]] = set()

    roots = {"review": model, "architecture": system}

    def add(root: str, path: list[str | int], key: str, **args: Any) -> None:
        if root not in roots or not isinstance(roots[root], Mapping):
            return
        if any(isinstance(part, str) and part in _BLOCKED_PARTS for part in path):
            raise ManifestError("generated review presentation cannot target evidence or identity")
        leaf = path[-1] if path else None
        if not isinstance(leaf, str) or leaf not in _ALLOWED_LEAVES:
            raise ManifestError("generated review presentation target is not approved text")
        source = _resolve(roots[root], path)
        if not isinstance(source, str) or not source.strip():
            raise ManifestError("generated review presentation target must be non-empty text")
        path_key = (root, tuple(path))
        if path_key in seen:
            return
        seen.add(path_key)
        messages.append(
            {"root": root, "path": path, "key": key, "args": args, "text": _render(key, args)}
        )

    if isinstance(conceptual, Mapping):
        add("review", ["conceptual_architecture", "source", "label"], "concept.source")
        if automatic_profile:
            add(
                "review",
                ["conceptual_architecture", "title"],
                "concept.title",
                product_name=product_name,
                map_kind=map_kind,
            )
            add(
                "review",
                ["conceptual_architecture", "boundary_note"],
                "concept.boundary",
                map_kind=map_kind,
            )
            if not purpose_is_source:
                add(
                    "review",
                    ["conceptual_architecture", "description"],
                    "concept.purpose_unknown",
                    product_name=product_name,
                )
            for component_index, component in enumerate(conceptual.get("components", [])):
                if not isinstance(component, Mapping):
                    continue
                component_id = str(component.get("id") or "")
                if component_id.startswith("code-capability-"):
                    category = component_id.removeprefix("code-capability-")
                    if category in CATEGORIES:
                        add(
                            "review",
                            ["conceptual_architecture", "components", component_index, "label"],
                            "category",
                            category=category,
                            field="label",
                        )
                        add(
                            "review",
                            ["conceptual_architecture", "components", component_index, "description"],
                            "category",
                            category=category,
                            field="description",
                        )
                for group_index, group in enumerate(component.get("implementation_groups", [])):
                    if isinstance(group, Mapping) and str(group.get("id")) in CATEGORIES:
                        add(
                            "review",
                            [
                                "conceptual_architecture",
                                "components",
                                component_index,
                                "implementation_groups",
                                group_index,
                                "label",
                            ],
                            "category",
                            category=str(group["id"]),
                            field="label",
                        )

    summary_items = model.get("summary", [])
    if isinstance(summary_items, list):
        for summary_index, summary in enumerate(summary_items):
            if not isinstance(summary, Mapping):
                continue
            summary_id = str(summary.get("id") or "")
            if summary_id not in {"summary.what", "summary.why", "summary.impact", "summary.attention"}:
                continue
            base_path: list[str | int] = ["summary", summary_index]
            add("review", [*base_path, "question"], "summary.question", id=summary_id)
            add(
                "review",
                [*base_path, "truth_label"],
                "truth.label",
                state=str(summary.get("truth_state") or "unknown"),
            )
            claim_ids = {str(item) for item in summary.get("claim_ids", [])}
            if summary_id == "summary.what" and claim_ids and all(item.startswith("function.auto-") for item in claim_ids):
                message_key = "summary.what"
                message_args = {"changed_files": int(model.get("change", {}).get("changed_files", 0))}
            elif summary_id == "summary.why" and not claim_ids:
                context = summary.get("task_context") if isinstance(summary.get("task_context"), Mapping) else {}
                entries = context.get("entries", []) if isinstance(context.get("entries"), list) else []
                message_key = "summary.why"
                message_args = {"roles": sorted({str(item.get("role")) for item in entries if isinstance(item, Mapping)})}
            elif summary_id == "summary.impact":
                overlay = system.get("change_overlay", {}) if isinstance(system, Mapping) else {}
                impacted = overlay.get("impacted", []) if isinstance(overlay, Mapping) else []
                message_key = "summary.impact"
                message_args = {"count": len(impacted) if isinstance(impacted, list) else 0}
            elif summary_id == "summary.attention" and claim_ids <= {"attention.runtime-unknown"}:
                message_key = "summary.attention"
                message_args = {}
            else:
                message_key = ""
                message_args = {}
            if message_key:
                add("review", [*base_path, "text"], message_key, **message_args)
                for item_index, item in enumerate(summary.get("items", [])):
                    if isinstance(item, Mapping):
                        add("review", [*base_path, "items", item_index, "text"], message_key, **message_args)
                        add(
                            "review",
                            [*base_path, "items", item_index, "truth_label"],
                            "truth.label",
                            state=str(item.get("truth_state") or "unknown"),
                        )
            if summary_id in {"summary.impact", "summary.attention"} and summary.get("next_check"):
                add(
                    "review",
                    [*base_path, "next_check"],
                    "summary.next-check",
                    kind="impact" if summary_id == "summary.impact" else "attention",
                )
            context = summary.get("task_context")
            if isinstance(context, Mapping):
                context_path = [*base_path, "task_context"]
                add(
                    "review",
                    [*context_path, "state_label"],
                    "task-context.state",
                    state=str(context.get("state") or "available"),
                )
                add(
                    "review",
                    [*context_path, "summary"],
                    "summary.why",
                    roles=sorted({str(item.get("role")) for item in context.get("entries", []) if isinstance(item, Mapping)}),
                )
                if context.get("action_label"):
                    add("review", [*context_path, "action_label"], "task-context.action")
                if context.get("action_cost"):
                    add("review", [*context_path, "action_cost"], "task-context.cost")
                for entry_index, entry in enumerate(context.get("entries", [])):
                    if not isinstance(entry, Mapping):
                        continue
                    entry_path = [*context_path, "entries", entry_index]
                    add("review", [*entry_path, "role_label"], "task-context.role", role=str(entry.get("role")))
                    add("review", [*entry_path, "source_label"], "task-context.source", role=str(entry.get("role")))
                    if entry.get("warning"):
                        add("review", [*entry_path, "warning"], "task-context.warning")

    auto_rules = target_profile.get("node_label_rules", []) if automatic_profile else []
    node_paths: dict[str, int] = {}
    for view_name, view in (model.get("views", {}) or {}).items():
        if not isinstance(view, Mapping) or not isinstance(view.get("nodes"), list):
            continue
        for node_index, node in enumerate(view["nodes"]):
            if not isinstance(node, Mapping):
                continue
            node_id = str(node.get("node_id") or "")
            technical = str(node.get("technical_label") or "")
            label_source = str(node.get("label_source") or "")
            node_paths[node_id] = node_paths.get(node_id, 0) + 1
            label_path = ["views", str(view_name), "nodes", node_index, "label"]
            if label_source == "unknown":
                add("review", label_path, "node.unknown-label")
            elif label_source == "target_profile" and automatic_profile:
                for rule in auto_rules:
                    if isinstance(rule, Mapping) and str(rule.get("pattern") or "") in technical:
                        add("review", label_path, "node-rule", pattern=str(rule.get("pattern") or ""))
                        break
            add(
                "review",
                ["views", str(view_name), "nodes", node_index, "status_label"],
                "node.status",
                status=str(node.get("status") or ""),
            )
        for path_index, relation in enumerate(view.get("paths", [])):
            if isinstance(relation, Mapping):
                add(
                    "review",
                    ["views", str(view_name), "paths", path_index, "relation_label"],
                    "relation.label",
                )

    details = model.get("node_details", {})
    after_paths = model.get("views", {}).get("after", {}).get("paths", []) if isinstance(model.get("views"), Mapping) else []
    if isinstance(details, Mapping):
        for node_id, detail in details.items():
            if not isinstance(detail, Mapping):
                continue
            detail_path = ["node_details", str(node_id)]
            technical = str(detail.get("technical_label") or "")
            label_source = str(detail.get("label_source") or "")
            if label_source == "unknown":
                add("review", [*detail_path, "label"], "node.unknown-label")
            elif label_source == "target_profile" and automatic_profile:
                for rule in auto_rules:
                    if isinstance(rule, Mapping) and str(rule.get("pattern") or "") in technical:
                        add("review", [*detail_path, "label"], "node-rule", pattern=str(rule.get("pattern") or ""))
                        break
            status = str(detail.get("status") or "")
            before_state = str(detail.get("before_state") or ("absent" if status == "added" else ""))
            after_state = str(detail.get("after_state") or ("absent" if status == "removed" else ""))
            if before_state == "absent":
                add("review", [*detail_path, "before"], "node.before", state="missing")
            elif before_state == "present_without_responsibility":
                add("review", [*detail_path, "before"], "node.before", state="unknown")
            if after_state == "absent":
                add("review", [*detail_path, "after"], "node.after", state="missing")
            elif after_state == "present_without_responsibility":
                add("review", [*detail_path, "after"], "node.after", state="unknown")
            related_count = sum(
                1
                for item in after_paths
                if isinstance(item, Mapping)
                and str(node_id) in {str(item.get("changed_node_id")), str(item.get("impacted_node_id"))}
            )
            add("review", [*detail_path, "status_label"], "node.status", status=status)
            add("review", [*detail_path, "impact"], "node.impact", status=status, count=related_count)
            add("review", [*detail_path, "evidence_boundary"], "node.evidence-boundary")
            add("review", [*detail_path, "unknown"], "node.unknown")

    for branch_index, branch in enumerate(model.get("branch_groups", [])):
        if not isinstance(branch, Mapping) or str(branch.get("id")) not in {"omitted.impacted", "omitted.context"}:
            continue
        branch_id = str(branch["id"])
        add("review", ["branch_groups", branch_index, "label"], "branch.label", id=branch_id)
        add("review", ["branch_groups", branch_index, "limitation"], "branch.limitation", id=branch_id)

    changed_categories: list[str] = []
    if isinstance(system, Mapping):
        overlay = system.get("change_overlay", {})
        changed_ids = set()
        if isinstance(overlay, Mapping):
            for status in ("added", "modified", "removed"):
                values = overlay.get(status, [])
                if isinstance(values, list):
                    changed_ids.update(str(value) for value in values)
        for group in system.get("groups", []):
            if isinstance(group, Mapping) and str(group.get("group_id")) in CATEGORIES:
                if changed_ids.intersection(str(value) for value in group.get("node_ids", [])):
                    changed_categories.append(str(group["group_id"]))
    for claim_index, claim in enumerate(model.get("claims", [])):
        if not isinstance(claim, Mapping):
            continue
        claim_id = str(claim.get("id") or "")
        if claim_id not in {"function.auto-change", "attention.runtime-unknown", "history.auto-unknown", "architecture.auto-location"}:
            continue
        add(
            "review",
            ["claims", claim_index, "text"],
            "claim.auto",
            id=claim_id,
            changed_files=int(model.get("change", {}).get("changed_files", 0)),
            categories=changed_categories,
        )
    if isinstance(system, Mapping):
        add(
            "architecture",
            ["status_label"],
            "architecture.status",
            status=str(system.get("status") or ""),
        )
        if automatic_profile:
            for group_index, group in enumerate(system.get("groups", [])):
                if not isinstance(group, Mapping) or str(group.get("group_id")) not in CATEGORIES:
                    continue
                category = str(group["group_id"])
                add(
                    "architecture",
                    ["groups", group_index, "label"],
                    "category",
                    category=category,
                    field="label",
                )
                add(
                    "architecture",
                    ["groups", group_index, "responsibility"],
                    "category",
                    category=category,
                    field="description",
                )
            for area_index, area in enumerate(target_profile.get("module_areas", [])):
                if not isinstance(area, Mapping) or str(area.get("id")) not in CATEGORIES:
                    continue
                category = str(area["id"])
                add(
                    "architecture",
                    ["target_profile", "module_areas", area_index, "label"],
                    "category",
                    category=category,
                    field="label",
                )
                add(
                    "architecture",
                    ["target_profile", "module_areas", area_index, "description"],
                    "category",
                    category=category,
                    field="description",
                )
            for rule_index, rule in enumerate(target_profile.get("node_label_rules", [])):
                if isinstance(rule, Mapping):
                    add(
                        "architecture",
                        ["target_profile", "node_label_rules", rule_index, "label"],
                        "node-rule",
                        pattern=str(rule.get("pattern") or ""),
                    )
            if target_concept:
                add(
                    "architecture",
                    ["target_profile", "conceptual_architecture", "title"],
                    "concept.title",
                    product_name=product_name,
                    map_kind=map_kind,
                )
                add(
                    "architecture",
                    ["target_profile", "conceptual_architecture", "boundary_note"],
                    "concept.boundary",
                    map_kind=map_kind,
                )
                if not purpose_is_source:
                    add(
                        "architecture",
                        ["target_profile", "conceptual_architecture", "description"],
                        "concept.purpose_unknown",
                        product_name=product_name,
                    )
                for component_index, component in enumerate(target_concept.get("components", [])):
                    if not isinstance(component, Mapping):
                        continue
                    component_id = str(component.get("id") or "")
                    if component_id.startswith("code-capability-"):
                        category = component_id.removeprefix("code-capability-")
                        if category in CATEGORIES:
                            add(
                                "architecture",
                                [
                                    "target_profile",
                                    "conceptual_architecture",
                                    "components",
                                    component_index,
                                    "label",
                                ],
                                "category",
                                category=category,
                                field="label",
                            )
                            add(
                                "architecture",
                                [
                                    "target_profile",
                                    "conceptual_architecture",
                                    "components",
                                    component_index,
                                    "description",
                                ],
                                "category",
                                category=category,
                                field="description",
                            )
                    for detail_index, detail in enumerate(component.get("details", [])):
                        if not isinstance(detail, Mapping):
                            continue
                        suffix = str(detail.get("id") or "").rsplit(".", 1)[-1]
                        if suffix not in RESPONSIBILITIES:
                            continue
                        add(
                            "architecture",
                            [
                                "target_profile",
                                "conceptual_architecture",
                                "components",
                                component_index,
                                "details",
                                detail_index,
                                "label",
                            ],
                            "responsibility",
                            responsibility=suffix,
                            field="label",
                        )
                        add(
                            "architecture",
                            [
                                "target_profile",
                                "conceptual_architecture",
                                "components",
                                component_index,
                                "details",
                                detail_index,
                                "description",
                            ],
                            "responsibility",
                            responsibility=suffix,
                            field="description",
                        )

    return {
        "schema_version": SCHEMA,
        "review_identity": review_identity,
        "source_language": "zh-CN",
        "target_language": "en",
        "messages": messages,
    }
