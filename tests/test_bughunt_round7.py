"""Public administration state exposes campaign scope independently of setup."""
import unittest
import test_encounter_features as fixture

class StateCampaignScopeTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown

    def test_named_setup_state_includes_campaign_id(self):
        self.assertEqual(self.c.public_state()['active_campaign_id'],self.c.active_campaign())

    def test_unnamed_encounter_state_includes_campaign_id(self):
        self.c.STATE['active_setup']=None
        self.assertEqual(self.c.public_state()['active_campaign_id'],self.c.active_campaign())

    def test_campaign_id_updates_without_named_setup(self):
        self.c.STATE['active_setup']=None
        previous=self.c.public_state()['active_campaign_id']
        other=self.c.STORAGE.create_campaign('Other','','now')
        self.c.STORAGE.set_value('active_campaign',other)
        state=self.c.public_state()
        self.assertNotEqual(state['active_campaign_id'],previous)
        self.assertEqual(state['active_campaign_id'],other)
        self.assertIsNone(state['active_setup'])

if __name__=='__main__':unittest.main()
