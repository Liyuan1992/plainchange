from __future__ import annotations

import ast
import re
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable

from .git_evidence import read_git_blob
from .models import sha256_bytes


_DECLARATION_PATHS = ("README.md", "README.rst")
_MAX_IDENTIFIER_SCAN_FILES = 384
_WORKFLOW_HEADINGS = {
    "pipeline",
    "workflow",
    "how it works",
    "how this works",
    "processing pipeline",
    "流程",
    "工作流程",
    "处理流程",
    "运行流程",
    "软件怎么工作",
}
_CAPABILITY_HEADING_SIGNALS = {
    "capabilities",
    "features",
    "what it does",
    "overview",
    "current status",
    "current progress",
    "功能",
    "能力",
    "核心能力",
    "项目概览",
    "当前进度",
    "主要功能",
}
_CAPABILITY_HEADING_PENALTIES = {
    "changelog",
    "release notes",
    "installation",
    "quickstart",
    "roadmap",
    "license",
    "contributing",
    "更新日志",
    "安装",
    "快速开始",
    "路线图",
    "许可证",
}
_ORCHESTRATOR_STEMS = {
    "app",
    "application",
    "cli",
    "command",
    "commands",
    "main",
    "orchestrator",
    "pipeline",
    "runner",
    "workflow",
}
_COMMON_STAGE_LABELS = {
    "validate": "检查配置和输入",
    "validation": "检查配置和输入",
    "synthesize": "生成所需内容",
    "synthesis": "生成所需内容",
    "timeline": "编排处理顺序",
    "sample": "生成短样本",
    "render": "生成最终内容",
    "qa": "检查结果质量",
    "quality": "检查结果质量",
    "build": "完成需要更新的步骤",
    "publish": "发布结果",
    "deploy": "部署软件",
    "ingest": "接收并导入输入",
    "extract": "提取需要的信息",
    "transform": "整理和转换内容",
    "load": "载入结果",
    "test": "运行检查",
}

_WEAK_CODE_TOKENS = {
    "app",
    "application",
    "core",
    "data",
    "digital",
    "docs",
    "engine",
    "main",
    "package",
    "project",
    "runtime",
    "self",
    "src",
    "system",
    "test",
    "tests",
    "workflow",
}

# These families describe common software responsibilities, not product-specific
# business stages. They are used only inside an explicitly anchored code scope
# and never establish runtime order.
_INTERNAL_RESPONSIBILITY_FAMILIES = (
    (
        "input",
        "接收输入与会话",
        "接收调用方交来的内容，并维护这次交互需要的会话信息。",
        {"entry", "input", "message", "messages", "request", "session", "turn", "turns"},
    ),
    (
        "context",
        "准备上下文与已有信息",
        "整理本次处理需要的上下文、提示、记忆或已保存信息。",
        {"context", "memory", "payload", "prompt", "prompts", "selection"},
    ),
    (
        "decision",
        "判断如何处理",
        "根据规则、权限和当前状态判断接下来可以使用哪些能力。",
        {"capability", "decision", "permission", "permissions", "policy", "route", "router", "visibility"},
    ),
    (
        "execution",
        "执行实际处理工作",
        "调用实际处理能力，并协调任务、工具或并行工作。",
        {"agent", "batch", "execute", "execution", "native", "parallel", "runtime", "skill", "skills", "tool", "tools"},
    ),
    (
        "delivery",
        "整理并交付结果",
        "把处理结果整理成调用方可以接收的形式，并完成必要的交接。",
        {"handoff", "output", "rendering", "response", "result", "results"},
    ),
    (
        "state",
        "记录状态与过程",
        "记录处理中产生的状态、事件、缓存或可追踪过程信息。",
        {"cache", "event", "events", "ledger", "receipt", "state", "status", "storage", "store"},
    ),
)


def _git_source_ref(commit: str, path: str, content: bytes | None = None) -> str:
    result = f"git:{commit}:{path}"
    if content is not None:
        result += f":sha256:{sha256_bytes(content)}"
    return result


def collect_declarations(
    repo: Path,
    commit: str,
    tree: Iterable[str],
    timeout: int,
) -> list[dict[str, str]]:
    available = set(tree)
    declarations: list[dict[str, str]] = []
    for path in _DECLARATION_PATHS:
        if path not in available:
            continue
        raw = read_git_blob(repo, commit, path, timeout)[:64_000]
        declarations.append(
            {
                "path": path,
                "text": raw.decode("utf-8", errors="replace"),
                "source_ref": _git_source_ref(commit, path, raw),
            }
        )
    return declarations


def _strip_markdown(value: str) -> str:
    value = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = value.replace("**", "").replace("__", "").replace("`", "")
    return re.sub(r"\s+", " ", value).strip(" -\t")


def declared_purpose(
    declarations: list[dict[str, str]],
    fallback: str,
    project_kind: str,
) -> dict[str, Any]:
    for declaration in declarations:
        sections = _heading_sections(declaration["text"])
        candidates = [
            body
            for heading, body in sections
            if heading in {"about", "overview", "introduction", "简介", "项目简介"}
        ]
        candidates.append(declaration["text"].splitlines())
        declared = ""
        for lines in candidates:
            paragraph: list[str] = []
            started = False
            in_fence = False
            for raw_line in lines:
                line = raw_line.strip()
                if line.startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                if not line:
                    if started:
                        break
                    continue
                if line.startswith(("#", ".. ", "[!", "![", "<", "|", "---", "===")):
                    continue
                cleaned = _strip_markdown(line)
                lower = cleaned.lower()
                if (
                    not cleaned
                    or lower.startswith(("documentation:", "source code:"))
                    or ("http" in lower and len(cleaned) < 160)
                ):
                    continue
                if len(cleaned) < 18:
                    continue
                paragraph.append(cleaned)
                started = True
            if paragraph:
                declared = " ".join(paragraph)[:600]
                break
        if not declared:
            continue
        owner_text = declared
        lower = declared.lower()
        if project_kind == "video_pipeline" or (
            "video" in lower and any(word in lower for word in ("production", "render", "episode"))
        ):
            owner_text = "根据项目配置制作系列或单集视频，并完成内容生成、渲染和质量检查。"
        return {
            "text": owner_text,
            "declared_text": declared,
            "statement_state": "project_declared",
            "source_refs": [declaration["source_ref"]],
        }
    return {
        "text": fallback,
        "declared_text": "",
        "statement_state": "unknown",
        "source_refs": [],
    }


def _heading_sections(text: str) -> list[tuple[str, list[str]]]:
    lines = text.splitlines()
    result: list[tuple[str, list[str]]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^\s*(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        level = len(match.group(1))
        heading = _strip_markdown(match.group(2)).lower().rstrip(":：")
        body: list[str] = []
        cursor = index + 1
        while cursor < len(lines):
            next_heading = re.match(r"^\s*(#{1,6})\s+(.+?)\s*#*\s*$", lines[cursor])
            if next_heading and len(next_heading.group(1)) <= level:
                break
            body.append(lines[cursor])
            cursor += 1
        result.append((heading, body))
    return result


def _workflow_lines(section: list[str]) -> list[str]:
    fenced: list[str] = []
    current: list[str] = []
    in_fence = False
    for raw_line in section:
        if raw_line.strip().startswith("```"):
            if in_fence and current:
                fenced.extend(current)
                current = []
            in_fence = not in_fence
            continue
        if in_fence:
            current.append(raw_line)
    if fenced:
        return fenced
    return section


def _identifier_tokens(value: str) -> list[str]:
    tokens = re.findall(
        r"[A-Za-z][A-Za-z0-9]*", value.lower().replace("_", " ").replace("-", " ")
    )
    ignored = {"and", "or", "the", "a", "an", "to", "from", "with", "then"}
    return [token for token in tokens if token not in ignored]


def _step_id(key: str, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
    return f"declared-{slug[:48]}" if slug else f"declared-step-{index + 1}"


def _owner_label(key: str, description: str) -> str:
    tokens = _identifier_tokens(key)
    lower_description = description.lower()
    contextual = {
        "synthesize": "生成语音" if any(word in lower_description for word in ("wav", "audio", "speech", "voice")) else "生成所需内容",
        "timeline": "编排视频时间线" if any(word in lower_description for word in ("subtitle", "sound", "mix", "audio")) else "编排处理顺序",
        "render": "渲染完整视频" if any(word in lower_description for word in ("frame", "ffmpeg", "mp4", "video")) else "生成最终内容",
        "qa": "检查视频质量" if any(word in lower_description for word in ("video", "delivery", "render")) else "检查结果质量",
        "build": "按顺序完成制作" if "stage" in lower_description else "完成需要更新的步骤",
    }
    for token in tokens:
        if token in contextual:
            return contextual[token]
        if token in _COMMON_STAGE_LABELS:
            return _COMMON_STAGE_LABELS[token]
    return _strip_markdown(key)[:72]


def _owner_description(key: str, description: str) -> str:
    token = next(iter(_identifier_tokens(key)), "")
    descriptions = {
        "validate": "检查配置、输入和所需素材是否可用。",
        "validation": "检查配置、输入和所需素材是否可用。",
        "synthesize": "生成后续处理需要的内容；输入没有变化时可以复用已有结果。",
        "synthesis": "生成后续处理需要的内容；输入没有变化时可以复用已有结果。",
        "timeline": "根据已经生成的内容安排时间顺序。",
        "sample": "完整处理前先生成一个较短样本，用来提前检查效果。",
        "render": "生成最终内容以及便于检查的辅助结果。",
        "qa": "按照项目规则检查结果，并生成质量说明。",
        "quality": "按照项目规则检查结果，并生成质量说明。",
        "build": "按照项目声明的顺序，只执行需要更新的步骤。",
    }
    return descriptions.get(token, description)


def _parse_workflow_steps(lines: list[str]) -> list[dict[str, Any]]:
    useful = [line.strip() for line in lines if line.strip() and not line.strip().startswith(("#", "$"))]
    if len(useful) == 1 and len(re.split(r"\s*(?:->|→|⇒)\s*", useful[0])) >= 4:
        parts = [_strip_markdown(item) for item in re.split(r"\s*(?:->|→|⇒)\s*", useful[0])]
        useful = [part for part in parts if part]
    parsed: list[tuple[str, str]] = []
    for raw_line in useful:
        line = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", raw_line).strip()
        if not line or line.startswith(("|", "---")):
            continue
        match = re.match(r"^(.{1,72}?)\s*(?:->|→|⇒|:\s|：\s*)\s*(.+)$", line)
        if match:
            key = _strip_markdown(match.group(1))
            description = _strip_markdown(match.group(2))
        elif re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)", raw_line):
            key = _strip_markdown(line)
            description = f"项目说明把“{key}”列为一个工作步骤。"
        else:
            key = _strip_markdown(line)
            description = f"项目说明把“{key}”列为一个工作步骤。"
        if not key or len(key) > 72 or len(description) > 600:
            continue
        parsed.append((key, description))
    if not 4 <= len(parsed) <= 16:
        return []
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for index, (key, description) in enumerate(parsed):
        step_id = _step_id(key, index)
        if step_id in seen:
            step_id = f"{step_id}-{index + 1}"
        seen.add(step_id)
        result.append(
            {
                "id": step_id,
                "key": key,
                "tokens": _identifier_tokens(key),
                "label": _owner_label(key, description),
                "description": _owner_description(key, description),
                "declared_text": description,
                "type": "input" if index == 0 else "output" if index == len(parsed) - 1 else "process",
            }
        )
    return result


def extract_declared_workflow(
    declarations: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[str]]:
    for declaration in declarations:
        for heading, body in _heading_sections(declaration["text"]):
            if heading not in _WORKFLOW_HEADINGS:
                continue
            steps = _parse_workflow_steps(_workflow_lines(body))
            if steps:
                return steps, [declaration["source_ref"]]
    return [], []


def _capability_id(label: str, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return f"declared-capability-{slug[:42]}" if slug else f"declared-capability-{index + 1}"


def _capability_item(
    label: str,
    raw_description: str,
    index: int,
    *,
    token_source: str | None = None,
) -> dict[str, Any] | None:
    label = _strip_markdown(label).rstrip(":：")[:72]
    code_tokens = re.findall(r"`([^`]{1,160})`", token_source or raw_description)
    description = _strip_markdown(raw_description).lstrip(" (:：—-）)")[:600]
    if not label or not description or len(label) > 72:
        return None
    tokens = _identifier_tokens(" ".join([label, *code_tokens]))
    return {
        "id": _capability_id(label, index),
        "key": label,
        "tokens": tokens,
        "label": label,
        "description": description,
        "declared_text": description,
        "explicit_refs": code_tokens,
        "type": "capability",
    }


def _bullet_capability_groups(lines: list[str]) -> list[list[dict[str, Any]]]:
    groups: list[list[dict[str, Any]]] = []
    group: list[tuple[str, str]] = []
    current: tuple[str, list[str]] | None = None

    def finish_item() -> None:
        nonlocal current
        if current is not None:
            group.append((current[0], " ".join(current[1])))
            current = None

    def finish_group() -> None:
        finish_item()
        if 3 <= len(group) <= 12:
            parsed = [
                item
                for index, (label, description) in enumerate(group)
                if (item := _capability_item(label, description, index)) is not None
            ]
            if 3 <= len(parsed) <= 10:
                groups.append(parsed)
        group.clear()

    after_blank = False
    for raw_line in lines:
        line = raw_line.rstrip()
        if re.match(r"^\s*#{1,6}\s+", line):
            finish_group()
            after_blank = False
            continue
        match = re.match(r"^\s*[-*+]\s+\*\*(.{1,96}?)\*\*(.*)$", line)
        if match:
            finish_item()
            current = (match.group(1), [match.group(2)])
            after_blank = False
            continue
        if current is not None and (not line.strip() or line[:1].isspace()):
            if line.strip():
                current[1].append(line.strip())
            after_blank = not line.strip()
            continue
        if current is not None:
            finish_group()
        elif group and (line.strip() or after_blank):
            finish_group()
        after_blank = not line.strip()
    finish_group()
    return groups


def _table_capabilities(lines: list[str]) -> list[list[dict[str, Any]]]:
    groups: list[list[dict[str, Any]]] = []
    cursor = 0
    while cursor + 2 < len(lines):
        header = lines[cursor].strip()
        separator = lines[cursor + 1].strip()
        if not (
            header.startswith("|")
            and separator.startswith("|")
            and re.fullmatch(r"[|:\-\s]+", separator)
        ):
            cursor += 1
            continue
        header_cells = [cell.strip().casefold() for cell in header.strip("|").split("|")]
        description_signals = {
            "description", "details", "coverage", "covered features", "features",
            "purpose", "responsibility", "说明", "描述", "覆盖功能", "功能", "职责",
        }
        description_index = next(
            (index for index, cell in enumerate(header_cells) if cell in description_signals),
            1,
        )
        rows: list[list[str]] = []
        cursor += 2
        while cursor < len(lines) and lines[cursor].strip().startswith("|"):
            cells = [cell.strip() for cell in lines[cursor].strip().strip("|").split("|")]
            if len(cells) >= 2:
                rows.append(cells)
            cursor += 1
        if 3 <= len(rows) <= 12:
            parsed: list[dict[str, Any]] = []
            for index, cells in enumerate(rows[:10]):
                raw_description = cells[
                    description_index if description_index < len(cells) else 1
                ]
                item = _capability_item(
                    cells[0],
                    raw_description,
                    index,
                    token_source=" ".join(cells[1:]),
                )
                if item is not None:
                    parsed.append(item)
            if len(parsed) >= 3:
                groups.append(parsed)
    return groups


def extract_declared_capabilities(
    declarations: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[str]]:
    candidates: list[tuple[int, int, list[dict[str, Any]], str]] = []
    sequence = 0
    for declaration in declarations:
        sections = _heading_sections(declaration["text"])
        if not sections:
            sections = [("", declaration["text"].splitlines())]
        for heading, body in sections:
            lowered = heading.lower()
            heading_score = 12 if any(signal in lowered for signal in _CAPABILITY_HEADING_SIGNALS) else 0
            if any(signal in lowered for signal in _CAPABILITY_HEADING_PENALTIES):
                heading_score -= 18
            for group in [*_bullet_capability_groups(body), *_table_capabilities(body)]:
                descriptive = sum(len(item["description"]) >= 24 for item in group)
                tokenized = sum(bool(item["tokens"]) for item in group)
                # The deterministic owner draft is Chinese today. When the
                # same README contains equivalent bilingual capability lists,
                # prefer the list already written in the output language rather
                # than translating or rewriting source claims.
                output_language_match = sum(
                    bool(re.search(r"[\u3400-\u9fff]", str(item["label"])))
                    for item in group
                )
                score = (
                    heading_score
                    + len(group) * 3
                    + descriptive
                    + tokenized
                    + output_language_match * 2
                )
                candidates.append((score, -sequence, group, declaration["source_ref"]))
                sequence += 1
    if not candidates:
        return [], []
    _, _, capabilities, source_ref = max(candidates, key=lambda item: (item[0], item[1]))
    seen: set[str] = set()
    for index, capability in enumerate(capabilities):
        capability_id = capability["id"]
        if capability_id in seen:
            capability["id"] = f"{capability_id}-{index + 1}"
        seen.add(capability["id"])
    return capabilities, [source_ref]


def _token_matches_name(token: str, name: str) -> bool:
    token = re.sub(r"[^a-z0-9]+", "", token.lower())
    name = re.sub(r"[^a-z0-9]+", "", name.lower())
    return bool(token and token == name)


def _path_matches_tokens(path: str, tokens: list[str]) -> bool:
    names = [part.lower() for part in re.split(r"[^A-Za-z0-9]+", path) if part]
    useful = [
        token
        for token in tokens
        if (
            len(re.sub(r"[^a-z0-9]+", "", token.lower())) >= 4
            or token.lower() in _COMMON_STAGE_LABELS
        )
        and token.lower() not in _WEAK_CODE_TOKENS
    ]
    return any(_token_matches_name(token, name) for token in useful for name in names)


def _explicit_anchor_paths(explicit_refs: list[str], supported: list[str]) -> list[str]:
    result: list[str] = []
    for raw_ref in explicit_refs:
        candidate = raw_ref.strip().replace("\\", "/").removeprefix("./")
        candidate = candidate.split("#", 1)[0].strip()
        if not candidate:
            continue
        path_like = "/" in candidate or bool(PurePosixPath(candidate).suffix)
        if path_like:
            prefix = candidate.rstrip("/")
            matches = [
                path
                for path in supported
                if path == prefix or path.startswith(prefix + "/")
            ]
            if not matches and "/" not in candidate:
                basename_matches = [
                    path for path in supported if PurePosixPath(path).name == candidate
                ]
                matches = basename_matches if len(basename_matches) == 1 else []
            result.extend(matches)
            continue
        if candidate.lower() in _WEAK_CODE_TOKENS:
            continue
        result.extend(
            path
            for path in supported
            if _path_matches_tokens(path, [candidate])
        )
    return list(dict.fromkeys(result))


def _explicit_identifiers(explicit_refs: list[str]) -> set[str]:
    result: set[str] = set()
    for raw_ref in explicit_refs:
        if "/" in raw_ref or "\\" in raw_ref or "://" in raw_ref:
            continue
        for candidate in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", raw_ref):
            lowered = candidate.lower()
            if "_" in candidate or any(character.isupper() for character in candidate[1:]):
                if lowered not in _WEAK_CODE_TOKENS:
                    result.add(candidate)
    return result


def _source_identifiers(path: str, text: str) -> set[str]:
    if path.endswith(".py"):
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return set()
        result: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                result.add(node.name)
            elif isinstance(node, ast.Name):
                result.add(node.id)
            elif isinstance(node, ast.Attribute):
                result.add(node.attr)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{3,}", node.value):
                    result.add(node.value)
        return result
    return set(re.findall(r"\b[A-Za-z_$][A-Za-z0-9_$]{3,}\b", text))


def _internal_capability_details(
    step: dict[str, Any],
    anchors: list[str],
    declaration_refs: list[str],
    commit: str,
    category_for_path: Callable[[str], str],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = {}
    family_lookup = {item[0]: item for item in _INTERNAL_RESPONSIBILITY_FAMILIES}
    assignment_order = ("state", "delivery", "decision", "context", "input", "execution")
    eligible_anchors = [
        path
        for path in anchors[:96]
        if not path.lower().startswith(("tests/", "test/", "docs/", "design/"))
    ]
    for path in eligible_anchors:
        stem_tokens = {
            token.lower()
            for token in re.split(r"[^A-Za-z0-9]+", PurePosixPath(path).stem)
            if token and token.lower() not in {"init", "base", "constants", "helpers", "utils"}
        }
        for family_id in assignment_order:
            signals = family_lookup[family_id][3]
            if stem_tokens & signals:
                grouped.setdefault(family_id, []).append(path)
                break
    populated = [family_id for family_id, paths in grouped.items() if paths]
    if len(populated) < 2 or sum(len(paths) for paths in grouped.values()) < 3:
        return []
    details: list[dict[str, Any]] = []
    for family_id, label, description, _ in _INTERNAL_RESPONSIBILITY_FAMILIES:
        paths = grouped.get(family_id, [])
        if not paths:
            continue
        details.append(
            {
                "id": f"{step['id']}.{family_id}",
                "type": "capability",
                "label": label,
                "description": description,
                "group_ids": sorted({category_for_path(path) for path in paths}),
                "evidence_status": "code_discovered",
                "evidence_label": "从代码结构发现",
                "evidence_note": "在这项能力明确引用的代码范围内，根据固定版本的文件和标识符名称形成候选职责；它不是项目声明或运行验证，仍需负责人确认。",
                "source_refs": [
                    *declaration_refs,
                    *[_git_source_ref(commit, path) for path in paths[:4]],
                ],
            }
        )
    return details[:6]


def _orchestrator_paths(supported: list[str]) -> list[str]:
    candidates = []
    for path in supported:
        posix = PurePosixPath(path)
        stem = posix.stem.lower()
        parts = {part.lower() for part in posix.parts}
        if stem in _ORCHESTRATOR_STEMS or parts & {"commands", "pipeline", "workflows"}:
            candidates.append(path)
    return sorted(candidates, key=lambda item: (len(PurePosixPath(item).parts), item))[:48]


def _call_sequences(path: str, text: str) -> list[tuple[str, list[str]]]:
    if not path.endswith(".py"):
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    sequences: list[tuple[str, list[str]]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        function_words = set(_identifier_tokens(node.name))
        if not function_words & {
            "build",
            "execute",
            "main",
            "orchestrate",
            "pipeline",
            "process",
            "run",
        } and not any(
            word.startswith(("build_", "run_", "execute_", "process_"))
            for word in function_words
        ):
            continue
        calls: list[tuple[int, int, str]] = []
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            function = child.func
            if isinstance(function, ast.Name):
                name = function.id
            elif isinstance(function, ast.Attribute):
                name = function.attr
                if "_" not in name and name.lower() in _COMMON_STAGE_LABELS:
                    # A generic method such as issues.render() is not evidence
                    # that the workflow's render stage ran.
                    continue
            else:
                continue
            calls.append((getattr(child, "lineno", 0), getattr(child, "col_offset", 0), name))
        calls.sort()
        if calls:
            sequences.append((node.name, [name for _, _, name in calls]))
    return sequences


def _matched_step_index(name: str, steps: list[dict[str, Any]]) -> int | None:
    names = _identifier_tokens(name)
    for index, step in enumerate(steps):
        if any(_token_matches_name(token, candidate) for token in step["tokens"] for candidate in names):
            return index
    return None


def reconcile_workflow(
    repo: Path,
    commit: str,
    timeout: int,
    supported: list[str],
    declarations: list[dict[str, str]],
    category_for_path: Callable[[str], str],
) -> dict[str, Any] | None:
    steps, declaration_refs = extract_declared_workflow(declarations)
    if not steps:
        steps, declaration_refs = extract_declared_capabilities(declarations)
        if not steps:
            return None
        structure_kind = "capability_map"
    else:
        structure_kind = "workflow"
    orchestrators: list[dict[str, Any]] = []
    source_identifier_cache: dict[str, set[str]] = {}
    for path in _orchestrator_paths(supported):
        raw = read_git_blob(repo, commit, path, timeout)[:128_000]
        text = raw.decode("utf-8", errors="replace")
        orchestrators.append(
            {
                "path": path,
                "text": text,
                "source_ref": _git_source_ref(commit, path, raw),
                "call_sequences": _call_sequences(path, text),
            }
        )
    for step in steps:
        explicit_refs = [str(ref) for ref in step.get("explicit_refs", [])]
        anchors = _explicit_anchor_paths(explicit_refs, supported)
        explicit_identifiers = _explicit_identifiers(explicit_refs)
        if explicit_identifiers and not anchors:
            identifier_candidates = sorted(
                (
                    path
                    for path in supported
                    if not path.lower().startswith(("tests/", "test/", "docs/", "design/"))
                ),
                key=lambda path: (len(PurePosixPath(path).parts), len(path), path),
            )[:_MAX_IDENTIFIER_SCAN_FILES]
            for path in identifier_candidates:
                if path not in source_identifier_cache:
                    raw = read_git_blob(repo, commit, path, timeout)[:256_000]
                    source_identifier_cache[path] = _source_identifiers(
                        path, raw.decode("utf-8", errors="replace")
                    )
                if explicit_identifiers & source_identifier_cache[path]:
                    anchors.append(path)
        if not anchors and not explicit_refs:
            anchors = [path for path in supported if _path_matches_tokens(path, step["tokens"])]
            useful_tokens = [
                token
                for token in step["tokens"]
                if token.lower() not in _WEAK_CODE_TOKENS and len(token) >= 4
            ]
            for item in orchestrators:
                if any(
                    re.search(rf"(?i)(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])", item["text"])
                    for token in useful_tokens
                ):
                    anchors.append(item["path"])
        anchors = sorted(
            dict.fromkeys(anchors),
            key=lambda path: (
                PurePosixPath(path).stem.lower()
                in {"__init__", "constants", "helpers", "utils", "base"},
                len(PurePosixPath(path).parts),
                path,
            ),
        )[:96]
        step["group_ids"] = sorted({category_for_path(path) for path in anchors})
        step["evidence_status"] = "declared_and_code_supported" if anchors else "declared_only"
        step["evidence_label"] = "找到对应代码" if anchors else "仅来自项目说明"
        step["evidence_note"] = (
            "项目说明中的这一步在固定版本代码里找到了对应入口或实现位置；仍未运行验证。"
            if anchors
            else "项目说明提到了这一步，但在当前限定代码范围内没有找到稳定对应位置。"
        )
        step["source_refs"] = [*declaration_refs, *[_git_source_ref(commit, path) for path in anchors[:5]]]
        step["details"] = (
            _internal_capability_details(
                step,
                anchors,
                declaration_refs,
                commit,
                category_for_path,
            )
            if structure_kind == "capability_map"
            else []
        )

    if structure_kind == "capability_map":
        return {
            "kind": structure_kind,
            "steps": steps,
            "source_refs": declaration_refs,
            "order_status": "not_applicable",
            "order_label": "没有先后顺序",
            "order_note": "项目说明把这些内容描述为并列能力，不代表调用顺序或运行时先后。",
            "order_source_refs": declaration_refs,
        }

    best_supported = 0
    conflict_ref: str | None = None
    order_ref: str | None = None
    full_support = False
    for item in orchestrators:
        for function_name, calls in item["call_sequences"]:
            indexes = [_matched_step_index(name, steps) for name in calls]
            compact: list[int] = []
            for index in (value for value in indexes if value is not None):
                if not compact or compact[-1] != index:
                    compact.append(index)
            distinct = list(dict.fromkeys(compact))
            if len(distinct) < 3:
                continue
            if distinct != sorted(distinct):
                conflict_ref = f"{item['source_ref']}:function:{function_name}"
                continue
            if len(distinct) > best_supported:
                best_supported = len(distinct)
                order_ref = f"{item['source_ref']}:function:{function_name}"
            if distinct == list(range(len(steps))):
                full_support = True
    if conflict_ref:
        order_status = "conflicting"
        order_label = "顺序有冲突"
        order_note = "项目说明给出的步骤顺序与至少一处编排代码中的调用顺序不一致；不能把文档顺序当成实际顺序。"
        order_refs = [*declaration_refs, conflict_ref]
    elif full_support:
        order_status = "code_supported"
        order_label = "代码支持该顺序"
        order_note = "固定版本的一处编排函数按项目说明的完整顺序引用了这些步骤；仍未运行验证。"
        order_refs = [*declaration_refs, order_ref] if order_ref else declaration_refs
    elif best_supported >= 3:
        order_status = "partially_supported"
        order_label = "顺序部分支持"
        order_note = "编排代码支持其中一部分先后关系，但没有覆盖项目说明中的全部步骤；完整运行顺序仍未验证。"
        order_refs = [*declaration_refs, order_ref] if order_ref else declaration_refs
    else:
        order_status = "unverified"
        order_label = "顺序未验证"
        order_note = "当前只能确认项目说明列出了这些步骤，还没有足够编排代码证明它们的完整先后顺序。"
        order_refs = declaration_refs
    return {
        "kind": structure_kind,
        "steps": steps,
        "source_refs": declaration_refs,
        "order_status": order_status,
        "order_label": order_label,
        "order_note": order_note,
        "order_source_refs": [ref for ref in order_refs if ref],
    }
