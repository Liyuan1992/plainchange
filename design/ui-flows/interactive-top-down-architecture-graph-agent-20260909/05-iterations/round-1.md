# Round 1

- Focus: structure and layout
- Review items this round is allowed to fix: replace the mistaken vertical list with an actual top-down, clickable node-and-edge graph while preserving current facts and drill-down.
- Changes made: topology ranks became graph rows; same-rank branches became columns; source-bottom to target-top orthogonal arrows were restored; one selected node now owns the expansion state; second click collapses it.
- Verification result: FastAPI 9 nodes/9 arrows/5 rows and Change Passport 8 nodes/8 arrows/7 rows; both report zero connector-card intersections and no horizontal canvas overflow. FastAPI node interaction opens 7 subdomains and collapses cleanly. At 390 px the clickable one-column fallback retains all relationship prose without overflow. Browser console issues: 0. Full tests: 50 passed.
- Remaining deviations: the complete relationship list intentionally repeats the visible topology for accessibility and narrow fallback. Independent beginner retelling remains pending.
