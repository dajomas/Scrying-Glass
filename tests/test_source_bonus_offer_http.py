"""Real FastAPI ASGI/form boundary; no auth, transaction, storage or live-provider acceptance."""
import json
import unittest
from urllib.parse import urlencode
from unittest.mock import patch
from fastapi import FastAPI
from python import scrying_glass_monster_selection as selection


class SourceBonusOfferHTTPTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from test_manual_monster_bonus_creation import ManualBonusCreationTests
        fixture = ManualBonusCreationTests('test_explicit_manual_bonus_and_unset_roll_total')
        fixture.setUp()
        self.context, self.handler = fixture.context, fixture.handler
        self.app = FastAPI()
        self.app.add_api_route('/api/monsters/lookup', self.handler.monster_lookup_candidates, methods=['GET'])
        self.app.add_api_route('/api/monsters', self.handler.create_monster, methods=['POST'])
        self.context.CONFIG = {'display': {'dndbeyond_image_lookup': True, 'fivetools_fallback': False}}
        self.candidate = dict(found=True, species='Goblin', name='Goblin', provider='D&D Beyond',
            source_url='https://www.dndbeyond.com/monsters/example', legacy=False,
            image_url=None, ac=15, hp='10', initiative_bonus=12,
            initiative_bonus_status='available')
        self.form = dict(name='Goblin', monster_species='Goblin', ac='15',
            hprangestart='10', hprangeend='', color='#842029', quantity='1')

    async def request(self, method, path, *, fields=None, query=''):
        body = urlencode(fields or {}).encode()
        headers = [(b'host', b'fixture.test')]
        if method == 'POST':
            headers.extend([(b'content-type', b'application/x-www-form-urlencoded'),
                            (b'content-length', str(len(body)).encode())])
        scope = dict(type='http', asgi={'version': '3.0', 'spec_version': '2.3'},
            http_version='1.1', method=method, scheme='http', path=path,
            raw_path=path.encode(), query_string=query.encode(), root_path='', headers=headers,
            client=('127.0.0.1', 1234), server=('fixture.test', 80))
        sent = False
        messages = []
        async def receive():
            nonlocal sent
            if not sent:
                sent = True
                return {'type': 'http.request', 'body': body, 'more_body': False}
            return {'type': 'http.disconnect'}
        async def send(message):
            messages.append(message)
        await self.app(scope, receive, send)
        status = next(item['status'] for item in messages if item['type'] == 'http.response.start')
        content = b''.join(item.get('body', b'') for item in messages if item['type'] == 'http.response.body')
        return status, json.loads(content)

    async def lookup(self, **changes):
        candidate = dict(self.candidate, **changes)
        with patch.object(selection, 'dnd_candidates', return_value=[candidate]), patch.object(
                selection.time, 'time', return_value=1000):
            status, response = await self.request('GET', '/api/monsters/lookup', query='species=Goblin')
        self.assertEqual(status, 200)
        self.assertEqual(response['status'], 'ok')
        return response['candidates'][0]

    async def create(self, candidate, **changes):
        fields = dict(self.form, selection_token=candidate['selection_token'],
            initiative_bonus=str(candidate['initiative_bonus']))
        if 'initiative_bonus_offer_token' in candidate:
            fields['initiative_bonus_offer_token'] = candidate['initiative_bonus_offer_token']
        fields.update(changes)
        with patch.object(selection.time, 'time', return_value=1000):
            return await self.request('POST', '/api/monsters', fields=fields)

    def assert_no_creation(self):
        self.context.hp_value_factory.assert_not_called()
        self.context.save_image.assert_not_called()
        self.context.dnd_image.assert_not_called()
        self.context.make_monster.assert_not_called()
        self.context.combatants_changed.assert_not_awaited()
        self.assertEqual(self.context.STATE['monsters'], [])

    async def test_lookup_to_form_creation_preserves_signed_values_and_quantity(self):
        for value in (12, 0, -2):
            with self.subTest(value=value):
                candidate = await self.lookup(initiative_bonus=value)
                status, created = await self.create(candidate, quantity='2')
                self.assertEqual(status, 200)
                self.assertEqual(len(created), 2)
                self.assertEqual(len({item['id'] for item in created}), 2)
                for item in created:
                    self.assertEqual(item['initiative_bonus'], value)
                    self.assertEqual(item['initiative_bonus_origin'], 'source')
                    self.assertEqual(item['monster_source_url'], candidate['source_url'])
                    self.assertIsNone(item['initiative_roll'])
                    self.assertIsNone(item['initiative'])

    async def test_tampered_token_and_changed_form_value_are_422_before_side_effects(self):
        candidate = await self.lookup()
        for changes in ({'initiative_bonus_offer_token': candidate['initiative_bonus_offer_token']+'x'},
                        {'initiative_bonus': '99'}, {'initiative_bonus': ''},
                        {'monster_species': 'Orc'}):
            with self.subTest(changes=changes):
                status, response = await self.create(candidate, **changes)
                self.assertEqual(status, 422)
                self.assertIn('detail', response)
        self.assert_no_creation()

    async def test_other_candidate_selection_is_rejected_over_form_boundary(self):
        first = await self.lookup()
        other = await self.lookup(source_url='https://www.dndbeyond.com/monsters/other')
        status, _ = await self.create(first, selection_token=other['selection_token'])
        self.assertEqual(status, 422)
        self.assert_no_creation()

    async def test_omitted_offer_retains_manual_and_default_origins(self):
        candidate = await self.lookup()
        candidate.pop('initiative_bonus_offer_token')
        for value, origin in (('12', 'manual'), ('', 'default')):
            status, created = await self.create(candidate, initiative_bonus=value)
            self.assertEqual(status, 200)
            self.assertEqual(created[0]['initiative_bonus_origin'], origin)

    async def test_unavailable_lookup_does_not_issue_offer(self):
        candidate = await self.lookup(initiative_bonus=None, initiative_bonus_status='missing')
        self.assertNotIn('initiative_bonus_offer_token', candidate)
        status, created = await self.create(candidate, initiative_bonus='')
        self.assertEqual(status, 200)
        self.assertEqual(created[0]['initiative_bonus'], 0)
        self.assertEqual(created[0]['initiative_bonus_origin'], 'default')


if __name__ == '__main__':
    unittest.main()
