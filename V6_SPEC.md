# Busch Apple Trade Tool — v6 spec (for EDIT chat)

Small, well-scoped change. The tool is live + fully working ($515 cap, multi-team trades, draft capital, neutral→cap-on).
This raises the multi-team trade limit.

## Allow up to 10-team trades (currently capped at 4)
- The trade builder currently supports 2–4 teams. Raise the max to **10** (the whole league) — Sleeper supports
  10-team trades in-app, so league members should be able to model them here too.
- The multi-team model already handles N teams (per-asset "goes to → team" destination selector, per-team projected
  totals). This is mostly RAISING THE CAP from 4 → 10 and making sure nothing hardcodes 4.

## Guardrails / watch-outs
- **Mobile layout is the real risk:** 10 team panels side-by-side will overflow on a phone. The v4 `.trade-panels`
  grid already collapses (side-by-side desktop → 2-up → stacked mobile). Confirm it still works at 10 panels: on
  desktop they should wrap to multiple rows (not shrink to unreadable slivers); on mobile they stack. Cap column
  min-width so panels stay readable and wrap rather than squish.
- The per-asset destination dropdown must list ALL teams currently in the trade (up to 10), not just a fixed few.
- Per-team projected total / room / over-$515 flag must compute correctly for all involved teams (SHOW_CAP=true now).
- Picks stay $0, never counted. Resolver dollar logic UNCHANGED.
- Standalone repo only. Live Sleeper API. Commit author = ndjunce / noreply (so Vercel deploys).
- Re-verify: build a 5–6 team trade, confirm destinations + per-team totals are right and mobile stacks cleanly.
