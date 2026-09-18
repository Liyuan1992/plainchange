# TASK-041: Multi-project validation

State: DONE
Tier: standard

The owner asked: “再多测试几个项目，比如我的 memdsl”. This is explicit
approval to run the current PlainChange implementation against several local Git
repositories. It does not authorize changes inside those repositories, model/API
calls, commits, tags, remotes or release publication.

## Scope and plan

- Analyze the latest two committed revisions of `memdsl` first.
- Compare with at least two structurally different committed repositories; use
  `VideoFactory` and `DigitalSelf` if their Git objects are locally available.
- Write reports only under PlainChange-owned `artifacts/` directories.
- Capture before/after target HEAD and status to prove target worktrees unchanged.
- Measure elapsed phases/report size, validate generated contracts, and run DOM
  language/interaction checks where a complete translation pack exists.
- Inspect the actual owner-facing reports for whether project purpose, workflow,
  change location, impact, unknowns and checks remain useful.

## Known limits

- Deterministic reports are authored in Chinese. English body translation still
  requires a source-bound reviewed pack; absence of a pack must be disclosed, not
  silently treated as bilingual coverage.
- Static analysis is not runtime verification or proof of user comprehension.
- Dirty target worktrees are not included in the commit-to-commit comparison.

## Stop condition

Finish after three source-bound reports and cross-project findings, or record an
observed blocker precisely. Apply only repository-neutral fixes revealed by the
samples, then re-run affected checks. Preserve all unrelated local changes.

## Observed results

| Project | Fixed range | Supported modules / static edges | Wall time | Owner result |
| --- | --- | ---: | ---: | --- |
| memdsl | `7fc1d0b..a061bc4` | 52 / 215 | 1.28 s | Purpose found; workflow and change location failed |
| VideoFactory | `58d2149..d6594e3` | 87 / 158 | 1.64 s | Seven-step declared workflow; change mapped to video quality check |
| DigitalSelf | `4da99fc..a662719` | 1,140 / 2,058 | 5.16 s | Purpose found; workflow and change location failed |

The generated HTML sizes are 0.34, 0.36 and 0.96 MB respectively. Real headless
Chromium exercised both tabs, all four overview nodes and their details at 1280
and 390 px. There were no console errors or horizontal overflow. Screenshots are
stored next to each report as `browser-software.png`.

Target proof: memdsl remained clean at `a061bc4`; VideoFactory remained at
`d6594e3` with the same 39-line status SHA-256; DigitalSelf remained at `a662719`
with the same 82-line status SHA-256. All three before/after status hashes match.

## Product assessment

- Performance and report delivery pass this sample: even the 1,140-module project
  completed in 5.16 seconds, far below the earlier 40-minute experience.
- VideoFactory passes because its root README has an explicit workflow section
  that the conservative extractor can reconcile with code.
- memdsl's README clearly explains the product and capabilities, and its latest
  change is visibly a release/MCP Registry distribution change, but the report
  reduces the software to generic input/process/output and merely lists 21 files.
- DigitalSelf similarly provides a recognizable product purpose but no accepted
  deterministic workflow. The generic four-step arrows are labelled unverified,
  yet still fail the product's “understand the software” promise.
- All three fresh reports lack source-bound English body packs. English mode makes
  that limitation explicit; it does not satisfy automatic bilingual generation.

No target-specific fix was added. The new browser harness is repository-neutral.
See BUG-20260910-029 for the unresolved comprehension gap. Automatic bilingual
generation remains a separately known translation-authoring limitation.

Full repository test suite: `104 passed in 53.45s`; browser harness syntax and
diff checks pass. The `ds` completion CLI was unavailable, so no completion
receipt was submitted. No commit, tag, remote operation or release occurred.
