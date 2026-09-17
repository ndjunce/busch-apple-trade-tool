# Busch Apple Trade Tool — v2 Quality-of-Life spec (for EDIT chat)

v1 is live on Vercel + verified. This is the QoL polish round Nick requested. All changes are to the standalone
`index.html` in this repo (ndjunce/busch-apple-trade-tool). Keep it self-contained, vanilla JS, live Sleeper API,
CAP config constant (still 365 until the league vote passes — 8/10 yes as of 2026-09-16, awaiting 2 more).

## 1. Remove the salary SOURCE badge (auction / rookie / FAAB / FA$1)
- The source LABEL is wrong for some players (cosmetic mislabel; the $ AMOUNTS are audited-correct per Nick).
- Simply REMOVE the source badge from the player rows everywhere it shows (salary table + trade builder).
- Keep the salary $ itself. Do NOT change the resolver's dollar logic — only stop displaying the source tag.
  (If we later want the source shown correctly, that's a separate fix; for now just hide it.)

## 2. Team logos / player headshots by each player
- Add a small player image to each player row (same fallback pattern as the personal dashboard + picks site):
  ESPN headshot by espn_id → team logo → position-colored initial. Use Sleeper's `espn_id` from the players dict
  where present (partial coverage is fine, falls back to team logo).
- Also show each TEAM's owner avatar/logo on team headers if easy (optional; player images are the priority).

## 3. Sort + filter per team
- Per-team controls: SORT by salary (default high→low), by position, by name. FILTER by position (QB/RB/WR/TE/K/DEF...).
- Client-side only on the already-loaded roster data. Compose cleanly.

## 4. Splash / landing page + multi-team SELECT (1–4 teams side by side)
- On open, show a clean splash: title + a team picker (all 10 teams, owner name + avatar/logo).
- Let the user SELECT 1, 2, 3, or 4 teams and view those rosters side by side (responsive columns; stacks on mobile).
- This is the main "browse" view — easy for league members to eyeball their team or compare a few.
- Keep the "all 10 teams" full view available too (a "show all" option).

## 5. Same view functionality on the TRADE TOOL tab
- The trade builder should reuse the same team-select + logos + sort/filter niceties so picking players is easy.
- Two-team trade builder stays the core; just make selecting players pleasant (search/filter within a team).

## 6. Shorter URL (Nick action, not code)
- Current live = preview URL `busch-apple-trade-tool-dokpbm9sb-fun-fun-fun1.vercel.app` (has a random hash).
- Use the Vercel PRODUCTION domain instead (Settings→Domains): should be `busch-apple-trade-tool.vercel.app`,
  or rename the project (Settings→General) to something shorter e.g. `busch-apple` → `busch-apple.vercel.app`.
- No code change; update README with the final clean URL once chosen.

## Guardrails
- Standalone repo only — do NOT touch the personal fantasy-dashboard or fantasy_football_project CAN AM tools.
- Live public Sleeper API, no secrets. Cache players dict (24h) as before. Keep the Refresh button.
- Verify salary totals still match the audit after refactor (Ajay $426 … Seth $331 of $515; at CAP=365 three show "over" — correct).
- Mobile-first: everything readable + no horizontal overflow at ~390px (league will mostly use phones).
- CAP stays a single config constant; flip 365→515 only when the vote passes.
