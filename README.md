# Busch Apple — Salary & Trade Tool

A standalone salary-cap and trade calculator for a 10-team fantasy football **salary dynasty** league. It pulls
every roster and draft pick from the public Sleeper API on each load and **derives salaries from draft and transaction history** — no manual data entry, no
spreadsheet upkeep. Self-contained `index.html`, vanilla JS, no build step, deployed on Vercel.

**Live:** https://busch-apple-trade-tool.vercel.app/

## What it does
- **Team / Salary view** — browse any team (or several side by side); every rostered player with their salary and
  NFL team, each team's total value, cap room, and over-cap flag. Player headshots with team-logo fallback.
- **Trade Builder** — build trades between **up to 10 teams** at once. Pick players (and future draft picks) from
  each team, choose which team each asset goes to, and instantly see every team's projected salary total and cap
  room after the deal, with an over-cap flag. An honest calculator — it shows the numbers, not a fair/unfair verdict.
- **Live data** — reflects roster moves as they happen (a waiver claim shows up on the next load). Refresh button
  plus optional auto-refresh.

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
