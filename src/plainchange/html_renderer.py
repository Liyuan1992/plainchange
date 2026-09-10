from __future__ import annotations

import base64
import gzip
import json
from importlib import resources
from typing import Any, Mapping

from .models import ManifestError, canonical_json_bytes, sha256_bytes
from .review_model import validate_beginner_review_model
from .software_control import validate_software_control

THEME_SCHEMA = "change-passport.review-theme.v1"
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
            resources.files("plainchange")
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


def _technical_payload(system_architecture: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if system_architecture is None:
        return None
    raw = canonical_json_bytes(system_architecture)
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    return {
        "schema_version": "change-passport.technical-payload.v1",
        "encoding": "gzip+base64",
        "sha256": sha256_bytes(raw),
        "compressed_sha256": sha256_bytes(compressed),
        "uncompressed_bytes": len(raw),
        "compressed_bytes": len(compressed),
        "data": base64.b64encode(compressed).decode("ascii"),
    }


def render_review_html(model_value: Any, software_control_value: Any | None = None) -> str:
    model = validate_beginner_review_model(model_value)
    system_architecture = model.get("system_architecture")
    software_control = None
    if software_control_value is not None:
        software_control = validate_software_control(
            software_control_value,
            review=model,
            system_architecture=system_architecture,
        )
    compact_model = dict(model)
    compact_model.pop("system_architecture", None)
    template = _resource_text("templates/review.html")
    css = _resource_text("templates/review.css")
    javascript = _resource_text("templates/review.js")
    replacements = {
        "{{THEME_CSS}}": _theme_css(_load_theme()),
        "{{APP_CSS}}": css,
        "{{REVIEW_JSON}}": _json_for_script(compact_model),
        "{{SOFTWARE_CONTROL_JSON}}": _json_for_script(software_control),
        "{{TECHNICAL_PAYLOAD_JSON}}": _json_for_script(
            _technical_payload(system_architecture)
        ),
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
