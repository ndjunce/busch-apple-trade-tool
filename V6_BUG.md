# v6 REGRESSION — trade builder unusable (for EDIT chat)

## Symptom (Nick, live site)
After v6 (10-team trades), on the Trade builder tab:
- Can ADD/toggle teams into the trade (up to 10) — that part works.
- BUT can NOT select players (asset checkboxes don't work / don't respond), and can NOT choose the
  destination team for an asset. So no trade can actually be built. The tab is broken for its core purpose.

## Likely cause
v6 replaced the fixed `.trade-panels.n{1..4}` / `.rcols.n{N}` grid classes with auto-fill grids and REMOVED the
`nPanels` / `n` class computations. Suspect the refactor broke the per-panel render or the event wiring:
- The player-asset checkboxes and the "goes to → team" destination `<select>` may no longer render inside each
  panel, OR
- The change/click handlers (delegated listeners) that read asset selection + destination got disconnected when
  the wrapper markup changed (e.g. a container class/id the handler depends on was renamed/removed), OR
- `paintTrade()` builds the panels string but the interactive elements' handlers aren't re-bound after the
  auto-fill refactor.

## What to check
1. Confirm each team panel actually renders its player list with working checkboxes + each checked asset shows a
   destination dropdown listing all OTHER in-trade teams.
2. Confirm the delegated event handlers still match the current markup (container selector, data attributes,
   asset keys `p:<pid>` / `k:<year-round-orig>`).
3. Compare against the last known-good trade builder (freeze tag `good-busch-v5` → `f92b600`) to see exactly what
   the v6 diff changed in the render/handler path, not just the CSS.

## Expected after fix
- Add 3-6 teams → each panel shows its players (checkboxes) + picks.
- Check a player → a destination dropdown appears listing the other in-trade teams → pick one.
- Per-team projected totals + room + over-$515 update correctly (SHOW_CAP=true, CAP=515).
- Verify on desktop (panels wrap) AND mobile (stack). Commit as ndjunce/noreply so Vercel deploys. Log to DECISION_LOG.

## Guardrails
- Keep the 10-team cap + auto-fill wrapping (don't revert v6's intent — fix the interaction regression it caused).
- Resolver unchanged, picks $0, CAP=515/SHOW_CAP=true untouched.
