"""Direct creation-handler signed-offer checks; not authenticated HTTP or browser acceptance."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import HTTPException
from python import scrying_glass_monster_selection as selection
from python.scrying_glass_source_bonus_offer import issue_bonus_offer


class SourceBonusOfferCreationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from test_manual_monster_bonus_creation import ManualBonusCreationTests
        fixture = ManualBonusCreationTests('test_explicit_manual_bonus_and_unset_roll_total')
        fixture.setUp()
        self.context, self.handler = fixture.context, fixture.handler
        self.arguments = dict(fixture.arguments, monster_species='Goblin')
        self.candidate = dict(species='Goblin', name='Goblin', provider='D&D Beyond',
            source_url='https://www.dndbeyond.com/monsters/example', legacy=False,
            image_url=None, initiative_bonus=12, initiative_bonus_status='available')

    def tokens(self, **changes):
        candidate = dict(self.candidate, **changes)
        with patch.object(selection.time, 'time', return_value=1000):
            selected = selection.issue_token(candidate)
        return selected, issue_bonus_offer(candidate, selection._KEY, now=1000)

    async def create(self, selected, offered, bonus='12', **changes):
        args = dict(self.arguments, selection_token=selected,
                    initiative_bonus_offer_token=offered, initiative_bonus=bonus)
        args.update(changes)
        with patch.object(selection.time, 'time', return_value=1000):
            return await self.handler.create_monster(**args)

    def assert_no_side_effects(self):
        self.context.hp_value_factory.assert_not_called()
        self.context.save_image.assert_not_called()
        self.context.dnd_image.assert_not_called()
        self.context.make_monster.assert_not_called()
        self.context.combatants_changed.assert_not_awaited()
        self.assertEqual(self.context.STATE['monsters'], [])

    async def test_signed_values_and_quantity_keep_source_origin_without_roll(self):
        for value in (12, 0, -2):
            selected, offered = self.tokens(initiative_bonus=value)
            result = await self.create(selected, offered, str(value), quantity=2)
            self.assertEqual(len({item['id'] for item in result}), 2)
            for item in result:
                self.assertEqual(item['initiative_bonus'], value)
                self.assertEqual(item['initiative_bonus_origin'], 'source')
                self.assertEqual(item['monster_source_url'], self.candidate['source_url'])
                self.assertIsNone(item['initiative_roll'])
                self.assertIsNone(item['initiative'])

    async def test_tampered_expired_wrong_species_and_wrong_key_rejected(self):
        selected, offered = self.tokens()
        wrong_key = issue_bonus_offer(self.candidate, b'wrong-key', now=1000)
        expired = issue_bonus_offer(self.candidate, selection._KEY, now=-1000)
        for token, changes in ((offered+'x', {}), (expired, {}), (wrong_key, {}),
                               (offered, {'monster_species': 'Orc'})):
            with self.subTest(token=token), self.assertRaises(HTTPException) as caught:
                await self.create(selected, token, **changes)
            self.assertEqual(caught.exception.status_code, 422)
        self.assert_no_side_effects()

    async def test_other_candidate_or_manual_selection_rejected_before_image_save(self):
        _, offered = self.tokens()
        other, _ = self.tokens(source_url='https://www.dndbeyond.com/monsters/other')
        for selected in (other, 'manual', 'invalid'):
            with self.subTest(selected=selected), self.assertRaises(HTTPException) as caught:
                await self.create(selected, offered, image=SimpleNamespace(filename='new.png'))
            self.assertEqual(caught.exception.status_code, 422)
        self.assert_no_side_effects()

    async def test_changed_or_blank_bonus_cannot_claim_source_origin(self):
        selected, offered = self.tokens(initiative_bonus=0)
        for value in ('', '1', 'malformed'):
            with self.subTest(value=value), self.assertRaises(HTTPException) as caught:
                await self.create(selected, offered, value)
            self.assertEqual(caught.exception.status_code, 422)
        self.assert_no_side_effects()

    async def test_no_offer_keeps_manual_and_default_behaviour(self):
        selected, _ = self.tokens()
        for value, origin in (('12', 'manual'), ('', 'default')):
            result = await self.create(selected, '', value)
            self.assertEqual(result[0]['initiative_bonus_origin'], origin)

    async def test_valid_offer_preserves_uploaded_image_precedence(self):
        selected, offered = self.tokens()
        result = await self.create(selected, offered, image=SimpleNamespace(filename='new.png'))
        self.assertEqual(result[0]['image_url'], '/media/new.png')
        self.assertEqual(result[0]['initiative_bonus_origin'], 'source')
        self.context.save_image.assert_called_once()
        self.context.dnd_image.assert_not_called()


if __name__ == '__main__':
    unittest.main()
