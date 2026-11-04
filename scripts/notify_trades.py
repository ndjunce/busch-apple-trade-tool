"""Busch-only completed-trade monitor. Python stdlib; no Sleeper writes.

Rules come from this site's index.html. Durable dedupe lives on a separate Git
branch, never in an evictable Actions cache. No existing notification code used.
"""
import argparse
import base64
import concurrent.futures
import copy
import datetime as dt
import hashlib
import json
import math
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
API = 'https://api.sleeper.app/v1'
LEAGUE = '1372256037666574336'
STATE_BRANCH = 'busch-trade-alert-state'
STATE_FILE = 'trade-alert-state.json'
LINK = f'https://sleeper.com/leagues/{LEAGUE}/trades'


class CheckError(Exception):
    pass


def request_json(url, data=None, token=None, method=None):
    headers = {'Accept': 'application/json', 'User-Agent': 'BuschTradeMonitor/1.0'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
        headers['X-GitHub-Api-Version'] = '2022-11-28'
    if data is not None:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, headers=headers, data=None if data is None else json.dumps(data).encode(), method=method)
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise CheckError(f'HTTP {error.code}') from None
    except Exception as error:
        # Never include URL, headers, payload or exception text: topic is secret.
        raise CheckError(f'Request failed ({type(error).__name__})') from None


def checked_list(value, label):
    if not isinstance(value, list) or any(not isinstance(x, dict) for x in value):
        raise CheckError(f'Incomplete {label}')
    return value


def integer(value, label, minimum=0):
    if isinstance(value, bool):
        raise CheckError(f'Invalid {label}')
    try:
        number = float(value)
    except (ValueError, TypeError):
        raise CheckError(f'Invalid {label}') from None
    if not math.isfinite(number) or number != int(number) or number < minimum:
        raise CheckError(f'Invalid {label}')
    return int(number)


def rules(html):
    def body(name):
        match = re.search(r'const\s+' + name + r'\s*=\s*\{(.*?)\n\};', html, re.S)
        if not match:
            raise CheckError(f'Missing website rule: {name}')
        return match.group(1)
    cap = re.search(r'const\s+CAP\s*=\s*(\d+)', html)
    league = re.search(r'const\s+LEAGUE_ID\s*=\s*["\'](\d+)', html)
    if not cap or not league or league.group(1) != LEAGUE:
        raise CheckError('Website league/cap mismatch')
    scale = dict((key, int(value)) for key, value in re.findall(r'"(\d\.\d\d)"\s*:\s*(\d+)', body('ROOKIE_SCALE')))
    if len(scale) != 30:
        raise CheckError('Incomplete rookie salary scale')
    try:
        forfeited = json.loads('{' + body('FORFEITED_PICKS') + '}')
    except ValueError:
        raise CheckError('Invalid forfeiture ledger') from None
    owner = dict(re.findall(r'["\']?([\w.\-]+)["\']?\s*:\s*["\']([^"\']*)["\']', body('OWNER')))
    return {'cap': int(cap.group(1)), 'scale': scale, 'forfeited': forfeited, 'owners': owner}


def timestamp(tx):
    # created is proposal time, not acceptance/processing time.
    return integer(tx.get('status_updated'), 'processing timestamp', 1)


def histories(get=request_json):
    def fetch(week):
        return checked_list(get(f'{API}/league/{LEAGUE}/transactions/{week}'), f'week {week} history')
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        buckets = list(pool.map(fetch, range(1, 19)))
    unique = {}
    for bucket in buckets:
        for tx in bucket:
            key = str(tx.get('transaction_id') or '')
            if not key:
                raise CheckError('Transaction missing ID')
            if key in unique and unique[key] != tx:
                raise CheckError('History changed during fetch; retry required')
            unique[key] = tx
    return list(unique.values())


def completed_trades(transactions):
    def order(tx):
        try:
            return timestamp(tx)
        except CheckError:
            return 0  # Still discover it; audit reports UNABLE TO VERIFY.
    return sorted((tx for tx in transactions if tx.get('type') == 'trade' and tx.get('status') == 'complete'), key=lambda tx: (order(tx), str(tx['transaction_id'])))


def signature(tx):
    # Exclude private proposals; accepted means public processed status=complete.
    fields = {k: tx.get(k) for k in ('status', 'status_updated', 'adds', 'drops', 'draft_picks', 'roster_ids')}
    return hashlib.sha256(json.dumps(fields, sort_keys=True).encode()).hexdigest()


def roster_signature(rosters):
    return sorted((integer(r['roster_id'], 'roster ID', 1), tuple(sorted(map(str, r.get('players') or [])))) for r in rosters)


def snapshot(get=request_json):
    before = checked_list(get(f'{API}/league/{LEAGUE}/rosters'), 'rosters')
    txs = histories(get)
    drafts = checked_list(get(f'{API}/league/{LEAGUE}/drafts'), 'drafts')
    picks = {d['draft_id']: checked_list(get(f"{API}/draft/{d['draft_id']}/picks"), 'draft picks') for d in drafts}
    users = checked_list(get(f'{API}/league/{LEAGUE}/users'), 'users')
    players = get(f'{API}/players/nfl')
    league = get(f'{API}/league/{LEAGUE}')
    if str(league.get('season')) != '2026' or str(league.get('league_id')) != LEAGUE:
        raise CheckError('League rollover requires rule review')
    if not isinstance(players, dict):
        raise CheckError('Incomplete player metadata')
    after = checked_list(get(f'{API}/league/{LEAGUE}/rosters'), 'rosters')
    if roster_signature(before) != roster_signature(after):
        raise CheckError('Rosters changed during fetch; retry required')
    # Refetch history after the second roster read. A new transaction can leave a
    # superficially unchanged roster (e.g. two moves cancelling each other).
    final_txs = histories(get)
    digest = lambda rows: sorted((str(t['transaction_id']), signature(t)) for t in rows if t.get('status') == 'complete')
    if digest(txs) != digest(final_txs):
        raise CheckError('Transactions changed during fetch; retry required')
    return {'rosters': after, 'transactions': txs, 'drafts': drafts, 'draft_picks': picks, 'users': users, 'players': players}


def holdings_at(snapshot_data, target):
    holdings = {integer(r['roster_id'], 'roster ID', 1): set(map(str, r.get('players') or [])) for r in snapshot_data['rosters']}
    def owners():
        result = {}
        for rid, players in holdings.items():
            for pid in players:
                if pid in result:
                    raise CheckError('Player appears on multiple rosters')
                result[pid] = rid
        return result
    owners()
    cutoff = timestamp(target)
    moves = [tx for tx in snapshot_data['transactions'] if tx.get('status') == 'complete' and (tx.get('adds') or tx.get('drops'))]
    participants = set(target.get('roster_ids') or []) | set((target.get('adds') or {}).values()) | set((target.get('drops') or {}).values())
    for tx in moves:
        affected = set((tx.get('adds') or {}).values()) | set((tx.get('drops') or {}).values())
        if str(tx.get('transaction_id')) != str(target['transaction_id']) and timestamp(tx) == cutoff and participants & affected:
            raise CheckError('Same-time roster moves prevent a processing-time cap check')
    # Equal-time moves involving the same player cannot be safely ordered.
    seen = set()
    for tx in moves:
        for pid in set(tx.get('adds') or {}) | set(tx.get('drops') or {}):
            key = (timestamp(tx), str(pid))
            if key in seen:
                raise CheckError('Ambiguous transaction ordering')
            seen.add(key)
    for tx in sorted((t for t in moves if timestamp(t) > cutoff), key=timestamp, reverse=True):
        for pid, rid in (tx.get('adds') or {}).items():
            rid = integer(rid, 'add roster', 1)
            if rid not in holdings or str(pid) not in holdings[rid]:
                raise CheckError('Cannot reconstruct post-trade rosters')
            holdings[rid].remove(str(pid))
        for pid, rid in (tx.get('drops') or {}).items():
            rid = integer(rid, 'drop roster', 1)
            if rid not in holdings or str(pid) in owners():
                raise CheckError('Cannot reconstruct post-trade rosters')
            holdings[rid].add(str(pid))
    for pid, rid in (target.get('adds') or {}).items():
        if str(pid) not in holdings.get(integer(rid, 'trade destination', 1), set()):
            raise CheckError('Trade assets disagree with reconstructed rosters')
    return holdings


def prices_at(snapshot_data, target, rule):
    cutoff = timestamp(target)
    prices, rookie = {}, {}
    drafts = snapshot_data['drafts']
    if not any(d.get('type') == 'auction' for d in drafts):
        raise CheckError('Auction salary source missing')
    for draft in sorted(drafts, key=lambda d: d.get('start_time') or 0):
        start = integer(draft.get('start_time'), 'draft start', 1)
        if start > cutoff:
            continue
        for pick in snapshot_data['draft_picks'][draft['draft_id']]:
            pid = str(pick.get('player_id') or '')
            if not pid:
                raise CheckError('Draft player missing')
            if draft.get('type') == 'auction':
                value = (pick.get('metadata') or {}).get('amount')
                if value not in (None, ''):
                    prices[pid] = integer(value, 'auction amount')
            else:
                slot = f"{integer(pick.get('round'), 'round', 1)}.{integer(pick.get('draft_slot'), 'slot', 1):02d}"
                if slot not in rule['scale']:
                    raise CheckError('Rookie pick outside validated scale')
                rookie[pid] = rule['scale'][slot]
    result = {**rookie, **prices}
    for tx in sorted((t for t in snapshot_data['transactions'] if t.get('status') == 'complete' and t.get('adds') and timestamp(t) <= cutoff), key=timestamp):
        for pid in tx['adds']:
            if tx.get('type') == 'free_agent':
                result[str(pid)] = 1
            elif tx.get('type') == 'waiver':
                result[str(pid)] = integer((tx.get('settings') or {}).get('waiver_bid'), 'waiver bid')
            elif tx.get('type') != 'trade':
                raise CheckError('Unknown acquisition type')
    return result


def audit_trade(snapshot_data, tx, rule):
    holdings = holdings_at(snapshot_data, tx)
    prices = prices_at(snapshot_data, tx, rule)
    users = {u['user_id']: u.get('display_name') or u.get('username') or '?' for u in snapshot_data['users']}
    names = {r['roster_id']: rule['owners'].get(users.get(r.get('owner_id')), users.get(r.get('owner_id'), f"Team {r['roster_id']}")) for r in snapshot_data['rosters']}
    participants = set(tx.get('roster_ids') or []) | set((tx.get('adds') or {}).values()) | set((tx.get('drops') or {}).values())
    for pick in tx.get('draft_picks') or []:
        participants.update([integer(pick.get('previous_owner_id'), 'pick source', 1), integer(pick.get('owner_id'), 'pick destination', 1)])
    if len(participants) < 2 or any(rid not in holdings for rid in participants):
        raise CheckError('Incomplete trade participants')
    teams = []
    for rid in sorted(participants):
        total = sum(prices.get(pid, 1) for pid in holdings[rid])
        incoming = sum(prices.get(str(pid), 1) for pid, dest in (tx.get('adds') or {}).items() if dest == rid)
        outgoing = sum(prices.get(str(pid), 1) for pid, source in (tx.get('drops') or {}).items() if source == rid)
        teams.append({'name': names[rid], 'before': total - incoming + outgoing, 'after': total, 'room': rule['cap'] - total})
    bad_picks = []
    for pick in tx.get('draft_picks') or []:
        identity = f"{integer(pick.get('season'), 'pick year', 2027)}-{integer(pick.get('round'), 'pick round', 1)}-{integer(pick.get('roster_id'), 'pick original', 1)}"
        if identity in rule['forfeited']:
            entry = rule['forfeited'][identity]
            bad_picks.append(f"{entry['owner']}'s original {entry['label']} — FORFEITED")
    issues = any(t['room'] < 0 for t in teams) or bool(bad_picks)
    body = [f"Processed trade {tx['transaction_id']}", 'Checked at processing time; later drops do not erase an earlier cap issue.']
    for team in teams:
        room = f"${team['room']} room" if team['room'] >= 0 else f"${-team['room']} OVER CAP"
        body.append(f"{team['name']}: ${team['before']} -> ${team['after']} / ${rule['cap']} ({room})")
    body.extend(bad_picks)
    if not issues:
        body.append('Under cap; no known forfeited picks included.')
    body.append('Tracked checks only; not full roster/contract approval. No Sleeper action taken.')
    return {'title': 'Busch trade alert: NEEDS REVIEW' if issues else 'Busch trade alert: checks passed', 'body': '\n'.join(body), 'priority': 4 if issues else 3, 'issues': issues}


def send_alert(alert):
    topic = (os.environ.get('NTFY_TOPIC') or '').strip()
    if not topic:
        raise CheckError('NTFY_TOPIC is not configured')
    message = alert['body']
    if len(message.encode()) > 3800:
        message = message.encode()[:3600].decode('utf-8', 'ignore') + '\nSee trade details.'
    response = request_json('https://ntfy.sh/', {'topic': topic, 'title': alert['title'], 'message': message, 'priority': alert.get('priority', 3), 'tags': ['warning'] if alert.get('issues') else ['white_check_mark'], 'click': LINK})
    if not isinstance(response, dict) or not response.get('id'):
        raise CheckError('ntfy did not confirm delivery')
    print('ntfy accepted alert:', response['id'])


def confirm_setup(state, send, save):
    if state.get('startup_confirmed'):
        return
    send({'title': 'Busch trade alerts enabled', 'body': 'Separate Busch trade monitor is ready. Checks scheduled every 5 minutes, including while your PC is off. New completed trades will be checked for the $515 cap and known forfeited picks. GitHub scheduling can run late. Historical trades were baselined quietly; no Sleeper changes.', 'priority': 3, 'issues': False})
    state['startup_confirmed'] = True
    save(state)


class StateStore:
    def __init__(self, repo, token):
        self.repo, self.token, self.sha = repo, token, None

    def api(self, path, data=None):
        return request_json('https://api.github.com/repos/' + self.repo + path, data, self.token)

    def load(self):
        try:
            value = self.api(f'/contents/{STATE_FILE}?ref={STATE_BRANCH}')
        except CheckError as error:
            if str(error) == 'HTTP 404':
                return None
            raise
        self.sha = value['sha']
        state = json.loads(base64.b64decode(value['content']))
        if state.get('schema') != 1 or state.get('league') != LEAGUE or not isinstance(state.get('seen'), dict):
            raise CheckError('Monitor state invalid; do not silently reset')
        return state

    def save(self, state):
        if not self.sha:
            try:
                self.api(f'/git/ref/heads/{STATE_BRANCH}')
            except CheckError as error:
                if str(error) != 'HTTP 404':
                    raise
                head = self.api('/git/ref/heads/main')['object']['sha']
                self.api('/git/refs', {'ref': 'refs/heads/' + STATE_BRANCH, 'sha': head})
        payload = {'message': 'Record Busch trade alert state [skip ci]', 'branch': STATE_BRANCH, 'content': base64.b64encode((json.dumps(state, sort_keys=True, indent=2)+'\n').encode()).decode()}
        if self.sha:
            payload['sha'] = self.sha
        # PUT (not POST) is required for GitHub's contents endpoint.
        value = request_json(f'https://api.github.com/repos/{self.repo}/contents/{STATE_FILE}', payload, self.token, method='PUT')
        self.sha = value['content']['sha']


def process(state, transactions, get_snapshot, rule, send, save):
    changed = [tx for tx in completed_trades(transactions) if state['seen'].get(str(tx['transaction_id']), {}).get('signature') != signature(tx) or state['seen'].get(str(tx['transaction_id']), {}).get('phase') == 'unknown']
    if not changed:
        return 0
    try:
        data = get_snapshot()
    except (CheckError, KeyError, TypeError, ValueError):
        data = None
    count = 0
    for tx in changed:
        key = str(tx['transaction_id'])
        prior = state['seen'].get(key, {})
        try:
            if data is None:
                raise CheckError('Snapshot incomplete')
            current = next((t for t in data['transactions'] if str(t['transaction_id']) == key and t.get('status') == 'complete'), None)
            if current is None or signature(current) != signature(tx):
                raise CheckError('Trade changed during check')
            alert = audit_trade(data, current, rule)
            phase = 'verified'
            if prior.get('phase') == 'unknown':
                alert['title'] = alert['title'].replace('Busch trade alert:', 'Busch trade recheck:')
        except (CheckError, KeyError, TypeError, ValueError):
            phase = 'unknown'
            alert = {'title': 'Busch trade alert: UNABLE TO VERIFY', 'body': f'Processed trade {key}\nRequired history or consistent roster data is unavailable. This is NOT a cap approval. The monitor will retry.', 'priority': 4, 'issues': True}
        if phase == 'unknown' and prior.get('phase') == 'unknown' and prior.get('signature') == signature(tx):
            continue
        send(alert)  # Persist only after acknowledged send: retry on failure.
        state['seen'][key] = {'signature': signature(tx), 'phase': phase}
        save(state)
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--initialize', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    rule = rules((ROOT/'index.html').read_text(encoding='utf-8'))
    repo = os.environ.get('GITHUB_REPOSITORY', 'ndjunce/busch-apple-trade-tool')
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        raise CheckError('GitHub token required for durable state')
    store = StateStore(repo, token)
    state = store.load()
    if args.dry_run:
        transactions = histories()
        data = snapshot()
        for tx in completed_trades(transactions)[-3:]:
            print(json.dumps(audit_trade(data, tx, rule), ensure_ascii=True))
        print('Dry run only; nothing sent or saved.')
        return
    if os.environ.get('BUSCH_TRADE_ALERTS_ENABLED') != 'true':
        print('Busch trade alerts disabled; no changes.')
        return
    if args.initialize:
        if state is not None:
            if state.get('startup_confirmed') is False:
                confirm_setup(state, send_alert, store.save)
                print('Setup confirmation retried without resetting history.')
                return
            raise CheckError('Already initialized; refusing to reset dedupe history')
        if not (os.environ.get('NTFY_TOPIC') or '').strip():
            raise CheckError('NTFY_TOPIC is not configured; baseline not changed')
        transactions = histories()
        # Verify salary sources and reconstruction on the newest trade before
        # enabling. Historical trades are baselined, never sent as new alerts.
        data = snapshot()
        trades = completed_trades(data['transactions'])
        if trades:
            audit_trade(data, trades[-1], rule)
        state = {'schema': 1, 'league': LEAGUE, 'initialized_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'seen': {str(tx['transaction_id']): {'signature': signature(tx), 'phase': 'baseline'} for tx in trades}, 'health': 'ok', 'startup_confirmed': False}
        store.save(state)
        confirm_setup(state, send_alert, store.save)
        print('Initialized; historical completed trades baselined:', len(trades))
        return
    if state is None:
        raise CheckError('Saved monitor state missing; manual investigation required, not automatic reinitialization')
    if state.get('startup_confirmed') is False:
        confirm_setup(state, send_alert, store.save)
    try:
        transactions = histories()
    except CheckError:
        if state.get('health') != 'unavailable':
            send_alert({'title': 'Busch trade monitor: DATA UNAVAILABLE', 'body': 'Required Sleeper trade history could not be loaded. No trades can be approved. Checks will retry; GitHub scheduling may also be delayed.', 'priority': 4, 'issues': True})
            state['health'] = 'unavailable'
            store.save(state)
        raise CheckError('Required transaction history unavailable; check will retry') from None
    if state.get('health') != 'ok':
        send_alert({'title': 'Busch trade monitor: recovered', 'body': 'Sleeper trade history is available again. Checking for newly processed trades since the last successful scan.', 'priority': 3, 'issues': False})
        state['health'] = 'ok'
        store.save(state)
    count = process(state, transactions, snapshot, rule, send_alert, store.save)
    print('New trade alerts:', count)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # No traceback or external error bodies that could reveal secrets.
        print('Busch monitor stopped:', str(error) if isinstance(error, CheckError) else type(error).__name__, file=sys.stderr)
        sys.exit(1)
