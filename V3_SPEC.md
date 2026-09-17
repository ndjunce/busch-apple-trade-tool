# Busch Apple Trade Tool — v3 spec (for EDIT chat)

v2 is live + verified (splash, multi-team view, logos, sort/filter, badge removed). This adds multi-team trades,
future draft capital, and a $515 explainer note. Standalone `index.html`, live Sleeper API, CAP config constant.

## 1. MULTI-TEAM TRADES (3+ teams) on the Trade tab
- Let the user add MORE than two teams to a trade (e.g. 3- or 4-team deal).
- For each player put INTO the trade, a "goes to → [team]" selector picks the DESTINATION team (not just an A↔B swap).
- Recompute each involved team's projected total after all the moves (players leaving that team subtracted, players
  arriving added). Show each team's projected total + room + over-cap flag vs the CAP config.
- Keep the simple 2-team flow easy; multi-team is the expanded mode.
- Reuse v2 niceties (player images, per-team search/filter within each team's pick list).

## 2. FUTURE DRAFT CAPITAL (tradeable, $0 salary)
Sleeper only exposes TRADED picks (`/league/{id}/traded_picks`) — NOT the picks a team still holds by default.
Verified for Busch Apple: only 2 traded picks exist right now:
  - 2027 R1: originally ChayDyck -> now owned by rearmostzeus (Zach)
  - 2027 R2: originally JunceBoxes (Nick) -> now owned by Nyquilbandit (Henry)
So to show FULL draft capital per team, build it as: DEFAULT baseline picks (every team starts with their own
picks) MINUS traded-away + PLUS acquired, using the traded_picks endpoint to adjust.

**DEFAULT baseline (CONFIRMED by Nick):** each team starts with their own 1st, 2nd, 3rd round pick for
2027, 2028, 2029 = **9 future picks each** (3 years × 3 rounds) before trades. League trades 3 years out.
VERIFIED against Nick's real Sleeper picks: his list is 2027 1st, 2027 3rd, 2028 1/2/3, 2029 1/2/3 = 8 picks —
the missing 2027 2nd is exactly the one he traded to Henry (matches Sleeper traded_picks). So the model
"9 defaults − traded-away + acquired" reproduces Sleeper's display exactly. Build it that way.

- Render each team's future picks (e.g. "2027 1st", "2028 2nd") as tradeable ASSETS.
- Picks carry **$0 salary** — they do NOT affect the cap math (a pick only gets a rookie-scale salary when a
  player is drafted into it, and its slot isn't known until final standings). This is correct + honest.
- Picks can be added to a (multi-team) trade and assigned a destination team, same as players.
- Pull the 2 real trades from Sleeper `traded_picks` so ownership is accurate; apply on top of the default baseline.
- Do NOT try to show a pick's draft SLOT or dollar VALUE for future years — not knowable until season-end standings
  (non-playoff teams pick by inverse record; playoff teams fill NFL-style). Just show "YEAR ROUND" + owner.

## 3. $515 CAP EXPLAINER NOTE (simple)
- Add a short, simple note on the page (near the cap / on the Trade tab) explaining the pending rule:
  "Cap is currently $365 (auction budget). If the league vote passes, the in-season cap becomes $515 — that's the
   $365 auction budget + the $150 FAAB, treated as one combined salary cap. That extra room is what lets trades
   actually happen (you can take on a big contract without instantly breaking the cap). FAAB isn't traded on its
   own — it's just part of your $515. Next year the cap resets to the auction base + increase; FAAB salaries carry over."
- Keep it plain-English and short. When CAP flips 365->515, the note should reflect the active number.

## Guardrails
- Standalone repo only. Live public Sleeper API, no secrets. Cache players dict (24h). Keep Refresh.
- CAP stays a single config constant (365 now; flip to 515 when the vote passes — vote was 8/10, near unanimous).
- Re-verify the 10 team salary totals still match the audit after refactor (Ajay $426 ... Seth $331 of $515).
- Mobile-first: no horizontal overflow at ~390px; multi-team + picks must stay readable on a phone.
- Picks = $0 salary, never counted toward the cap.
