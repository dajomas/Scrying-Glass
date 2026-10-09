import sqlite3, unittest, sys
from pathlib import Path
from unittest.mock import patch
from python.scrying_glass_storage import SQLiteStorage
class FailingConnection:
    row_factory = None
    closed = False
    def execute(self, sql): raise sqlite3.OperationalError('injected PRAGMA failure')
    def close(self): self.closed = True
connection=FailingConnection()
with patch('python.scrying_glass_storage.sqlite3.connect',return_value=connection):
    try:SQLiteStorage(Path('injected.sqlite3'))
    except sqlite3.OperationalError:pass
assert connection.closed
original=sqlite3.connect
opened=[]
class TrackedConnection(sqlite3.Connection):
    closed_explicitly=False
    def close(self):
        super().close()
        self.closed_explicitly=True
def connect(*a,**kw):
    kw['factory']=TrackedConnection
    c=original(*a,**kw);opened.append(c);return c
with patch('sqlite3.connect',side_effect=connect):
    result=unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.discover('tests'))
assert result.wasSuccessful()
leaks=[c for c in opened if not c.closed_explicitly]
print(f'Connections opened: {len(opened)}; without explicit close: {len(leaks)}')
for c in leaks:c.close()
assert not leaks
print('PASS: failed PRAGMA initialization closes connection; suite closes all tracked connections')

