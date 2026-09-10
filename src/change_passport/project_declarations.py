from __future__ import annotations

import ast
import re
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable

from .git_evidence import read_git_blob
from .models import sha256_bytes


_DECLARATION_PATHS = ("README.md", "README.rst")
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


def _token_matches_name(token: str, name: str) -> bool:
    token = token.lower().replace("-", "_")
    name = name.lower().replace("-", "_")
    if token == name:
        return True
    if len(token) >= 5 and len(name) >= 5:
        return token[:5] == name[:5]
    return False


def _path_matches_tokens(path: str, tokens: list[str]) -> bool:
    names = [part.lower() for part in re.split(r"[^A-Za-z0-9]+", path) if part]
    return any(_token_matches_name(token, name) for token in tokens for name in names)


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
        return None
    orchestrators: list[dict[str, Any]] = []
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
        anchors = [path for path in supported if _path_matches_tokens(path, step["tokens"])]
        for item in orchestrators:
            if any(re.search(rf"(?i)\b{re.escape(token)}\w*\b", item["text"]) for token in step["tokens"]):
                anchors.append(item["path"])
        anchors = list(dict.fromkeys(anchors))[:8]
        step["group_ids"] = sorted({category_for_path(path) for path in anchors})
        step["evidence_status"] = "declared_and_code_supported" if anchors else "declared_only"
        step["evidence_label"] = "找到对应代码" if anchors else "仅来自项目说明"
        step["evidence_note"] = (
            "项目说明中的这一步在固定版本代码里找到了对应入口或实现位置；仍未运行验证。"
            if anchors
            else "项目说明提到了这一步，但在当前限定代码范围内没有找到稳定对应位置。"
        )
        step["source_refs"] = [*declaration_refs, *[_git_source_ref(commit, path) for path in anchors[:5]]]

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
        "steps": steps,
        "source_refs": declaration_refs,
        "order_status": order_status,
        "order_label": order_label,
        "order_note": order_note,
        "order_source_refs": [ref for ref in order_refs if ref],
    }
