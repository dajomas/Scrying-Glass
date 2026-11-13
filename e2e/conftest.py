"""Real-server Playwright end-to-end fixtures (SG-TODO-021).

Each test gets its own Scrying Glass server process with a throwaway storage
directory and fixed test accounts. No HTTP is intercepted. Every test runs in
Chromium and Firefox; use ``--browser-name`` to select one.
"""
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BROWSERS = ("chromium", "firefox")
ACCOUNTS = {
    "superadmin": ("e2e-super", "super-pass-123"),
    "admin": ("e2e-dm", "dm-pass-1234"),
    "client": ("e2e-viewer", "viewer-pass-123"),
}
ARTIFACTS = Path(os.environ.get("E2E_ARTIFACTS", ROOT / "e2e-results" / "local"))


def pytest_addoption(parser):
    parser.addoption("--browser-name", action="append", choices=BROWSERS,
                     help="Browser to run (repeatable); default: all")
    parser.addoption("--no-progress", action="store_true", help="Use pytest's normal progress output")


def pytest_generate_tests(metafunc):
    if "browser_name" in metafunc.fixturenames:
        names = metafunc.config.getoption("--browser-name") or list(BROWSERS)
        metafunc.parametrize("browser_name", names, scope="session")


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class Server:
    """One Scrying Glass process: admin and client apps on free local ports."""

    def __init__(self, directory):
        self.directory = Path(directory)
        self.admin_port, self.client_port = _free_port(), _free_port()
        self.admin = f"http://127.0.0.1:{self.admin_port}"
        self.client = f"http://127.0.0.1:{self.client_port}"
        self.log_path = self.directory / "server.log"
        users = "\n".join(f'    - {{username: {name}, role: {role}, password: "{password}"}}'
                          for role, (name, password) in ACCOUNTS.items())
        self.config = self.directory / "config.yaml"
        self.config.write_text(
            "network: {bind: \"127.0.0.1\", admin_port: %d, client_port: %d}\n"
            "storage_dir: \"%s\"\n"
            "display: {dndbeyond_image_lookup: false, fivetools_fallback: false, open5e_lookup: false}\n"
            "security:\n  users:\n%s\n" % (self.admin_port, self.client_port,
                                           (self.directory / "data").as_posix(), users),
            encoding="utf-8")
        self.process = None

    def start(self, timeout=30):
        log = self.log_path.open("ab")
        self.process = subprocess.Popen(
            [sys.executable, str(ROOT / "scrying_glass_server.py"), "--config", str(self.config)],
            cwd=self.directory, stdout=log, stderr=subprocess.STDOUT)
        log.close()
        deadline = time.monotonic() + timeout
        for port in (self.admin_port, self.client_port):
            while True:
                if self.process.poll() is not None:
                    raise RuntimeError("Server exited early:\n" + self.log())
                try:
                    socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
                    break
                except OSError:
                    if time.monotonic() > deadline:
                        raise RuntimeError("Server did not start:\n" + self.log())
                    time.sleep(0.1)
        return self

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(10)
        self.process = None

    def log(self):
        return self.log_path.read_text(encoding="utf-8", errors="replace") if self.log_path.exists() else ""


@pytest.fixture
def server(request):
    with tempfile.TemporaryDirectory(prefix="scrying-e2e-") as directory:
        instance = Server(directory).start()
        try:
            yield instance
        finally:
            instance.stop()
            if getattr(request.node, "e2e_failed", False):
                target = _artifact_dir(request.node)
                target.mkdir(parents=True, exist_ok=True)
                (target / "server.log").write_text(instance.log(), encoding="utf-8")


@pytest.fixture(scope="session")
def browser(browser_name):
    with sync_playwright() as playwright:
        launcher = getattr(playwright, browser_name)
        args = ["--no-sandbox"] if browser_name == "chromium" else []
        instance = launcher.launch(headless=os.environ.get("E2E_HEADED") != "1", args=args)
        yield instance
        instance.close()


class Session:
    """Pages for one browser context, with console and page-error capture."""

    def __init__(self, browser, server, label):
        self.server = server
        self.label = label
        self.context = browser.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
        self.context.set_default_timeout(10000)
        self.context.tracing.start(screenshots=True, snapshots=True)
        self.errors, self.console, self.pages = [], [], []
        self.prompts, self.dialogs = [], []

    def page(self):
        page = self.context.new_page()
        page.on("pageerror", lambda error: self.errors.append(f"{self.label}: {error}"))
        page.on("console", lambda message: self.console.append(f"{self.label} [{message.type}] {message.text}"))
        page.on("dialog", self._dialog)
        self.pages.append(page)
        return page

    def _dialog(self, dialog):
        """Accept confirm/alert dialogs; answer prompts from ``self.prompts`` in order."""
        self.dialogs.append((dialog.type, dialog.message))
        if dialog.type == "prompt" and self.prompts:
            dialog.accept(self.prompts.pop(0))
        else:
            dialog.accept()

    def login(self, role, portal="admin"):
        name, password = ACCOUNTS[role]
        page = self.page()
        base = self.server.admin if portal == "admin" else self.server.client
        page.goto(base + "/login")
        page.fill("[name=username]", name)
        page.fill("[name=password]", password)
        page.click("form button")
        page.wait_for_load_state("networkidle")
        return page


@pytest.fixture
def sessions(browser, server, request):
    created = []

    def make(label="dm"):
        session = Session(browser, server, label)
        created.append(session)
        return session

    yield make
    failed = getattr(request.node, "e2e_failed", False)
    target = _artifact_dir(request.node)
    for session in created:
        if failed:
            target.mkdir(parents=True, exist_ok=True)
            for index, page in enumerate(session.pages):
                try:
                    page.screenshot(path=str(target / f"{session.label}-{index}.png"), full_page=True)
                except Exception:
                    pass
            session.context.tracing.stop(path=str(target / f"{session.label}-trace.zip"))
            (target / f"{session.label}-console.log").write_text(
                "\n".join(session.console + session.errors), encoding="utf-8")
        else:
            session.context.tracing.stop()
        session.context.close()
    errors = [error for session in created for error in session.errors]
    if errors and not failed:
        pytest.fail("Uncaught page errors:\n" + "\n".join(errors))


def _artifact_dir(node):
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in node.nodeid.split("::", 1)[-1])
    return ARTIFACTS / "failures" / safe


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        item.e2e_failed = True


# ---------------------------------------------------------------------------
# Progress lines: "Now running test 001/027: <description> [browser] ... SUCCESS"
# The description is the first docstring line of the test. --no-progress restores
# pytest's normal output.
# ---------------------------------------------------------------------------
_PROGRESS = {}
_OUTCOMES = {}


def pytest_sessionstart(session):
    config = session.config
    reporter = config.pluginmanager.get_plugin("terminalreporter")
    if reporter and not config.getoption("--no-progress"):
        _PROGRESS["reporter"] = reporter


def pytest_collection_modifyitems(session, config, items):
    for number, item in enumerate(items, 1):
        item.e2e_number = (number, len(items))


def _describe(item):
    doc = (item.function.__doc__ or "").strip().splitlines()
    text = doc[0].strip().rstrip(".") if doc else item.originalname.removeprefix("test_").replace("_", " ").capitalize()
    browser = item.callspec.params.get("browser_name") if hasattr(item, "callspec") else None
    return f"{text} [{browser}]" if browser else text


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    reporter = _PROGRESS.get("reporter")
    if reporter:
        number, total = getattr(item, "e2e_number", (0, 0))
        reporter.ensure_newline()
        width = max(3, len(str(total)))
        reporter.write(f"Now running test {number:0{width}d}/{total:0{width}d}: {_describe(item)} ... ", flush=True)


def pytest_runtest_logreport(report):
    if report.failed:
        _OUTCOMES.setdefault(report.nodeid, "FAILED" if report.when == "call" else "ERROR")
    elif report.skipped:
        _OUTCOMES.setdefault(report.nodeid, "SKIPPED")


@pytest.hookimpl(trylast=True)
def pytest_runtest_logfinish(nodeid, location):
    reporter = _PROGRESS.get("reporter")
    if reporter:
        outcome = _OUTCOMES.get(nodeid, "SUCCESS")
        markup = {"SUCCESS": {"green": True}, "SKIPPED": {"yellow": True}}.get(outcome, {"red": True, "bold": True})
        reporter.write_line(outcome, **markup)


@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report, config):
    """Suppress pytest's progress letters while the progress lines are active."""
    if _PROGRESS.get("reporter"):
        if report.passed:
            return ("passed" if report.when == "call" else ""), "", ""
        if report.skipped:
            return "skipped", "", ""
        return ("failed" if report.when == "call" else "error"), "", ""
