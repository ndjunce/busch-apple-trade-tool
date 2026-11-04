import copy
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('trade_alerts', ROOT/'scripts/notify_trades.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture(total=490):
    trade = {'transaction_id': 'old-leg', 'type': 'trade', 'status': 'complete', 'created': 10, 'status_updated': 100, 'leg': 1, 'roster_ids': [1, 2], 'adds': {'p': 2}, 'drops': {'p': 1}, 'draft_picks': []}
    data = {'rosters': [{'roster_id': 1, 'owner_id': 'a', 'players': []}, {'roster_id': 2, 'owner_id': 'b', 'players': ['p', 'q']}], 'transactions': [trade], 'users': [{'user_id': 'a', 'display_name': 'A'}, {'user_id': 'b', 'display_name': 'B'}], 'drafts': [{'draft_id': 'd', 'type': 'auction', 'start_time': 1}], 'draft_picks': {'d': [{'player_id': 'p', 'metadata': {'amount': '30'}}, {'player_id': 'q', 'metadata': {'amount': str(total)}}]}, 'players': {}}
    rule = {'cap': 515, 'scale': {}, 'owners': {}, 'forfeited': {'2029-3-10': {'owner': 'Henry', 'label': '2029 3rd'}}}
    return data, trade, rule


class MonitorTests(unittest.TestCase):
    def test_website_rules(self):
        rule = m.rules((ROOT/'index.html').read_text(encoding='utf-8'))
        self.assertEqual(rule['cap'], 515)
        self.assertEqual(len(rule['scale']), 30)
        self.assertEqual(list(rule['forfeited']), ['2029-3-10'])

    def test_cap_boundary(self):
        for other, issue in [(485, False), (486, True)]:
            data, tx, rule = fixture(other)
            result = m.audit_trade(data, tx, rule)
            self.assertEqual(result['issues'], issue)
            self.assertIn(f'${other+30}', result['body'])

    def test_later_drop_does_not_hide_violation(self):
        data, tx, rule = fixture()
        data['transactions'].append({'transaction_id': 'drop', 'type': 'free_agent', 'status': 'complete', 'status_updated': 200, 'drops': {'p': 2}})
        data['rosters'][1]['players'] = ['q']
        self.assertIn('$520', m.audit_trade(data, tx, rule)['body'])

    def test_later_waiver_price_not_used(self):
        data, tx, rule = fixture()
        data['transactions'] += [{'transaction_id': 'drop', 'type': 'free_agent', 'status': 'complete', 'status_updated': 200, 'drops': {'p': 2}}, {'transaction_id': 'waiver', 'type': 'waiver', 'status': 'complete', 'status_updated': 300, 'adds': {'p': 1}, 'settings': {'waiver_bid': 1}}]
        data['rosters'][0]['players'] = ['p']
        data['rosters'][1]['players'] = ['q']
        self.assertIn('$520', m.audit_trade(data, tx, rule)['body'])

    def test_forfeiture_by_original(self):
        for original, expected in [(10, True), (7, False)]:
            data, tx, rule = fixture(100)
            tx['draft_picks'] = [{'season': '2029', 'round': 3, 'roster_id': original, 'previous_owner_id': 1, 'owner_id': 2}]
            self.assertEqual(m.audit_trade(data, tx, rule)['issues'], expected)

    def test_multi_team_conservation(self):
        data, tx, rule = fixture(100)
        data['rosters'].append({'roster_id': 3, 'owner_id': 'c', 'players': ['r']})
        data['users'].append({'user_id': 'c', 'display_name': 'C'})
        data['draft_picks']['d'].append({'player_id': 'r', 'metadata': {'amount': 20}})
        data['rosters'][1]['players'] = ['p']
        data['rosters'][0]['players'] = ['q']
        tx.update({'roster_ids': [1, 2, 3], 'adds': {'p': 2, 'q': 1, 'r': 3}, 'drops': {'p': 1, 'q': 3, 'r': 2}})
        result = m.audit_trade(data, tx, rule)
        self.assertFalse(result['issues'])
        self.assertIn('C:', result['body'])

    def test_all_18_weeks_and_null_failure(self):
        data, tx, rule = fixture()
        called = []
        def get(url):
            week = int(url.rsplit('/', 1)[1]);called.append(week)
            return [tx] if week == 1 else []
        self.assertEqual(m.histories(get), [tx])
        self.assertEqual(sorted(called), list(range(1, 19)))
        with self.assertRaises(m.CheckError):
            m.histories(lambda url: None if url.endswith('/2') else [])

    def test_only_complete_detected(self):
        data, tx, rule = fixture()
        other = dict(tx, transaction_id='pending', status='pending', consenter_ids=[1, 2])
        self.assertEqual(m.completed_trades([tx, other]), [tx])

    def test_processing_timestamp_required(self):
        data, tx, rule = fixture()
        tx.pop('status_updated')
        self.assertEqual(m.completed_trades([tx]), [tx])
        with self.assertRaises(m.CheckError):
            m.audit_trade(data, tx, rule)

    def test_simultaneous_move_is_unknown(self):
        data, tx, rule = fixture(485)
        data['rosters'][1]['players'].append('r')
        data['transactions'].append({'transaction_id': 'same-time', 'type': 'free_agent', 'status': 'complete', 'status_updated': 100, 'adds': {'r': 2}})
        with self.assertRaises(m.CheckError):
            m.audit_trade(data, tx, rule)

    def test_dedupe_and_baseline(self):
        data, tx, rule = fixture()
        state = {'seen': {str(tx['transaction_id']): {'signature': m.signature(tx), 'phase': 'baseline'}}}
        sent=[];saved=[]
        self.assertEqual(m.process(state, [tx], lambda:data, rule, sent.append, lambda s:saved.append(copy.deepcopy(s))),0)
        state = {'seen': {}}
        self.assertEqual(m.process(state, [tx], lambda:data, rule, sent.append, lambda s:saved.append(copy.deepcopy(s))),1)
        self.assertEqual(m.process(state, [tx], lambda:data, rule, sent.append, lambda s:saved.append(copy.deepcopy(s))),0)
        self.assertEqual(len(sent),1)

    def test_send_failure_not_marked(self):
        data, tx, rule = fixture()
        state={'seen':{}}
        def fail(alert):raise m.CheckError('test send failure')
        with self.assertRaises(m.CheckError):m.process(state,[tx],lambda:data,rule,fail,lambda s:None)
        self.assertEqual(state['seen'],{})

    def test_unknown_once_then_correction(self):
        data, tx, rule = fixture()
        state={'seen':{}};sent=[]
        def fail():raise m.CheckError('missing history')
        self.assertEqual(m.process(state,[tx],fail,rule,sent.append,lambda s:None),1)
        self.assertEqual(m.process(state,[tx],fail,rule,sent.append,lambda s:None),0)
        self.assertEqual(m.process(state,[tx],lambda:data,rule,sent.append,lambda s:None),1)
        self.assertIn('UNABLE',sent[0]['title'])
        self.assertIn('recheck',sent[1]['title'])

    def test_setup_confirmation_retry(self):
        state={'seen':{},'startup_confirmed':False}
        def fail(alert):raise m.CheckError('test send failure')
        with self.assertRaises(m.CheckError):m.confirm_setup(state,fail,lambda s:None)
        self.assertFalse(state['startup_confirmed'])
        sent=[];m.confirm_setup(state,sent.append,lambda s:None)
        self.assertTrue(state['startup_confirmed'])
        m.confirm_setup(state,sent.append,lambda s:None)
        self.assertEqual(len(sent),1)

    def test_malformed_snapshot_alerts_unknown(self):
        data, tx, rule = fixture()
        state={'seen':{}};sent=[]
        def malformed():raise KeyError('draft_id')
        self.assertEqual(m.process(state,[tx],malformed,rule,sent.append,lambda s:None),1)
        self.assertIn('UNABLE',sent[0]['title'])


if __name__ == '__main__':
    unittest.main()
