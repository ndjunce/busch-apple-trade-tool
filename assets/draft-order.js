/* Provisional rookie-pick view. No forecasts, salary arithmetic or league writes. */
(function (host) {
  "use strict";

  const esc = value => String(value == null ? "" : value).replace(/[&<>"']/g,
    c => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[c]));
  const number = value => value !== null && value !== "" && Number.isFinite(Number(value)) ? Number(value) : null;
  const count = value => { const n = number(value); return n !== null && n >= 0 && Number.isInteger(n) ? n : null; };
  const slot = (round, rank) => `${round}.${String(rank).padStart(2, "0")}`;

  /**
   * standings(rawRosters, leagueSettings) -> rows, worst record first.
   * rankLow/rankHigh are a tied range, never an invented roster-ID tiebreak.
   * This is NOT official playoff seeding: divisions and actual playoff finish
   * are deliberately not inferred from this regular-season snapshot.
   */
  function standings(rosters, settings) {
    const rows = (Array.isArray(rosters) ? rosters : []).map(roster => {
      const s = roster.settings || {};
      const wins = count(s.wins), losses = count(s.losses), ties = count(s.ties);
      const whole = number(s.fpts), decimal = number(s.fpts_decimal);
      const valid = wins !== null && losses !== null && ties !== null && whole !== null && decimal !== null
        && whole >= 0 && decimal >= 0 && decimal < 100;
      return {
        roster_id:Number(roster.roster_id), wins, losses, ties,
        games:valid ? wins + losses + ties : null,
        pointsFor:valid ? Math.round(whole * 100 + decimal) / 100 : null,
        valid, rankLow:null, rankHigh:null, group:"Unknown"
      };
    });
    const cmp = (a, b) => {
      if (!a.valid || !b.valid) return Number(b.valid) - Number(a.valid);
      // Cross multiplication avoids floating-point distinctions in equal win percentages.
      const record = (2 * a.wins + a.ties) * (b.games || 1) - (2 * b.wins + b.ties) * (a.games || 1);
      return record || a.pointsFor - b.pointsFor;
    };
    rows.sort(cmp);
    const complete = rows.length > 0 && rows.every(r => r.valid)
      && new Set(rows.map(r => r.roster_id)).size === rows.length;
    const playoffs = count((settings || {}).playoff_teams);
    const nonplayoff = playoffs !== null && playoffs <= rows.length ? rows.length - playoffs : null;
    if (complete) {
      for (let i = 0; i < rows.length;) {
        let end = i + 1;
        while (end < rows.length && cmp(rows[i], rows[end]) === 0) end++;
        for (let j = i; j < end; j++) {
          rows[j].rankLow = i + 1;
          rows[j].rankHigh = end;
          rows[j].group = nonplayoff === null ? "Playoff count unknown"
            : end <= nonplayoff ? "Outside playoff places by record"
            : i >= nonplayoff ? "Playoff-place illustration; finish pending"
            : "Tied across illustrative playoff cutoff";
        }
        i = end;
      }
    }
    return rows;
  }

  /** render(teams, rawRosters, leagueSettings, forfeitedPickMap) -> escaped HTML. */
  function render(teams, rosters, settings, forfeited) {
    if (!Array.isArray(teams) || !teams.length) return "";
    const byId = new Map(teams.map(t => [Number(t.roster_id), t]));
    const raw = new Map((Array.isArray(rosters) ? rosters : []).map(r => [Number(r.roster_id), r]));
    const rows = standings(teams.map(t => raw.get(Number(t.roster_id)) || {roster_id:t.roster_id}), settings);
    const ownerName = id => {
      const t = byId.get(Number(id));
      return t ? t.owner || t.sn || `Roster ${id}` : `Roster ${id}`;
    };
    const holders = new Map();
    for (const t of teams) for (const p of (t.picks || [])) {
      const key = `${Number(p.year)}-${Number(p.round)}-${Number(p.origRid)}`;
      if (!holders.has(key)) holders.set(key, new Set());
      holders.get(key).add(Number(t.roster_id));
    }
    const pickCell = (year, round, row) => {
      const identity = `${year}-${round}-${row.roster_id}`;
      if (Object.prototype.hasOwnProperty.call(forfeited || {}, identity)) {
        return `<td><strong>Forfeited — ${esc(ownerName(row.roster_id))} original</strong></td>`;
      }
      const current = holders.get(identity);
      const holder = !current || !current.size ? "Owner unavailable"
        : current.size !== 1 ? "Conflicting ownership; verify"
        : ownerName([...current][0]);
      const place = row.rankLow === null ? "Order unavailable"
        : row.rankLow === row.rankHigh ? slot(round, row.rankLow)
        : `${slot(round, row.rankLow)}–${slot(round, row.rankHigh)} (tied)`;
      return `<td>${esc(place)}<br><span class="bs-dim">${esc(holder)}</span></td>`;
    };
    const yearTable = year => {
      const near = year === 2027;
      const intro = near
        ? "PROVISIONAL: current regular-season record, then lower points-for. Non-playoff originals are ordered this way; playoff originals will be ordered by actual playoff finish. Playoff-place slots below are standings-based placeholders, not confirmed draft positions."
        : "CURRENT STANDINGS ILLUSTRATION ONLY — not a forecast of this draft year. These slots reuse today's records to show each original pick and its current owner. Actual future records and playoff results will determine the order.";
      const body = rows.map(row => {
        const record = row.valid ? `${row.wins}–${row.losses}${row.ties ? `–${row.ties}` : ""}` : "Unavailable";
        const pf = row.pointsFor === null ? "Unavailable" : row.pointsFor.toFixed(2);
        const tie = row.rankLow !== null && row.rankLow !== row.rankHigh ? " · Exact record/PF tie; no further tiebreak assumed" : "";
        const group = row.group === "Outside playoff places by record" ? "Non-playoff projection"
          : row.group === "Playoff-place illustration; finish pending" ? "Playoff finish TBD" : row.group;
        return `<tr><th scope="row">${esc(ownerName(row.roster_id))}<br><span class="bs-dim">${esc(record)} · ${esc(pf)} PF</span><br><span class="bs-micro">${esc(group + tie)}</span></th>${[1,2,3].map(round => pickCell(year, round, row)).join("")}</tr>`;
      }).join("");
      return `<details class="bs-details"${near ? " open" : ""}><summary><span class="bs-h2">${year} rookie picks</span> · ${near ? "provisional order" : "current-standings illustration"}</summary><p class="tt-note">${intro}</p><div class="bs-table-wrap" tabindex="0" role="region" aria-label="${year} rookie pick ownership table; scroll horizontally if needed"><table class="bs-table"><caption>${year}: original teams and current pick holders — ${near ? "provisional" : "illustration only"}</caption><thead><tr><th scope="col">Original team / record</th><th scope="col">First</th><th scope="col">Second</th><th scope="col">Third</th></tr></thead><tbody>${body}</tbody></table></div></details>`;
    };
    return `<section class="bs-panel" aria-label="Rookie draft order and ownership"><h2 class="bs-h2">Rookie draft picks</h2><p class="tt-note">Pick positions follow the original team; traded picks show their current holder. No slots are locked. Record-based playoff places are illustrative, not official playoff seeding; divisions can affect qualification. Exact record/PF ties remain tied. Forfeited originals have no available holder.</p>${[2027,2028,2029].map(yearTable).join("")}</section>`;
  }

  host.BuschDraftOrder = Object.freeze({render, standings});
})(typeof window !== "undefined" ? window : globalThis);
