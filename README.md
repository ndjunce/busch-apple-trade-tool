# Busch Apple — Salary & Trade Tool

Standalone salary and trade calculator for the Busch Apple Salary Dynasty league. Pulls live from the public Sleeper API on each load. Self-contained `index.html`, vanilla JS, no build step.

**Live:** (Vercel URL added after deploy)

## What it does
- **Salary Table** — every team, every rostered player's salary + source, team total, and room vs the cap.
- **Trade Builder** — pick players from two teams, see each side's outgoing/incoming salary and each team's projected total + room after the swap, with an over-cap flag. Honest calculator, no fair/unfair verdict.

## Salary model
Per player, resolved by priority (ported from the audited reference implementation, verified against the official auction sheet):
1. Auction price (all auction drafts merged oldest-first, newest wins)
2. FAAB winning bid (becomes the player's salary)
3. Rookie draft slot → rookie scale
4. $1 minimum (free-agent adds / blanks)

## Cap
Cap per team is a **config value** in `index.html` (`const CAP = 365`). Default 365 (current live rule). If the league passes the $515 combined-cap vote, flip that one line to `515`.

## Data
Public Sleeper API only (`api.sleeper.app`), no auth, no secrets. The ~14MB player dictionary is cached in localStorage with a 24h TTL. A Refresh button and optional 60s auto-refresh keep an open tab current.

## Local
Open `index.html` in a browser, or serve the folder. No build step.
