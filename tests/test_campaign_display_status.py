"""Real SQLite authorization with seeded sessions and synthetic socket metadata."""
import time
import types
import unittest
import test_campaign_ownership as ownership_tests
from test_campaign_viewers import Socket
from python.scrying_glass_campaign_viewers import viewers


class DisplayStatusTests(unittest.TestCase):
    setUp = ownership_tests.OwnershipTests.setUp
    tearDown = ownership_tests.OwnershipTests.tearDown
    request = ownership_tests.OwnershipTests.request
    call = ownership_tests.OwnershipTests.call
    grant = ownership_tests.OwnershipTests.grant

    def connect(self, token='viewer', campaign=None, revision=7, age=0):
        socket = Socket(token, campaign)
        self.c.SOCKETS.add(socket)
        self.c.features.displays[socket] = {'username':token,'seen':time.time()-age,'revision':revision}
        return socket

    def prepare(self):
        self.grant(self.a, 'alice')
        self.grant(self.b, 'bob')
        self.c.features = types.SimpleNamespace(displays={})
        viewers(self.c).replace(self.a, {'user_ids':[self.ids['viewer']]})

    def summary(self, name='alice'):
        async def feature_summary():
            return {'revision':7,'displays':[{'username':'UNFILTERED'}]}
        return self.call(name, '/api/features', feature_summary)

    def test_owner_gets_one_display_and_not_unfiltered_metadata(self):
        self.prepare()
        self.connect(campaign=self.a)
        value = self.summary()
        self.assertTrue(value['display_scope_available'])
        self.assertEqual([x['username'] for x in value['displays']], ['viewer'])
        with self.assertRaises(self.c.HTTPException):
            self.summary('bob')

    def test_other_campaign_unselected_denied_and_revoked_not_counted(self):
        self.prepare()
        viewers(self.c).replace(self.b, {'user_ids':[self.ids['viewer']]})
        self.connect(campaign=self.b)
        self.connect()
        selected = self.connect(campaign=self.a)
        self.assertEqual(len(self.summary()['displays']), 1)
        viewers(self.c).replace(self.a, {'user_ids':[]})
        self.assertEqual(self.summary()['displays'], [])
        self.assertIn(selected, self.c.SOCKETS)

    def test_auto_selected_single_campaign_disconnect_and_zero(self):
        self.prepare()
        self.assertEqual(self.summary()['displays'], [])
        socket = self.connect()
        self.assertEqual(len(self.summary()['displays']), 1)
        self.c.SOCKETS.remove(socket)
        self.assertEqual(self.summary()['displays'], [])

    def test_role_changes_ownership_and_invalid_sessions_rechecked(self):
        self.prepare()
        self.connect(campaign=self.a)
        self.c.STORAGE.connection.execute("UPDATE users SET role='admin' WHERE username='viewer'")
        self.assertEqual(self.summary()['displays'], [])
        self.connect(token='missing', campaign=self.a)
        self.assertEqual(self.summary()['displays'], [])
        self.grant(self.a, 'bob')
        with self.assertRaises(self.c.HTTPException):
            self.summary('alice')

    def test_multiple_sockets_status_and_superadmin_still_campaign_scoped(self):
        self.prepare()
        self.connect(campaign=self.a)
        self.connect(campaign=self.a, revision=6)
        self.connect(campaign=self.a, age=40)
        viewers(self.c).replace(self.b, {'user_ids':[self.ids['viewer']]})
        self.connect(campaign=self.b)
        value = self.summary('root')
        self.assertEqual([x['status'] for x in value['displays']], ['live','behind','stale'])


if __name__ == '__main__':
    unittest.main()
