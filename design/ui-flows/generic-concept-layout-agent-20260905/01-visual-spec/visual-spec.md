# Visual specification

## Intended outcome

The first architecture layer is a map of a target profile's configured system story, not a hand-positioned Change Passport chart. A reader sees directed stages in layers, parallel work side-by-side, joins converging into later stages, and human decisions as visually distinct nodes.

## Layout rules

1. Directed graph ranks define columns; profile grid coordinates break ties only.
2. Nodes in one rank stack vertically; each card retains its existing visual type and implementation drill-down.
3. Orthogonal connectors use the empty grid channels. Cards are obstacles, not link backgrounds.
4. Relation text remains below the map and is the complete, accessible record.
5. If the graph contains a directed cycle or no clear route, show a labelled `关系较复杂，已切换为结构化阅读` state and omit decorative connectors; never pretend the visual is complete.

## Responsive behavior

Desktop shows the layered map only when it is safely routable. Narrow screens always use ordered cards and the complete relation text.
