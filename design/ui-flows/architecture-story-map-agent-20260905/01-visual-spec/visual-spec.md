# Visual specification

## Target

Generated `review.html` → `整体架构` → `第 1 层 · 系统工作流`, desktop and narrow layouts.

## Problem observed

The current free-form SVG curves and their labels share the same plane as the cards. Because cards deliberately sit above the SVG, arrows and labels disappear under them; putting the SVG on top would instead obscure card copy. Raising z-index is therefore not an acceptable correction.

## Required picture

1. Three restrained responsibility bands: `外部输入`, `系统自动处理`, and `人工决定`.
2. A single, numbered, left-to-right main route in the automatic band: evidence spine → static extraction → constrained explanation and validation → reader report.
3. Two input cards enter the evidence spine through short vertical/horizontal orthogonal branches in a dedicated input gutter.
4. The human approval card sits in the human-decision band, after the report; the reusable-baseline state is its terminal result.
5. Each visible connector runs only through the empty gutters between stages, never through or behind a card. Connector wording is represented by numbered steps and a small relation key, not floating labels.
6. The existing profile-source boundary and the static-code implementation layer stay visible and unchanged in meaning.

## Responsive behavior

- Desktop: bands and connectors are visible; all connector routes are orthogonal and non-overlapping with cards.
- Narrow: cards stack in narrative order; no SVG connector is shown; an ordered text route preserves every configured relationship.

## Visual language

Reuse the existing cards, blue/green/amber palette, typography, and low-contrast grid. Do not add bitmap assets or workflow-engine notation. Numbers are stage markers, not runtime proof.
