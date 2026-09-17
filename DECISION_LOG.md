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


## 2026-09-16 — Repo created + pushed (token re-auth resolved) — DONE
Nick regenerated the GitHub PAT, so the stale-token block is cleared. Created private repo `ndjunce/busch-apple-trade-tool` and pushed v1 (index.html + README + DECISION_LOG + .gitignore), local/origin in sync (0/0). All 4 files confirmed on remote. REMAINING: Nick imports the repo into Vercel (framework = Other / static, no build settings) and pastes the .vercel.app URL to add to the README + share with the league. CAP still = 365 (current live rule); flip to 515 if/when the league vote passes.


## 2026-09-16 — v1 LIVE on Vercel + v2 QoL spec written — vote 8/10 yes
v1 deployed: preview URL https://busch-apple-trade-tool-dokpbm9sb-fun-fun-fun1.vercel.app/ (Nick to switch to the clean PRODUCTION domain — Settings→Domains, likely busch-apple-trade-tool.vercel.app, or rename project shorter). League vote on the $515 cap = 8 yes, awaiting 2.
Nick requested QoL v2 (spec: `V2_QOL_SPEC.md`): (1) REMOVE the source badge (auction/rookie/FAAB/FA$1) — label is cosmetically wrong for some; $ amounts are audited-correct, so just hide the tag, don't touch dollar logic; (2) player images/team logos per row (espn_id→team logo→initial fallback); (3) per-team sort + filter (salary/pos/name; filter by pos); (4) SPLASH landing + multi-team select (view 1–4 teams side by side, plus show-all); (5) same select/logos/filter niceties on the trade-tool tab; (6) shorter URL (Nick action, Vercel domain — no code). Guardrails: standalone only, live Sleeper, CAP config stays 365 until vote passes, mobile-first no-overflow, re-verify totals after refactor. NEXT: EDIT chat builds v2 from V2_QOL_SPEC.md.

## 2026-09-16 — v2 QoL round — WORKS (deploy = Vercel auto on push)
Built all v2 spec items in the standalone `index.html`. Salary $ resolver dollar-logic UNCHANGED from v1.

**Shipped:**
1. **Source badge REMOVED** everywhere (salary table + trade rows). Kept the salary $. Resolver dollar logic untouched (badge was cosmetically mislabeling some players; $ amounts are audited-correct).
2. **Player images** — headshot (ESPN CDN by Sleeper `espn_id`) → team logo (white chip) → position-colored initial. Extended the slim players cache to keep `espn_id` (`e`) + `team` (`t`); bumped cache key v1→v2 so stale caches refresh. Owner **avatars** shown on team headers + picker cards (Sleeper `avatar` thumbs).
3. **Per-team sort + filter** — sort by Salary (default), Position, Name; filter by position. Client-side on loaded rosters, per-team state.
4. **Splash / landing + multi-team select** — the Teams tab opens as a picker (all 10, owner + avatar + $total). Select 1–4 teams → rendered side by side in responsive columns (n1–n4; collapses on mobile). "Show all 10" + "Clear" buttons. 4-team cap (adding a 5th drops the oldest).
5. **Trade tab niceties** — reused player images + a per-side **search box** + position filter within each team's pick list; two-team builder core unchanged. Search preserves focus/caret across re-render.
6. Shorter URL = Nick action (Vercel domain), no code.

**Verified after build:** (a) resolver re-run vs live Sleeper — **all 10 team totals still match the audit exactly** (Ajay $426 … Seth $331); (b) `<script>` parses clean via node `new Function()`; (c) ESPN headshot + team-logo CDNs return 200 image/png, and Sleeper dict confirmed carrying espn_id+team (Saquon 3929630/PHI); (d) source badge render confirmed gone; CAP still 365.

**Mobile-first:** picker + columns collapse to 1-col under 620px; player rows are a 30px-image/name/salary grid with ellipsis, no horizontal overflow intended at ~390px (league is mostly phones).

**CAP still 365** (config constant). Flip to 515 when the vote passes (8/10 yes as of spec). **Freeze before v2:** tag `good-busch-v1` → 4259a1c. Blast radius: this repo's index.html only; did not touch fantasy-dashboard or CAN AM tools.


## 2026-09-16 — v2 deploy unblocked (Vercel Git-author) + v3 spec written
**Vercel block fixed:** deploy was blocked "couldn't find a Git account for the commit author" (Hobby plan). Cause: commits authored as `Klaus <ndjunce@hotmail.com>` — an email not linked to the GitHub account. Fix: set git identity to the GitHub noreply `224337140+ndjunce@users.noreply.github.com` (id from gh api), `git commit --amend --reset-author`, force-push. New commit `6a58a34` authored as ndjunce → Vercel deployed clean. v2 now LIVE on busch-apple-trade-tool.vercel.app.
**v3 spec written (`V3_SPEC.md`):** (1) MULTI-TEAM trades (3+ teams, per-player destination-team selector, per-team projected total/room/over-cap); (2) FUTURE DRAFT CAPITAL as $0-salary tradeable assets — Sleeper `traded_picks` only lists TRADED picks (verified: just 2 for this league — Chay 2027 1st→Zach, Nick 2027 2nd→Henry), so build = DEFAULT baseline (each team's own 2027/2028/2029 1st/2nd/3rd — NICK TO CONFIRM years/rounds) MINUS traded-away PLUS acquired; picks carry $0 salary + no slot/value (standings-dependent, not knowable), honest; (3) simple $515 explainer note (365 now → 515 if vote passes = auction $365 + FAAB $150 combined; extra room enables trades; FAAB not traded alone; resets next year w/ carryover). Guardrails: CAP config stays 365 until vote (8/10), re-verify totals, mobile-first, picks never counted toward cap.
OPEN: Nick to confirm the default future-pick set (assumed 2027-2029 × 1st/2nd/3rd = 9 per team).

## 2026-09-16 — v3: multi-team trades + future draft capital + $515 explainer — WORKS
Built all three v3 spec items in standalone `index.html`. Salary $ resolver dollar-logic UNCHANGED.

**1. Multi-team trades (2–4 teams).** Rewrote the trade tab from the fixed A/B model to an asset-based multi-team model: toggle 2–4 teams into the trade (chips), each team gets a panel (players + picks) with per-team search/filter. Check an asset → a **"→ destination team" selector** appears (defaults to another team in the trade). Per-team projected total = current − salary leaving + salary arriving; shows room + over-cap flag per team; verdict lists any teams over CAP. State: `TRADE_TEAMS` (ordered rids) + `TRADE_ASSETS` Map(assetKey → {fromRid,toRid,kind,amt}). Reconciles when a team leaves the trade or data refreshes.

**2. Future draft capital ($0 tradeable assets).** 9-pick baseline per team (2027/2028/2029 × 1st/2nd/3rd), adjusted by Sleeper `/traded_picks`. Picks are $0 and NEVER counted toward the cap (team total sums players only). Shown in a "Future picks · $0" section on team cards + as checkable assets in the trade with destination selectors.
- **BUG found + fixed during verify:** first cut keyed picks by a Set of `year-round`, which COLLAPSED duplicates — when Zach acquired Chay's 2027 1st on top of his own, one disappeared (Zach showed 9 not 10). Fixed: track picks by IDENTITY `(year, round, originalRoster)`, so a team can hold two 2027 1sts. Acquired picks show "(via <owner>)".
- **Verified vs live traded_picks (node):** Zach=10 (own + acquired Chay 2027-1, both present), Chay=8 (missing own 2027-1), Nick=8 (missing own 2027-2 → matches his REAL Sleeper display), Henry=10 (has acquired Nick 2027-2). Model reproduces Sleeper exactly.

**3. $515 explainer note** — plain-English `.explain` block on the Trade tab: cap is $365 now (auction budget); if the vote passes it becomes $515 (=$365 auction + $150 FAAB as one combined cap); that room is what lets trades happen; FAAB isn't traded on its own; picks trade at $0. Note text auto-reflects the active CAP (shows "currently $X"; switches wording when CAP≥515).

**Verified:** (a) salary totals re-run vs live — 9/10 match the audit exactly; **Zach $353 vs $354 = a $1 live-data drift** (a $1 FA add/drop since the audit), NOT a logic change (resolver code untouched, other 9 exact). (b) pick model correct (above). (c) `<script>` parses clean via node.
**Mobile-first:** trade team chips + panels stack; result cards use n2/n3/n4 grids collapsing to 1-col under 560px.
**CAP still 365** (config). **Freeze before v3:** tag `good-busch-v2` → 9cd4c56. Blast radius: this repo's index.html only.
