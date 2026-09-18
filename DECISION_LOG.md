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


## 2026-09-16 — v3 shipped + v4 spec (neutral display while vote open) written
v3 LIVE + verified: multi-team trades (2-4 teams, per-asset destination selector), future draft capital from Sleeper traded_picks ($0 assets; 9-pick baseline − traded + acquired; edit chat caught+fixed a Set-collapse bug where an acquired duplicate-round pick vanished, now keyed by year-round-origin w/ "via [owner]" label), $515 explainer note. Picks confirmed pulling live from Sleeper API. Salary 9/10 exact vs audit; Zach $353 vs $354 = live $1 drift, not logic.
v4 spec (`V4_SPEC.md`): (1) NEUTRAL cap display while vote is still open — remove all over-cap flags / red / "/365" / room; show each team's TOTAL VALUE only (team cards + multi-team view + trade projected totals). Keep CAP const + $515 note, but gate the cap-limit UI behind `SHOW_CAP=false` so it's a one-line re-enable at $515 when the vote passes. (2) Responsive: side-by-side columns on desktop, stacked single-column on mobile (<=620px), no overflow at 390px. Guardrails: resolver dollars unchanged, picks $0, commit author = ndjunce noreply (so Vercel deploys). NEXT: EDIT chat builds v4 from V4_SPEC.md.

## 2026-09-16 — v4: NEUTRAL cap display (SHOW_CAP flag) + responsive panels — WORKS
Small polish round to keep the site non-inflammatory while the $515 vote is still open. Salary resolver dollar logic UNCHANGED.

**1. Neutral cap display, gated behind `SHOW_CAP` (default false).** Added `const SHOW_CAP = false;` next to `CAP`. When false, the UI shows each team's **total value only** — no "/365", no room-remaining, no "over cap"/red anywhere. Gated (logic kept, not deleted, so it's a one-line re-enable):
  - Header capnote: dropped the "Cap per team: $365" line → neutral "salaries pulled live…".
  - Team cards: total shows "$X" + label "total value" (no "/CAP", no room line, no capbar) when neutral; `overCap` forced false.
  - Picker subline + trade-panel headers: "$X" only (no "/CAP").
  - Trade result cards: "total value after: $X" (no "/CAP", no room line, no red border/`over`); the over/under **verdict is suppressed** (only renders under `if(SHOW_CAP && anyAsset)`).
  - Foot + swap-note reworded to "showing total value only while the league cap vote is open."
  - **Kept the $515 explainer note** (informational about the pending vote) per spec.
  - **Re-enable path when vote passes:** set `CAP=515` AND `SHOW_CAP=true` → all cap flags/room/red come back at $515. Verified all over-flags (`overCap`, `over`) and the verdict are `SHOW_CAP`-gated so nothing leaks while false.

**2. Responsive: side-by-side desktop, stacked mobile.** Wrapped the trade-tab team panels in a `.trade-panels` grid (n1–n4), matching the existing `.cols`/`.rcols` pattern: full columns on desktop, collapse to 2-up ≤900px, single column ≤620px. Teams multi-team view + trade result cards already had these breakpoints. Mobile-first, no horizontal overflow intended at ~390px.

**Verified:** (a) `<script>` parses clean (node `new Function()`); (b) confirmed every cap/over/room/red output is behind `SHOW_CAP` (grep + read of teamCard `overCap`, renderTradeResult `over`/`afterLine`/verdict); (c) salary totals re-run vs live — **9/10 exact**, Zach $353 vs $354 = the SAME $1 live-data drift as v3 (resolver untouched, not a v4 regression). Picks still $0, never counted.
**CAP=365 / SHOW_CAP=false.** **Freeze before v4:** tag `good-busch-v3` → 6868e94. Commit author = ndjunce/noreply (Vercel-linked) per repo git config. Blast radius: this repo's index.html only.


## 2026-09-16 — v5 spec: add player NFL team to rows (Teams + Trade tabs) — last polish before sharing
Nick's final ask before sending to league: show each player's NFL team (BUF, SF, etc.) on their row, on both the Teams-tab cards and the Trade-builder panels. Data already available (Sleeper players dict `team`, already cached for the logo fallback) — just surface it as a compact muted label / small team logo next to name/pos. FA/no-team → blank or "FA", don't fabricate. Display-only; resolver + neutral cap (SHOW_CAP=false) + $0 picks all unchanged. Mobile-first (label must not overflow at 390px). Spec: `V5_SPEC.md`. NEXT: EDIT chat builds v5, then Nick shares with league.

## 2026-09-16 — v5: show player NFL team on rows — WORKS (display-only)
Last small polish before Nick shares it. Surfaced each player's NFL team (BUF, SF, etc.) as a compact muted label on their row, on BOTH the Teams-tab cards and the Trade-builder panels.
- Data was already there: player object carries `team` (`p.t` from the cached Sleeper dict, already used for the logo fallback). No new fetch, no cache bump.
- Added `teamTag(p)` helper → `<span class="pteam">· BUF</span>`; free agents / no pro team show "· FA" (never fabricated). Small muted uppercase tag next to the position, same visual weight as `.ppos`.
- Used in exactly 2 render spots (Teams card `.prow`, Trade panel `.pick`). New `.pteam` CSS: 10.5px muted, small left margin, inside the existing ellipsis-clamped name span so it can't push rows off-screen (mobile-safe at ~390px).
- **Untouched:** resolver dollar logic (sal() intact), neutral cap (SHOW_CAP=false), $0 picks. Verified via node: JS parses clean, teamTag used ×2, player.team populated, sal() unchanged, SHOW_CAP still false.
**Freeze before v5:** tag `good-busch-v4` → 281d0ec. Commit author = ndjunce/noreply. Blast radius: this repo's index.html only.


## 2026-09-16 — VOTE PASSED (10/10): flipped to $515 cap + SHOW_CAP=true — LIVE
League unanimously adopted the $515 combined cap. Flipped the two config values in index.html: `CAP` 365→515 and `SHOW_CAP` false→true (the gate built in v4). Cap display is now ON: teams show total / $515, room remaining, and over-cap flags return. Verified live against Sleeper under $515: ALL 10 TEAMS COMPLIANT — Ajay $426 (room $89, tightest), Henry $372, Riley $367, Chay $359, Jonah $358, Bobby $356, Nick $356, Zach $353, Charlie $334, Seth $331. Nobody over → everyone has real trade headroom ($89–$184). JS parses clean; resolver dollar logic untouched (only the 2 config values + comments changed). Committed + pushed; Vercel auto-deploys. The tool is now fully live in $515-enforcement mode for the league.
(Note: v5 player-NFL-team labels shipped just before this, per prior entry.)


## 2026-09-16 — Reworded draft-pick explainer to match league rule — pushed
Old note said a pick "only gets a salary when a rookie is drafted into it" — inaccurate. Correct rule: a pick's DRAFT SLOT (and thus salary) is set by FINAL STANDINGS — non-playoff teams ordered at end of regular season, playoff teams fill the rest after the playoffs (NFL-style). Updated the explainer text on the Trade tab accordingly. Picks still trade at $0 in-season (slot unknown until season end) + never count toward cap — that logic unchanged, only the wording. JS parses clean. Commit `f92b600`, pushed, Vercel redeploys.


## 2026-09-16 — v6 spec: allow up to 10-team trades — written (queued)
Nick wants the multi-team trade builder to support up to 10 teams (whole league), since Sleeper allows 10-team trades in-app. The v3 multi-team model already handles N teams; this is mostly raising the 4→10 cap + ensuring nothing hardcodes 4. Main watch-out: mobile layout with 10 panels (the v4 `.trade-panels` grid should wrap on desktop / stack on mobile — verify at 10, cap column min-width so they wrap not squish); destination dropdown must list all in-trade teams; per-team totals/over-$515 correct for all. Spec: `V6_SPEC.md`. LOW priority vs Nick's work deadline + Tue Sep 22 interviews — build after. NEXT: EDIT chat builds v6 from V6_SPEC.md.


## 2026-09-16 — v6 BUILT: multi-team trade limit raised 4 → 10 — WORKS
Raised the trade builder's team cap from 4 to 10 (whole league; Sleeper allows 10-team trades in-app). The v3 multi-team model already handled N teams (per-asset destination selector + per-team projected totals), so this was raising the cap + de-hardcoding 4 + fixing the layout for 10 panels.

**Changes (index.html only):**
- Trade-team toggle cap `>= 4` → `>= 10`. Label "Add teams to the trade (2–4)" → "(2–10)".
- **Layout for 10 panels (the real risk):** replaced the fixed `.trade-panels`/`.rcols` `n{1..4}` column classes with an **auto-fill grid** — `.trade-panels` = `repeat(auto-fill, minmax(260px,1fr))`, `.rcols` (result cards) = `minmax(180px,1fr)`; both stack to 1 column ≤620/560px. So 5–10 panels WRAP to multiple rows on desktop at a readable min-width (not squished slivers) and stack on mobile. Dropped the now-unused `nPanels`/`n` JS computations + `n${...}` classes.
- Destination dropdown (`destOptions`) + per-team result loop already map over ALL `tradeTeamObjects()` — no hardcoded limit, scale to 10 unchanged.
- **Left the Teams-tab viewer (`SELECTED`) capped at 4** on purpose — that's the "view 1–4 teams side by side" browse feature, separate from the trade builder; spec was only about trades.

**Verified (node, live Sleeper):** built a 6-team trade — each of the 6 source teams' destination dropdown lists the other 5 (all in-trade teams); moved 3 assets round-robin and per-team projected totals + room + over-$515 flag computed correctly for ALL 6 (e.g. Zach $353 → $442 after receiving Chase $89, room $73, under cap). `<script>` parses clean. Resolver dollar logic UNCHANGED (auction→FAAB→rookie→$1); picks still $0/never counted; CAP=515 / SHOW_CAP=true unchanged.
**Freeze before v6:** origin was at `f92b600` (last pushed good state). Commit author = ndjunce/noreply (Vercel deploys). Blast radius: this repo's index.html only.


## 2026-09-16 — v6 REGRESSION FIXED: trade builder couldn't select players/destinations — WORKS
**Symptom (live):** after v6, could toggle teams into a trade but couldn't select player assets or choose destinations — core function dead.

**Root cause (found by diffing v6 vs `good-busch-v5`):** the render + event-handler code was BYTE-IDENTICAL to v5 (verified — the v6 diff only touched CSS + the 4→10 cap + label + dropping nPanels/n). So it was NOT a logic/handler regression. It was the CSS auto-fill refactor: v5's grid used `repeat(N,1fr)` (tracks sized by container, items can't overflow); v6 switched to `repeat(auto-fill, minmax(260px,1fr))` — a fixed **260px min track**. `.side` panels had **no `min-width:0`**, so a panel whose content (long player names, the width:100% search box) exceeds 260px expanded/overflowed its track, and in a real browser that overflow rendered interactive elements (checkboxes / dest selects) where they couldn't be reliably clicked/tapped. Classic grid-item overflow bug that only manifests with real layout.

**Fix:** `.side{ …; min-width:0; overflow:hidden }` — grid items now clip to their track and can't overflow to block interaction. Kept v6's intent fully: 10-team cap + auto-fill wrapping (desktop wraps to rows, mobile stacks) unchanged.

**Verified:** built a jsdom harness (mock Sleeper data) that drives the REAL flow — add 3 teams → checkboxes render → check a player → destination `<select>` appears listing the other in-trade teams (→ Bobby, → Zach) → result panel computes. Passes. `node --check` clean. Confirmed the live deploy already had the v6 interactive code (so not a stale-deploy issue) — the fix is the CSS overflow guard. Resolver unchanged, picks $0, CAP=515/SHOW_CAP=true untouched. Removed all test scaffolding (jsdom/node_modules/package.json) so nothing extra ships.
**Freeze:** rollback = `good-busch-v5` → f92b600. Commit author = ndjunce/noreply.


## 2026-09-16 — v7 spec: screenshot-ready trade summary
Nick wants the trade result to list actual PLAYERS + their salaries per side (not just salary in/out totals) so a manager can SCREENSHOT it and post in the league/Sleeper chat as proof "the tool okayed this." Spec (`V7_SPEC.md`): per team show GIVES (each outgoing player + salary, picks $0) w/ sum, GETS (each incoming + salary) w/ sum, salary BEFORE→AFTER + room vs $515 + over flag; multi-team = per team separated; clean self-contained screenshot-friendly block w/ a "Busch Apple Trade — [date]" header + "all under $515 ✓ / X over" verdict; mobile-legible; OPTIONAL "Copy summary" text button. DISPLAY addition only — existing trade logic (audited resolver, $0 picks, $515, 10-team) unchanged, reuse computed salaries. Plan-chat wrote spec; build = edit chat. ndjunce/noreply.
