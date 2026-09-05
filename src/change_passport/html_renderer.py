from __future__ import annotations

import json
from importlib import resources
from typing import Any, Mapping

from .models import ManifestError
from .review_model import validate_beginner_review_model

THEME_SCHEMA = "change-passport.review-theme.v1"
SOURCE_DESIGN_TOKENS_SHA256 = (
    "3C14725FC63A06CD32820F9B734E570B02075E72D60D8FEB96581BC3AC869D40"
)
EXPECTED_THEME_PROPERTIES = {
    "--amber",
    "--amber-line",
    "--amber-soft",
    "--blue",
    "--blue-line",
    "--blue-soft",
    "--danger",
    "--focus",
    "--green",
    "--green-line",
    "--green-soft",
    "--grey-soft",
    "--ink",
    "--line",
    "--line-strong",
    "--muted",
    "--page",
    "--panel",
    "--panel-soft",
    "--radius-lg",
    "--radius-md",
    "--shadow",
}


def _resource_text(relative_path: str) -> str:
    try:
        return (
            resources.files("change_passport")
            .joinpath(relative_path)
            .read_text(encoding="utf-8")
        )
    except (FileNotFoundError, OSError) as exc:
        raise ManifestError(f"review renderer resource is missing: {relative_path}") from exc


def _load_theme() -> dict[str, str]:
    try:
        value = json.loads(_resource_text("assets/review-theme.json"))
    except json.JSONDecodeError as exc:
        raise ManifestError("review theme is not valid JSON") from exc
    if not isinstance(value, Mapping) or value.get("schema_version") != THEME_SCHEMA:
        raise ManifestError("review theme schema is invalid")
    if value.get("source_design_tokens_sha256") != SOURCE_DESIGN_TOKENS_SHA256:
        raise ManifestError("review theme is not bound to the confirmed design tokens")
    properties = value.get("custom_properties")
    if not isinstance(properties, Mapping):
        raise ManifestError("review theme custom_properties must be an object")
    if set(properties) != EXPECTED_THEME_PROPERTIES:
        missing = sorted(EXPECTED_THEME_PROPERTIES - set(properties))
        extra = sorted(set(properties) - EXPECTED_THEME_PROPERTIES)
        raise ManifestError(
            f"review theme property mismatch; missing={missing}, extra={extra}"
        )
    result: dict[str, str] = {}
    for key, raw_value in properties.items():
        if not isinstance(raw_value, str) or not raw_value.strip():
            raise ManifestError(f"review theme value is invalid: {key}")
        if any(character in raw_value for character in "{};\r\n"):
            raise ManifestError(f"review theme value contains unsafe CSS syntax: {key}")
        result[str(key)] = raw_value.strip()
    return result


def _theme_css(properties: Mapping[str, str]) -> str:
    rows = [":root {"]
    rows.extend(f"  {key}: {properties[key]};" for key in sorted(properties))
    rows.append("}")
    return "\n".join(rows)


def _json_for_script(value: Any) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (
        serialized.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render_review_html(model_value: Any) -> str:
    model = validate_beginner_review_model(model_value)
    template = _resource_text("templates/review.html")
    css = _resource_text("templates/review.css")
    javascript = _resource_text("templates/review.js")
    replacements = {
        "{{THEME_CSS}}": _theme_css(_load_theme()),
        "{{APP_CSS}}": css,
        "{{REVIEW_JSON}}": _json_for_script(model),
        "{{APP_JS}}": javascript,
    }
    rendered = template
    for placeholder, content in replacements.items():
        if rendered.count(placeholder) != 1:
            raise ManifestError(
                f"review template placeholder must appear exactly once: {placeholder}"
            )
        rendered = rendered.replace(placeholder, content)
    if any(placeholder in rendered for placeholder in replacements):
        raise ManifestError("review template contains an unresolved placeholder")
    return rendered
