# Busch Apple Trade Tool — v4 spec (for EDIT chat)

v3 is live (multi-team trades, draft capital from Sleeper, $515 note). This is a small polish round to make the
site NEUTRAL while the league vote is still open, plus a responsive layout tweak. Standalone `index.html`.

## 1. NEUTRAL cap display (vote not finalized — don't show anyone "over")
The vote on the $515 cap isn't final, so the site must NOT display over-cap flags or red warnings right now.
- REMOVE the "over cap" indicator everywhere: no "$X over", no red coloring, no "/365" comparison, no room-remaining.
- Just show each team's **TOTAL VALUE** (sum of player salaries) as a neutral number. Plain, no judgment.
- Applies to: the salary table / team cards, the multi-team view, AND the trade tab projected totals
  (show each team's projected total value after the trade, but neutral — no over/under-cap flag, no red).
- Keep the CAP constant in the code (still 365) but DON'T surface it as a limit in the UI right now.
- Keep the $515 explainer NOTE (it explains the pending vote) — that's informational, fine to keep. Just no live
  over-cap flagging on teams.
- DESIGN INTENT: neutral, clean, non-inflammatory while the vote is open. When the vote passes, we re-enable the
  cap display at $515 (over-cap flag + room) — so implement the cap flag behind a simple on/off flag (e.g.
  `SHOW_CAP = false`) rather than deleting the logic, so it's a one-line re-enable at $515 later.

## 2. Responsive layout: side-by-side desktop, stacked mobile
- Multi-team view + trade-tab team panels: on DESKTOP show selected teams as SIDE-BY-SIDE columns (use the width);
  on MOBILE (~<=620px) STACK them vertically, single column, readable, no horizontal overflow at ~390px.
- Use CSS (grid/flex + media query) — same mobile-first pattern as the other tools.

## Guardrails
- Standalone repo only. Live Sleeper API, no secrets. Keep Refresh + players cache.
- Salary resolver dollar logic UNCHANGED (v3 verified 9/10 exact; the 1 was live $1 drift, not logic).
- CAP stays a config constant; `SHOW_CAP=false` now (neutral). When vote passes: CAP=515 + SHOW_CAP=true.
- Picks stay $0, never counted.
- Mobile-first: no horizontal overflow at ~390px; verify side-by-side collapses to stacked on phone.
- Commit author MUST be the GitHub-linked identity (ndjunce / noreply email) so Vercel deploys — the repo's git
  config is already set to that; keep it.
