"""Serve split Admin sources through the existing StaticFiles HTTP behavior."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock

from fastapi.staticfiles import StaticFiles
from .scrying_glass_admin_source import read_admin_script


class AdminScriptStaticFiles(StaticFiles):
    """Replace only admin.js lookup; retain normal static response handling.

    The assembled file is a disposable runtime artifact outside the checkout.
    Tracked source files remain below the source-size limit. Re-read fragments
    for each admin.js lookup so source edits do not require a server restart.
    """

    def __init__(self, *, directory, **kwargs):
        super().__init__(directory=directory, **kwargs)
        self._admin_source_directory = Path(directory)
        self._admin_bundle_lock = Lock()
        self._admin_bundle_directory = TemporaryDirectory(prefix="scrying-admin-")
        self._admin_bundle_path = Path(self._admin_bundle_directory.name) / "admin.js"
        self._admin_bundle_content = None
        self._refresh_admin_bundle()

    def _refresh_admin_bundle(self):
        with self._admin_bundle_lock:
            content = read_admin_script(self._admin_source_directory)
            if content != self._admin_bundle_content or not self._admin_bundle_path.is_file():
                pending = self._admin_bundle_path.with_suffix(".pending")
                pending.write_bytes(content)
                os.replace(pending, self._admin_bundle_path)
                self._admin_bundle_content = content
            return str(self._admin_bundle_path), self._admin_bundle_path.stat()

    def lookup_path(self, path):
        if path == "admin.js":
            return self._refresh_admin_bundle()
        return super().lookup_path(path)
