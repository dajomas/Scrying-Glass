"""Start-up port check: plain messages instead of a uvicorn traceback."""
import socket
import unittest
from python.scrying_glass_port_check import port_message, port_problems


class PortCheckTests(unittest.TestCase):
    def test_free_ports_report_no_problems(self):
        """Free ports give no problems."""
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        self.assertEqual(port_problems("127.0.0.1", (("Admin", port),)), [])

    def test_busy_port_gives_a_plain_message(self):
        """A port in use is named with its role and a hint about another running instance."""
        with socket.create_server(("127.0.0.1", 0)) as busy:
            port = busy.getsockname()[1]
            problems = port_problems("127.0.0.1", (("Admin", port),))
        self.assertEqual(problems, [("Admin", port, "is already in use")])
        message = port_message("127.0.0.1", problems)
        self.assertIn(f"port {port} (Admin) is already in use", message)
        self.assertIn("may already be running", message)
        self.assertNotIn("Traceback", message)

    def test_server_checks_ports_before_the_database(self):
        """The server runs the port check before opening the database."""
        from pathlib import Path
        source = (Path(__file__).resolve().parents[1] / "scrying_glass_server.py").read_text(encoding="utf-8")
        self.assertLess(source.index("port_problems(CONFIG['network']['bind']"), source.index("SQLiteStorage(DATA_DIR"))


if __name__ == "__main__":
    unittest.main()
