# Busch Apple — Salary & Trade Tool

A standalone salary-cap and trade calculator for a 10-team fantasy football **salary dynasty** league. It pulls
every roster, salary, and draft pick **live from the public Sleeper API on each load** — no manual data entry, no
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
Each player's salary is resolved by priority, verified player-by-player against the league's official auction sheet:
1. **Auction price** — all auction drafts merged oldest-first, newest price wins (carryover dynasty).
2. **FAAB winning bid** — the amount you won a player for becomes their salary.
3. **Rookie draft slot** — mapped to the league's rookie salary scale.
4. **$1 minimum** — free-agent pickups / undrafted.

The combined cap is **$365 auction budget + $150 in-season FAAB = $515 per team**. Draft picks are tradeable but
carry $0 salary (their slot — and salary — is set by final standings, NFL-style, once the season ends).

## Tech
- Single self-contained `index.html`, vanilla JavaScript, no framework, no build step.
- Data: public Sleeper API (`api.sleeper.app`) only — no auth, no secrets. The player dictionary is cached in
  localStorage (24h TTL) to avoid re-downloading.
- Responsive: side-by-side columns on desktop, single-column stack on mobile.
- Deployed as a static site on Vercel.

## Run locally
Open `index.html` in a browser (or serve the folder). No build step.
