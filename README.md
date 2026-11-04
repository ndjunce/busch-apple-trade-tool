# Busch Apple — Salary & Trade Tool

A standalone salary-cap and trade calculator for a 10-team fantasy football **salary dynasty** league. It pulls
every roster and draft pick from the public Sleeper API on each load and **derives salaries from draft and transaction history** — no manual data entry, no
spreadsheet upkeep. Self-contained `index.html`, vanilla JS, no build step, deployed on Vercel.

Confirmed league pick forfeitures are the exception to API-only ownership: `FORFEITED_PICKS`
excludes Henry's original 2029 third (original roster 10), per the commissioner notice for
Weeks 5–6 OUT starters. Sleeper still lists it. The Teams count/list and Trade Builder omit it,
with a visible explanation; old shared links and refreshed selections cannot restore it.
Other teams' picks held by Henry remain available. This is a confirmed manual rule correction,
not automatic violation detection or a change to Sleeper. Future penalties require confirmation.

**Live:** https://busch-apple-trade-tool.vercel.app/

## What it does
- **Team / Salary view** — browse any team (or several side by side); every rostered player with their salary and
  NFL team, each team's total value, cap room, and over-cap flag. Player headshots with team-logo fallback.
- **Trade Builder** — build trades between **up to 10 teams** at once. Pick players (and future draft picks) from
  each team, choose which team each asset goes to, and instantly see every team's projected salary total and cap
  room after the deal, with an over-cap flag. An honest calculator — it shows the numbers, not a fair/unfair verdict.
- **Live data** — reflects roster moves as they happen (a waiver claim shows up on the next load). Refresh button
  plus optional auto-refresh.
- **Draft Picks tab** — 2027 provisional order and 2028/2029 current-standings illustrations, showing the
  original team and current holder for each first, second and third. Actual playoff finish and future seasons
  are unknown; exact ties remain ranges. No draft-capital valuations are published on this site.

## Separate Busch trade phone alerts

`.github/workflows/notify_trades.yml` runs `scripts/notify_trades.py` on standard public GitHub runners at
minutes 02,07,...57, around the clock, independent of the owner's PC. It uses **only** this repo's
`NTFY_TOPIC` secret and `BUSCH_TRADE_ALERTS_ENABLED=true` variable. Existing weekly/waiver/pregame notification
workflows and their switches live elsewhere and are not modified. No secret is embedded in the website.

On first installation, manually run **Busch trade alerts (ntfy)** with mode `initialize`. This silently
baselines historical completed trades and sends one setup confirmation. Later ticks send a separate alert
for each newly completed trade: salary cap at processing time, known forfeited picks, or **unable to verify**.
Private/pending proposals are not visible through the public API and are not treated as accepted. Busch's
current zero review delay makes completion the processing signal. All 18 history buckets are scanned, because
an offer accepted now may remain in its older proposal week. Later roster moves and salary resets are reversed
for the cap check; missing/inconsistent data never gets a green approval. Draft/contract/roster legality beyond
these checks is not certified, and the monitor never posts to or changes Sleeper.

Dedupe state is committed only on changes to `trade-alert-state.json` on branch `busch-trade-alert-state`.
Do not delete/reset this branch: missing state stops monitoring rather than silently dropping unseen trades.
Failed sends are retried; a crash between confirmed delivery and state persistence can duplicate an alert.
An unverifiable new trade sends one warning, then a correction when it can be verified. History outages send
one failure notice and one recovery notice. No new event means no phone alert and no state commit.

GitHub schedules are **best effort**: five minutes is a polling target, not a delivery guarantee; schedules
can be delayed or dropped. Public-repo schedules may be disabled after 60 days without activity. Check Actions
after a long offseason gap, after a failure, or at league rollover. Standard public runners avoid consuming
private-repo Actions minutes. The 2026 league/rules must be reviewed before enabling another season.

Run manual `dry-run` to inspect recent trades without sending or saving; `check` scans for new completed
trades. Disable only this monitor with `BUSCH_TRADE_ALERTS_ENABLED=false`. No other notification switch changes.

Tests: `python -m unittest discover -s tests -p test_trade_alerts.py`, `node tests/salary-regression.mjs`,
and `node tests/draft-order.mjs`.

## Salary model
Start with the newest available auction price, otherwise the rookie draft slot's salary scale, otherwise $1.
Replay completed acquisition events in timestamp order: a waiver claim resets salary to its winning bid,
a free-agent pickup resets it to $1, and a trade carries the existing salary. This implements the owner's
October 9, 2026 clarification; a prior owner's auction price does not survive a later free-agent pickup.
Missing transaction or pick history stops the refresh and disables trade cap results until a complete retry succeeds.
Refresh also removes selected trade assets no longer held by their source roster and updates retained salaries.

The combined cap is **$365 auction budget + $150 in-season FAAB = $515 per team**. Draft picks are tradeable but
carry $0 salary (their slot — and salary — is set by final standings, NFL-style, once the season ends).

The result checks salary cap arithmetic only. It does not check roster limits, lineup needs, contract expiry,
trade deadlines or fair value. The app has no contract-year records. Confirm any such rules separately.

## Tech
- Single self-contained `index.html`, vanilla JavaScript, no framework, no build step.
- Data: public Sleeper API (`api.sleeper.app`) only — no auth, no secrets. The player dictionary is cached in
  localStorage (24h TTL) to avoid re-downloading.
- The displayed update time is the successful roster/history fetch time. Player names, positions and NFL teams
  can come from the 24-hour dictionary cache; salaries are reconstructed, not an official Sleeper salary field.
- Responsive: side-by-side columns on desktop, single-column stack on mobile.
- Deployed as a static site on Vercel.

## Run locally
Open `index.html` in a browser (or serve the folder). No build step.
