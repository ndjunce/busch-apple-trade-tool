# Decision Log — Busch Apple Salary & Trade Tool

Append-only. Each entry: date · what was tried · outcome (WORKS / REJECTED / OPEN) · why.
Canonical log for this standalone tool. Full build spec: see `fantasy-dashboard/_scratch/BUSCH_APPLE_TRADE_TOOL_SPEC.md`.

---

## 2026-08-14 — v1 built: salary table + trade builder — WORKS (deploy pending)
Standalone site per spec (NOT bolted onto the personal dashboard or CAN AM tools). Self-contained `index.html`, vanilla JS, public Sleeper API only, no build step, no secrets.

**Salary resolver ported from the proven `audit_salaries.mjs`** — priority: auction price (all auction drafts merged oldest-first, newest wins) → FAAB winning bid (`transactions.settings.waiver_bid` on complete adds, weeks 1-18) → rookie draft slot → rookie scale → $1 free-agent floor. Rookie scale table + owner name map copied verbatim from the reference.

**VERIFIED before shipping:** ran the ported resolver against live Sleeper and compared to the spec's audited team totals. **All 10 teams match exactly** (Ajay $426, Henry $372, Riley $368, Chay $359, Jonah $358, Bobby $356, Nick $356, Zach $354, Charlie $334, Seth $331) and source counts match (242 auction + 9 FAAB + 30 rookie). Port is faithful.

**Cap = CONFIG value:** `const CAP = 365` at the top of the script (default = current live rule). One-line flip to 515 if the combined-cap vote passes. Not hardcoded anywhere else — cap label, table room, bars, and trade math all read the constant.

**v1 scope shipped:**
- Salary Table tab: all 10 teams (sorted by total desc), collapsible rosters, per-player salary + source badge (auction/FAAB/rookie/FA $1), team total /CAP, room (green) or over (red), cap progress bar.
- Trade Builder tab: pick Team A + Team B, checkbox their rosters, live projected totals (remove outgoing + add incoming), room after, over-cap flag per team, plain ok/over verdict. No fairness judgment. Salary travels with the player regardless of origin. Guards against same-team-both-sides.
- Refresh button + optional 60s auto-refresh; `/players/nfl` cached in localStorage 24h TTL. Trade selections reconciled against fresh rosters on reload.

**Honest display:** totals + room shown as-is, never clamped/hidden. Under the $365 default some teams show "over" (red) — correct per the current rule; flips to compliant if CAP→515.

**Blast radius:** brand-new folder/repo. Does NOT touch fantasy-dashboard or fantasy_football_project.

**NEXT:** create repo, push, deploy to Vercel, share URL. v2 later = draft-pick trading ($0 salary, slot by final standings).

## 2026-08-14 — v1 committed locally; repo create/push/deploy BLOCKED on gh auth — OPEN (user action)
Local git repo initialized + committed (`f565c7e`, 4 files). Attempted `gh repo create ndjunce/busch-apple-trade-tool --public --push` → **HTTP 401 Bad credentials**. `gh auth status`: "The token in keyring is invalid." Token went stale mid-session (it worked for the portfolio push earlier today). Cannot re-auth headlessly — needs the user's interactive `gh auth login`.
- **User action to unblock:** (1) `gh auth login -h github.com` (or set a fresh token). (2) re-run `gh repo create ndjunce/busch-apple-trade-tool --public --source=. --remote=origin --push` from the tool folder. (3) import the repo to Vercel (framework = Other / static, no build step) → get the .vercel.app URL. Then add the URL to README + this log.
- Nothing lost — v1 is fully built + committed + resolver-verified locally.
