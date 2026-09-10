from __future__ import annotations

import re
from dataclasses import dataclass


_DIFF_PATH = re.compile(r"^\+\+\+ b/(.+)$")
_HUNK_CONTEXT = re.compile(r"^@@ .*? @@\s*(.*)$")
_FUNCTION = re.compile(r"^\s*(?:async\s+def|def)\s+([A-Za-z_][A-Za-z0-9_]*)\s*(\(.*)$")
_CLASS = re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\b")
_CONDITION = re.compile(r"^\s*(?:if|elif)\s+(.+):\s*$")
_RAISE = re.compile(r"^\s*raise\s+([A-Za-z_][A-Za-z0-9_.]*)\b")
_RETURN_INTEGER = re.compile(r"^\s*return\s+(-?\d+)\s*(?:#.*)?$")


@dataclass(frozen=True)
class BehaviorSignal:
    kind: str
    path: str
    symbol: str | None
    condition: str | None
    detail: str

    def evidence_content(self) -> str:
        fields = [f"kind={self.kind}", f"path={self.path}"]
        if self.symbol:
            fields.append(f"symbol={self.symbol}")
        if self.condition:
            fields.append(f"condition={self.condition}")
        fields.append(f"detail={self.detail}")
        return "; ".join(fields)


def _indent(value: str) -> int:
    return len(value) - len(value.lstrip(" \t"))


def _definition_name(value: str) -> tuple[str, str] | None:
    function = _FUNCTION.match(value)
    if function:
        return function.group(1), function.group(2).strip()
    return None


def extract_behavior_signals(patch: str) -> list[BehaviorSignal]:
    """Extract conservative code-behavior signals from added Python diff lines.

    These are syntactic Git facts. They deliberately do not claim that a branch is
    reachable, breaking, executed, or user-visible.
    """

    signals: list[BehaviorSignal] = []
    current_path: str | None = None
    current_symbol: str | None = None
    condition_stack: list[tuple[int, str]] = []
    removed_definitions: dict[tuple[str, str], str] = {}
    added_definitions: dict[tuple[str, str], str] = {}

    for raw_line in patch.splitlines():
        path_match = _DIFF_PATH.match(raw_line)
        if path_match:
            current_path = path_match.group(1)
            current_symbol = None
            condition_stack = []
            continue
        if current_path is None or not current_path.endswith(".py"):
            continue
        hunk_match = _HUNK_CONTEXT.match(raw_line)
        if hunk_match:
            current_symbol = None
            condition_stack = []
            context = hunk_match.group(1)
            function = _FUNCTION.match(context)
            class_match = _CLASS.match(context)
            if function:
                current_symbol = function.group(1)
            elif class_match:
                current_symbol = class_match.group(1)
            continue
        if raw_line.startswith(("diff --git", "index ", "--- ")):
            continue
        if not raw_line or raw_line[0] not in {" ", "+", "-"}:
            continue

        marker = raw_line[0]
        code = raw_line[1:]
        definition = _definition_name(code)
        if definition:
            key = (current_path, definition[0])
            if marker == "-":
                removed_definitions[key] = definition[1]
            elif marker == "+":
                added_definitions[key] = definition[1]

        if marker == "-":
            continue

        function = _FUNCTION.match(code)
        class_match = _CLASS.match(code)
        if function:
            current_symbol = function.group(1)
            condition_stack = []
        elif class_match:
            current_symbol = class_match.group(1)
            condition_stack = []

        stripped = code.strip()
        if not stripped or stripped.startswith("#"):
            continue
        line_indent = _indent(code)
        while condition_stack and condition_stack[-1][0] >= line_indent:
            condition_stack.pop()
        condition_match = _CONDITION.match(code)
        if condition_match:
            condition_stack.append((line_indent, condition_match.group(1).strip()))
            continue
        if marker != "+":
            continue

        condition = condition_stack[-1][1] if condition_stack else None
        raise_match = _RAISE.match(code)
        if raise_match:
            signals.append(
                BehaviorSignal(
                    kind="added_exception_raise",
                    path=current_path,
                    symbol=current_symbol,
                    condition=condition,
                    detail=raise_match.group(1),
                )
            )
            continue
        return_match = _RETURN_INTEGER.match(code)
        if return_match and int(return_match.group(1)) != 0:
            signals.append(
                BehaviorSignal(
                    kind="added_nonzero_return",
                    path=current_path,
                    symbol=current_symbol,
                    condition=condition,
                    detail=return_match.group(1),
                )
            )

    for key in sorted(set(removed_definitions) & set(added_definitions)):
        before = removed_definitions[key]
        after = added_definitions[key]
        if before == after:
            continue
        signals.append(
            BehaviorSignal(
                kind="changed_callable_signature",
                path=key[0],
                symbol=key[1],
                condition=None,
                detail=f"before={before}; after={after}",
            )
        )

    severity = {
        "added_exception_raise": 0,
        "added_nonzero_return": 1,
        "changed_callable_signature": 2,
    }
    return sorted(
        set(signals),
        key=lambda item: (
            severity.get(item.kind, 99),
            item.path,
            item.symbol or "",
            item.condition or "",
            item.detail,
        ),
    )


def behavior_signal_evidence(
    patch: str,
    *,
    patch_sha256: str,
    patch_truncated: bool,
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for index, signal in enumerate(extract_behavior_signals(patch), start=1):
        limitations = [
            "syntactic diff signal only",
            "does not prove reachability, runtime execution, breaking impact, or user impact",
        ]
        if patch_truncated:
            limitations.append("patch truncated; behavior-signal coverage is incomplete")
        result.append(
            {
                "id": f"git.behavior.{index:03d}",
                "kind": "behavior_signal",
                "authority": "git_fact",
                "content": signal.evidence_content(),
                "source_ref": f"git:patch:{patch_sha256}#behavior-{index:03d}",
                "limitations": limitations,
            }
        )
    return result
