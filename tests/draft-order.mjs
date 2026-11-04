import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const context = {window:{}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(new URL('../assets/draft-order.js', import.meta.url), 'utf8'), context);
const {render, standings} = context.window.BuschDraftOrder;
const teams = Array.from({length:10}, (_,i) => ({roster_id:i+1,owner:`Owner ${i+1}`,picks:[]}));
for (const t of teams) for (const year of [2027,2028,2029]) for (const round of [1,2,3]) {
  t.picks.push({year,round,origRid:t.roster_id,ykey:`${year}-${round}-${t.roster_id}`});
}
const rosters = teams.map((t,i) => ({roster_id:t.roster_id,settings:{wins:i,losses:9-i,ties:0,fpts:100+i,fpts_decimal:25}}));
const settings = {playoff_teams:6};
const forfeited = {'2029-3-10':{originalRoster:10}};
let html = render(teams, rosters, settings, forfeited);
assert.equal((html.match(/<details /g) || []).length,3);
assert.equal((html.match(/<th scope="row">/g) || []).length,30);
assert.equal((html.match(/<summary>/g) || []).length,3);
assert.equal((html.match(/class="bs-table-wrap" tabindex="0"/g) || []).length,3);
assert.match(html,/Forfeited — Owner 10 original/);
assert.equal((html.match(/Forfeited — Owner 10 original/g) || []).length,1);
assert.match(html,/2028 rookie picks/);
assert.match(html,/2029 rookie picks/);
assert.equal((html.match(/not a forecast of this draft year/g) || []).length,2);
assert.match(html,/playoff originals will be ordered by actual playoff finish/);
assert.match(html,/not official playoff seeding/);
assert.match(html,/No slots are locked/);
console.log('PASS three accessible 10-row year tables, clear provisional/future uncertainty and one exact forfeiture');

const transferred = teams[0].picks.find(p=>p.ykey==='2027-1-1');
teams[0].picks=teams[0].picks.filter(p=>p!==transferred);
teams[9].picks.push(transferred);
html=render(teams,rosters,settings,forfeited);
assert.match(html,/<th scope="row">Owner 1<br>[\s\S]*?<\/th><td>1\.01<br><span class="bs-dim">Owner 10<\/span><\/td>/);
assert.match(html,/Forfeited — Owner 10 original/);
console.log('PASS a traded first retains original-team slot and shows current owner');

const order=standings(rosters,settings);
assert.equal(order[0].roster_id,1);
assert.equal(order[3].group,'Outside playoff places by record');
assert.equal(order[4].group,'Playoff-place illustration; finish pending');
const examples=[
 {roster_id:1,settings:{wins:3,losses:5,ties:0,fpts:879,fpts_decimal:54}},
 {roster_id:2,settings:{wins:2,losses:6,ties:0,fpts:957,fpts_decimal:76}},
 {roster_id:3,settings:{wins:2,losses:6,ties:0,fpts:904,fpts_decimal:86}}
];
assert.deepEqual(Array.from(standings(examples,{playoff_teams:0}),r=>r.roster_id),[3,2,1]);
console.log('PASS worse record precedes lower points-for; equal records use points-for');

const tied=structuredClone(rosters);
tied[4].settings={...tied[3].settings};
const tieRows=standings(tied,settings).filter(r=>r.roster_id===4||r.roster_id===5);
assert.ok(tieRows.every(r=>r.rankLow===4&&r.rankHigh===5));
assert.ok(tieRows.every(r=>r.group==='Tied across illustrative playoff cutoff'));
html=render(teams,tied,settings,forfeited);
assert.match(html,/1\.04–1\.05 \(tied\)/);
assert.match(html,/no further tiebreak assumed/);
const tiedReversed=standings([...tied].reverse(),settings).filter(r=>r.roster_id===4||r.roster_id===5);
assert.ok(tiedReversed.every(r=>r.rankLow===4&&r.rankHigh===5));
console.log('PASS exact ties preserve shared slot ranges, including playoff cutoff; input order does not break ties');

const pct=[
 {roster_id:1,settings:{wins:2,losses:2,ties:0,fpts:120,fpts_decimal:0}},
 {roster_id:2,settings:{wins:3,losses:3,ties:0,fpts:100,fpts_decimal:0}},
 {roster_id:3,settings:{wins:1,losses:2,ties:1,fpts:80,fpts_decimal:0}}
];
assert.deepEqual(Array.from(standings(pct,{playoff_teams:0}),r=>r.roster_id),[3,2,1]);
const incomplete=structuredClone(rosters);
delete incomplete[0].settings.fpts;
assert.ok(standings(incomplete,settings).every(r=>r.rankLow===null));
assert.match(render(teams,incomplete,settings,forfeited),/Order unavailable/);
assert.match(render(teams,rosters,{},forfeited),/Playoff count unknown/);
console.log('PASS win percentage handles ties/unequal games and missing data never fabricates an order');

const hostile=structuredClone(teams);
hostile[0].owner='<img src=x onerror=alert(1)> & "Owner"';
html=render(hostile,rosters,settings,forfeited);
assert.doesNotMatch(html,/<img/);
assert.match(html,/&lt;img/);
assert.equal(render([],rosters,settings,forfeited),'');
console.log('PASS names are escaped; empty team list produces no misleading table');
