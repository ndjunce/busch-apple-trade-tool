# Busch Apple Trade Tool — v5 spec (for EDIT chat) — SMALL add

v4 is live + neutral. This is the last small polish before Nick shares it. Standalone `index.html`.

## Add each player's NFL TEAM to their row (Teams tab + Trade builder tab)
- Show each player's pro/NFL team (e.g. Josh Allen → BUF, Christian McCaffrey → SF) on their row,
  on BOTH the Teams-tab team cards AND the Trade-builder team panels.
- The data is ALREADY available: Sleeper's players dict has each player's `team` (already cached — it's used
  for the team-logo image fallback). Just surface it as a small text label (and/or the small team logo) next to
  the player's name/position.
- Keep it compact + mobile-friendly (small muted abbreviation like the position tag). Players with no team
  (free agents / no pro team) show nothing or "FA" — don't fabricate.

## Guardrails
- Standalone repo only. Resolver dollar logic UNCHANGED. Picks stay $0.
- Neutral cap display stays (SHOW_CAP=false) — this change is display-only, doesn't touch cap logic.
- Mobile-first, no horizontal overflow at ~390px (the new team label must not push rows off-screen).
- Commit author = ndjunce / noreply (so Vercel deploys).
