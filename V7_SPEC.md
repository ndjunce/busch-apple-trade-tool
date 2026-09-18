# Busch Apple Trade Tool — v7 spec (for EDIT chat)

Live + working ($515 cap, 10-team trades, draft picks). This adds a SCREENSHOT-READY trade summary. Repo:
ndjunce/busch-apple-trade-tool. Mobile-first.

## Add a detailed, screenshot-ready trade SUMMARY (not just salary in/out totals)
GOAL: after building a trade, show a clear breakdown a manager can SCREENSHOT and post in the league/Sleeper chat as
proof "the tool okayed this." Right now the result only shows each team's salary in/out + projected total. Add the
actual PLAYERS + their salaries per side.

### What the summary should show (per team in the trade):
- Team name (+ owner avatar/logo if available).
- **GIVES:** list each outgoing asset with its salary — e.g. "C.J. Stroud $33, KC Concepcion $8" (and any draft
  picks at $0, e.g. "2027 1st ($0)"). Show the sum.
- **GETS:** list each incoming asset with its salary the same way. Show the sum.
- Team's salary total BEFORE → AFTER, with room vs $515 and the over-cap flag if applicable.
- For multi-team (3+), do this per team, clearly separated, with each asset's destination implied by which team's
  GETS it appears under.

### Screenshot-friendliness:
- A clean, self-contained summary block (readable if cropped/screenshotted) — team names, player names + salaries,
  before→after totals, and a clear "all teams under $515 ✓" or "X over" verdict line.
- A small header like "Busch Apple Trade — [date]" so a screenshot has context.
- Keep it legible on mobile (most screenshots come from phones). No horizontal cutoff.
- OPTIONAL nice-to-have: a "Copy summary" button that copies a text version (team / gives / gets / totals) to the
  clipboard for pasting into chat — but the visual summary is the priority (screenshot is the main ask).

## Guardrails
- Keep all existing trade logic (salaries via audited resolver, picks $0, $515 cap, 10-team) UNCHANGED — this is a
  DISPLAY addition to the result panel only.
- Reuse the player salaries already computed for the trade; don't refetch.
- Mobile-first, no overflow ~390px. Commit as ndjunce/noreply so Vercel deploys.
