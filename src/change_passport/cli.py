from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .git_evidence import GitEvidenceError
from .models import ManifestError
from .pipeline import (
    analyze_sample,
    approve_baseline_proposal,
    finalize_brief,
    prepare_sample,
    score_sample,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="change-passport",
        description="Evidence-bound change brief experiment",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    prepare = subcommands.add_parser("prepare", help="collect evidence and write a generator packet")
    prepare.add_argument("manifest")
    prepare.add_argument("--output", required=True)

    analyze = subcommands.add_parser(
        "analyze",
        help="run the deterministic local path and create an owner-facing candidate report",
    )
    analyze.add_argument("manifest")
    analyze.add_argument("--output", required=True)
    analyze.add_argument(
        "--generator",
        choices=("deterministic", "model"),
        default="deterministic",
        help="candidate wording generator; deterministic remains the default",
    )
    analyze.add_argument(
        "--model-config",
        help="OpenAI-compatible provider config JSON; required with --generator model",
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "analyze":
            result = analyze_sample(
                args.manifest,
                args.output,
                generator=args.generator,
                model_config_path=args.model_config,
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
    except (ManifestError, GitEvidenceError, OSError) as exc:
        print(
            json.dumps(
                {"ok": False, "error_type": type(exc).__name__, "error": str(exc)},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps({"ok": True, **result}, ensure_ascii=False))
    return 0
