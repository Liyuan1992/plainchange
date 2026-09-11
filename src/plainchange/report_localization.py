"""Source-bound translations of presentation text, never evidence or graph fields."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any

from .models import ManifestError

SCHEMA = "plainchange.report-translations.v1"
TEXT_FIELDS = frozenset({
    "purpose", "headline", "internal_concept_label", "text", "state_label",
    "state_explanation", "question", "answer", "audience", "explanation",
    "title", "instructions", "label", "description", "overview", "boundary_label",
    "boundary_note", "order_label", "order_note", "evidence_label", "evidence_note",
    "meaning", "visible_result", "current_change", "affected_people",
})
TEXT_ARRAYS = frozenset({
    "software_steps", "change_points", "before", "after", "unknowns", "owner_checks",
})
SKIP = frozenset({"source_identity", "basis", "validation", "source", "source_refs", "presentation"})

# Technical explanations are presentation too; source quotations and identifiers are not.
REVIEW_FIELDS = TEXT_FIELDS | frozenset({
    "eyebrow", "subtitle", "scope_note", "truth_label", "status_label", "icon",
    "before", "after", "impact", "unknown", "evidence_boundary", "limitation",
    "next_check", "action_label", "action_cost", "role_label", "source_label", "responsibility",
})
REVIEW_ARRAYS = TEXT_ARRAYS | frozenset({"limitations", "responsibilities"})
REVIEW_SKIP = SKIP | frozenset({"original_text", "task_context", "evidence", "patch"})


def review_text_locations(value: Any, path: tuple = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in REVIEW_SKIP:
                continue
            location = (*path, key)
            if key in REVIEW_FIELDS and isinstance(child, str):
                yield location, child
            elif key in REVIEW_ARRAYS and isinstance(child, list):
                for index, text in enumerate(child):
                    if isinstance(text, str):
                        yield (*location, index), text
            elif isinstance(child, (dict, list)):
                yield from review_text_locations(child, location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from review_text_locations(child, (*path, index))


def review_translation_template(model: dict, target: str = "en") -> dict:
    return {
        "review_identity": model["review_identity"],
        "translations": {text: text for _, text in review_text_locations(model)
                         if text.strip() and (target != "en" or re.search(r"[\u3400-\u9fff]", text))},
    }


def validated_review_translations(model: dict, pack: dict) -> dict:
    supplement = pack.get("review_text")
    if supplement is None:
        return {}
    if not isinstance(supplement, dict) or supplement.get("review_identity") != model["review_identity"]:
        raise ManifestError("technical explanation translation belongs to a different review")
    expected = review_translation_template(model, pack["target_language"])["translations"]
    translations = supplement.get("translations")
    if not isinstance(translations, dict) or set(translations) != set(expected):
        raise ManifestError("technical explanation translation must cover all presentation text")
    for target in translations.values():
        if not isinstance(target, str) or not target.strip():
            raise ManifestError("empty technical explanation translation")
        if pack["target_language"] == "en" and re.search(r"[\u3400-\u9fff]", target):
            raise ManifestError("English technical explanation still contains Chinese")
    return {"translations": translations, "fields": sorted(REVIEW_FIELDS),
            "arrays": sorted(REVIEW_ARRAYS), "skip": sorted(REVIEW_SKIP)}


def text_locations(value: Any, path: tuple = ()):
    """Enumerate only schema presentation fields; identity/state arrays are excluded."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key in SKIP:
                continue
            location = (*path, key)
            if key in TEXT_FIELDS and isinstance(child, str):
                yield location, child
            elif key in TEXT_ARRAYS and isinstance(child, list):
                for index, text in enumerate(child):
                    if isinstance(text, str):
                        yield (*location, index), text
            elif isinstance(child, (dict, list)):
                yield from text_locations(child, location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from text_locations(child, (*path, index))


def translation_template(control: dict, target: str = "en") -> dict:
    if target not in {"en", "zh-CN"}:
        raise ManifestError("report translation supports only en and zh-CN")
    return {
        "schema_version": SCHEMA,
        "control_identity": control["control_identity"],
        "target_language": target,
        "translations": dict.fromkeys(sorted({text for _, text in text_locations(control)}), ""),
    }


def localized_control(control: dict | None, pack: Any) -> dict:
    if not isinstance(control, dict) or not isinstance(pack, dict):
        raise ManifestError("report translations require an owner report and a translation object")
    if pack.get("schema_version") != SCHEMA:
        raise ManifestError("unsupported report translation schema")
    if pack.get("control_identity") != control["control_identity"]:
        raise ManifestError("report translation belongs to a different source identity")
    if pack.get("target_language") not in {"en", "zh-CN"}:
        raise ManifestError("report translation supports only en and zh-CN")
    translations = pack.get("translations")
    expected = {text for _, text in text_locations(control)}
    if not isinstance(translations, dict) or set(translations) != expected:
        raise ManifestError("report translation must cover every owner text exactly; missing or unknown text")
    for source, target in translations.items():
        if not isinstance(target, str) or not target.strip():
            raise ManifestError(f"empty report translation: {source[:60]}")
        if pack["target_language"] == "en" and re.search(r"[\u3400-\u9fff]", target):
            raise ManifestError(f"English report translation still contains Chinese: {source[:60]}")
    result = deepcopy(control)
    for path, source in text_locations(control):
        parent = result
        for key in path[:-1]:
            parent = parent[key]
        parent[path[-1]] = translations[source]
    return result


def localize_report(directory: str, *, translations: str | None = None,
                    export: str | None = None, language: str = "en") -> dict:
    from .html_renderer import render_review_html
    from .software_control import validate_software_control

    root = Path(directory).resolve()
    def read(path: Path):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            raise ManifestError(f"cannot read report JSON: {path.name}") from exc
    model = read(root / "beginner-review.json")
    control = validate_software_control(read(root / "software-control.json"), review=model,
                                        system_architecture=model.get("system_architecture"))
    if export:
        destination = Path(export)
        # Exclusive creation avoids overwriting a report or an existing translation.
        with destination.open("x", encoding="utf-8") as stream:
            template = translation_template(control, language)
            template["review_text"] = review_translation_template(model, language)
            json.dump(template, stream, ensure_ascii=False, indent=2)
        return {"translation_template": str(destination)}
    if not translations:
        raise ManifestError("provide --translations or --export")
    pack = read(Path(translations))
    html = render_review_html(model, control, pack)
    (root / "review.html").write_text(html, encoding="utf-8")
    (root / "report-translations.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"review_html": str(root / "review.html"), "language": pack["target_language"]}
