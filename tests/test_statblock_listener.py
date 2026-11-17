"""022.09 statblock listener: port preflight, private transport frames, revocation and isolation.

Native SQLite with seeded sessions and recording sockets; no FastAPI, network or browser.
FastAPI routes and the WebSocket endpoint are in test_statblock_listener_http.py.
"""
import asyncio
import json
import socket
import unittest

import test_statblock_import_service as service_tests
from python.scrying_glass_campaign_ownership import ownership
from python.scrying_glass_port_check import port_message, port_problems
from python.scrying_glass_service_notifications import NotificationsService
from python.scrying_glass_statblock_transport import close_session, frame, notify, sockets


class PortConfigurationTests(unittest.TestCase):
    def free(self):
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            return probe.getsockname()[1]

    def test_every_duplicate_combination_is_reported_before_binding(self):
        a, b = self.free(), self.free()
        labels = ('Admin', 'Client Display', 'Statblocks')
        for ports in ((a, a, b), (a, b, a), (b, a, a), (a, a, a)):
            with self.subTest(ports=ports):
                problems = port_problems('127.0.0.1', tuple(zip(labels, ports)))
                self.assertTrue(problems)
                self.assertTrue(all('more than one listener' in reason for _, _, reason in problems))
                self.assertIn('Give each listener its own port', port_message('127.0.0.1', problems))
        self.assertEqual(port_problems('127.0.0.1', tuple(zip(labels, (a, b, self.free())))), [])

    def test_invalid_and_occupied_statblock_ports(self):
        a, b = self.free(), self.free()
        for bad in (0, 65536, '3200', None, True):
            problems = port_problems('127.0.0.1', (('Admin', a), ('Client Display', b), ('Statblocks', bad)))
            self.assertEqual([(label, reason) for label, _, reason in problems],
                             [('Statblocks', 'is not a port number from 1 to 65535')])
        for position in range(3):
            with socket.create_server(('127.0.0.1', 0)) as busy:
                ports = [self.free(), self.free(), self.free()]
                ports[position] = busy.getsockname()[1]
                labels = ('Admin', 'Client Display', 'Statblocks')
                problems = port_problems('127.0.0.1', tuple(zip(labels, ports)))
            self.assertEqual(problems, [(labels[position], ports[position], 'is already in use')])
            message = port_message('127.0.0.1', problems)
            self.assertIn('--statblock-port', message)
            self.assertIn('may already be running', message)

    def test_default_configuration_and_cli_include_the_listener(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        init = (root / 'python/scrying_glass_init.py').read_text()
        self.assertIn("'statblock_port': 3200", init)
        server = (root / 'scrying_glass_server.py').read_text()
        self.assertIn("--statblock-port", server)
        self.assertIn("('Statblocks', CONFIG['network']['statblock_port'])", server)
        self.assertLess(server.index('port_problems('), server.index('SQLiteStorage(DATA_DIR'))
        self.assertIn('uvicorn.Config(statblock_app', server)


class RecordingSocket:
    def __init__(self, fail=False):
        self.frames, self.closed, self.fail = [], None, fail

    async def send_text(self, text):
        if self.fail:
            raise OSError('gone')
        self.frames.append(json.loads(text))

    async def close(self, code=1000, reason=''):
        self.closed = code


class TransportTests(service_tests.ImportFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.c.broadcast = NotificationsService(self.c).broadcast

    def register(self, token, **kwargs):
        value = RecordingSocket(**kwargs)
        sockets(self.c)[value] = token
        return value

    def test_frames_are_authorized_per_socket_and_carry_no_content(self):
        result = self.prepare(candidate=self.candidate())
        self.apply([{'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': result['selection_id']}])
        message, authorized = frame(self.c, 'alice-token')
        self.assertTrue(authorized)
        self.assertEqual(message['type'], 'state')
        self.assertEqual(message['state']['campaign_id'], self.c.active_campaign())
        text = json.dumps(message)
        for marker in ('5e.tools Goblin', 'content_digest', 'provenance', 'nodes'):
            self.assertNotIn(marker, text)
        for token, code in (('root-token', 'regular_admin_required'), ('viewer-token', 'regular_admin_required'),
                            ('bob-token', 'campaign_forbidden'), ('gone-token', 'unauthenticated')):
            message, authorized = frame(self.c, token)
            self.assertEqual((authorized, message['type'], message['code']), (False, 'revoked', code))

    def test_broadcast_updates_statblock_sockets_separately_from_displays(self):
        from python.scrying_glass_campaign_viewers import viewers
        acl = viewers(self.c); acl.initialize(); acl.replace(self.c.active_campaign(), {'user_ids': [self.ids['viewer']]})
        display = RecordingSocket(); display.cookies = {'client': 'viewer-token'}
        display.query_params = {'campaign_id': self.c.active_campaign()}
        self.c.SOCKETS.add(display)
        alice, bob, broken = self.register('alice-token'), self.register('bob-token'), self.register('alice-token', fail=True)
        asyncio.run(self.c.broadcast())
        self.assertEqual([f['type'] for f in alice.frames], ['state'])
        self.assertIsNone(alice.closed)
        self.assertEqual((bob.frames[0]['type'], bob.closed), ('revoked', 1008))
        self.assertEqual(broken.closed, 1011)
        self.assertEqual(set(sockets(self.c)), {alice})
        self.assertNotIn(alice, self.c.SOCKETS)
        self.assertTrue(display.frames)
        self.assertTrue(all('tiles' not in json.dumps(f) for f in display.frames))
        self.assertTrue(all(f['type'] == 'state' and 'encounter_token' not in json.dumps(f) for f in display.frames))

    def test_role_ownership_and_campaign_changes_revoke_on_the_next_update(self):
        alice = self.register('alice-token')
        ownership(self.c).reassign(self.c.active_campaign(), {'owner_user_id': self.ids['bob']})
        asyncio.run(notify(self.c))
        self.assertEqual((alice.frames[-1]['type'], alice.frames[-1]['code'], alice.closed),
                         ('revoked', 'campaign_forbidden', 1008))
        ownership(self.c).reassign(self.c.active_campaign(), {'owner_user_id': self.ids['alice']})
        again = self.register('alice-token')
        self.c.STORAGE.connection.execute("UPDATE users SET role='superadmin' WHERE username='alice'")
        asyncio.run(notify(self.c))
        self.assertEqual((again.frames[-1]['type'], again.closed), ('revoked', 1008))
        self.assertEqual(sockets(self.c), {})

    def test_campaign_switch_never_sends_the_old_campaign(self):
        alice = self.register('alice-token')
        asyncio.run(notify(self.c))
        old = alice.frames[-1]['state']
        self.c.STORAGE.set_value('active_campaign', self.other)
        asyncio.run(notify(self.c))
        self.assertEqual((alice.frames[-1]['type'], alice.closed), ('revoked', 1008))
        self.assertNotEqual(json.dumps(alice.frames[-1]), json.dumps({'type': 'state', 'state': old}))

    def test_logout_closes_only_that_sessions_sockets(self):
        self.c.SESSIONS['alice-2'] = {'username': 'alice', 'role': 'admin'}
        first, second = self.register('alice-token'), self.register('alice-2')
        asyncio.run(close_session(self.c, 'alice-token'))
        self.assertEqual((first.closed, second.closed), (1008, None))
        self.assertEqual(set(sockets(self.c)), {second})


if __name__ == '__main__':
    unittest.main()
