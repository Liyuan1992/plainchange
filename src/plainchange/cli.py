from __future__ import annotations

import argparse
import json
import locale
import sys
from pathlib import Path
from typing import Sequence

from .git_evidence import GitEvidenceError
from .models import ManifestError
from .onboarding import (
    OnboardingError,
    build_guided_manifest,
    inspect_repository,
    serve_onboarding,
)
from .pipeline import (
    analyze_sample,
    approve_baseline_proposal,
    finalize_brief,
    prepare_sample,
    score_sample,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="plainchange",
        description=(
            "Know what AI changed, what it affects, and what still needs verification."
        ),
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    localize = subcommands.add_parser("localize-report", help="export or apply source-bound report-body translations")
    localize.add_argument("directory")
    options = localize.add_mutually_exclusive_group(required=True)
    options.add_argument("--export", help="create a complete translation template")
    options.add_argument("--translations", help="apply a completed translation JSON")
    localize.add_argument("--language", choices=("en", "zh-CN"), default="en")

    serve = subcommands.add_parser("serve", help="open the guided local web interface")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--no-open", action="store_true", help="do not open the browser automatically")

    prepare = subcommands.add_parser("prepare", help="collect evidence and write a generator packet")
    prepare.add_argument("manifest")
    prepare.add_argument("--output", required=True)

    analyze = subcommands.add_parser(
        "analyze",
        help="analyze a Git project or an advanced manifest and create a Change Passport",
    )
    analyze.add_argument("target", help="Git project directory or sample manifest JSON")
    analyze.add_argument("--output", help="report directory; project mode uses a safe sibling folder")
    analyze.add_argument("--task", default="", help="optional original task or intent")
    analyze.add_argument(
        "--generator",
        choices=("auto", "model", "deterministic"),
        default="auto",
        help=(
            "analysis experience: auto uses a supplied model config or otherwise "
            "creates a clearly limited basic-evidence report"
        ),
    )
    analyze.add_argument(
        "--model-config",
        help="OpenAI-compatible provider config JSON; required with --generator model",
    )
    analyze.add_argument(
        "--human-language",
        choices=("auto", "en", "zh-CN"),
        default="auto",
        help="language requested from the model for owner-facing text; auto follows the system language",
    )

    finalize = subcommands.add_parser("finalize", help="validate model claims and render the brief")
    finalize.add_argument("packet")
    finalize.add_argument("raw_brief")
    finalize.add_argument("--output", required=True)
    finalize.add_argument(
        "--software-control",
        help="optional validated software-control.v1 owner-facing explanation",
    )

    score = subcommands.add_parser("score", help="score a frozen brief from human annotations")
    score.add_argument("brief")
    score.add_argument("annotation")
    score.add_argument("--output", required=True)

    approve = subcommands.add_parser(
        "approve-baseline",
        help="materialize an approved baseline from a proposal and explicit decision",
    )
    approve.add_argument("proposal")
    approve.add_argument("decision")
    approve.add_argument("--output", required=True)
    return parser


def _normalized_argv(argv: Sequence[str] | None) -> list[str]:
    values = list(sys.argv[1:] if argv is None else argv)
    commands = {"serve", "prepare", "analyze", "finalize", "score", "approve-baseline", "localize-report"}
    if values and not values[0].startswith("-") and values[0] not in commands:
        values.insert(0, "analyze")
    return values


def _configure_utf8_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                pass


def _system_human_language() -> str:
    candidates = [locale.getlocale()[0]]
    try:
        candidates.append(locale.setlocale(locale.LC_CTYPE))
    except locale.Error:
        pass
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.casefold().startswith(("zh", "chinese")):
            return "zh-CN"
    return "en"


def main(argv: Sequence[str] | None = None) -> int:
    _configure_utf8_output()
    parser = _parser()
    args = parser.parse_args(_normalized_argv(argv))
    direct_project = False
    try:
        if args.command == "serve":
            serve_onboarding(args.host, args.port, open_browser=not args.no_open)
            return 0
        if args.command == "localize-report":
            from .report_localization import localize_report
            result = localize_report(args.directory, translations=args.translations,
                                     export=args.export, language=args.language)
        elif args.command == "analyze":
            target = Path(args.target).expanduser()
            if target.is_dir():
                direct_project = True
                repository = inspect_repository(target)
                manifest, output, _payload = build_guided_manifest(
                    repository["path"],
                    repository["default_base"],
                    repository["default_head"],
                    task=args.task,
                    output=args.output,
                )
            else:
                if not args.output:
                    raise OnboardingError(
                        "使用 manifest 时请通过 --output 指定报告目录；直接分析项目可运行 plainchange analyze ."
                    )
                manifest, output = target, Path(args.output)
            result = analyze_sample(
                manifest,
                output,
                generator=args.generator,
                model_config_path=args.model_config,
                human_language=(
                    _system_human_language()
                    if args.human_language == "auto"
                    else args.human_language
                ),
            )
        elif args.command == "prepare":
            result = prepare_sample(args.manifest, args.output)
        elif args.command == "finalize":
            result = finalize_brief(
                args.packet,
                args.raw_brief,
                args.output,
                args.software_control,
            )
        elif args.command == "score":
            result = score_sample(args.brief, args.annotation, args.output)
        else:
            result = approve_baseline_proposal(
                args.proposal, args.decision, args.output
            )
    except (ManifestError, GitEvidenceError, OnboardingError, OSError) as exc:
        print(
            json.dumps(
                {"ok": False, "error_type": type(exc).__name__, "error": str(exc)},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2
    if direct_project:
        print("\nChange Passport generated:")
        print(result["review_html"])
    else:
        print(json.dumps({"ok": True, **result}, ensure_ascii=False))
    return 0
