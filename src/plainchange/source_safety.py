"""Conservative pre-send guard for common embedded credential formats.

This is pattern detection, not a guarantee that project text is non-sensitive.
Never include the matched value in errors or receipts.
"""
from __future__ import annotations

import re

from .model_adapter import ModelGenerationError

_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"\b(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16})\b"),
    re.compile(r'''(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)\s*[:=]\s*["']([^"'\r\n]{12,})["']'''),
)
_PLACEHOLDER = re.compile(r"(?i)^(?:your[-_ ].*|example[-_ ].*|placeholder.*|test[-_ ].*|dummy[-_ ].*|\$\{.*\}|<.*>|x+)$")


class SensitiveSourceError(ModelGenerationError):
    pass


def assert_safe_source(text: str) -> None:
    for pattern in _PATTERNS:
        for match in pattern.finditer(text):
            if match.lastindex and _PLACEHOLDER.fullmatch(match.group(1)):
                continue
            raise SensitiveSourceError("源文本疑似包含凭据，已阻止进入模型输入；请检查源文件并移除敏感内容。")
