import sys
import types
from unittest import mock


class GuardedRealDatabaseAccess(AssertionError):
    pass


def install_dependency_stubs():
    install_mysql_guard()
    install_qt_stubs()
    install_bcrypt_stub()


def install_mysql_guard():
    try:
        import mysql.connector as connector  # type: ignore
        import mysql  # type: ignore
    except Exception:
        mysql = types.ModuleType("mysql")
        connector = types.ModuleType("mysql.connector")

        class Error(Exception):
            def __init__(self, *args, errno=None):
                super().__init__(*args)
                self.errno = errno

        connector.Error = Error
        mysql.connector = connector
        sys.modules["mysql"] = mysql
        sys.modules["mysql.connector"] = connector

    if not hasattr(connector, "Error"):
        connector.Error = Exception

    def guarded_connect(*_args, **_kwargs):
        raise GuardedRealDatabaseAccess(
            "A unit test attempted to open a real MySQL connection. "
            "Patch get_connection() or mysql.connector.connect with a fake."
        )

    if not getattr(connector, "_gnc_lpg_test_guard", False):
        connector._gnc_lpg_original_connect = getattr(connector, "connect", None)
        connector.connect = guarded_connect
        connector._gnc_lpg_test_guard = True


def install_qt_stubs():
    if "PySide6.QtCore" in sys.modules:
        return

    pyside6 = sys.modules.get("PySide6") or types.ModuleType("PySide6")
    qtcore = types.ModuleType("PySide6.QtCore")

    class QObject:
        def __init__(self, *_args, **_kwargs):
            super().__init__()

    def Slot(*_args, **_kwargs):
        def decorator(func):
            return func

        return decorator

    qtcore.QObject = QObject
    qtcore.Slot = Slot
    pyside6.QtCore = qtcore
    sys.modules["PySide6"] = pyside6
    sys.modules["PySide6.QtCore"] = qtcore


def install_bcrypt_stub():
    if "bcrypt" in sys.modules:
        return

    bcrypt = types.ModuleType("bcrypt")

    def checkpw(plain_password, hashed_password):
        return plain_password == hashed_password

    def gensalt():
        return b"unit-test-salt"

    def hashpw(plain_password, _salt):
        return b"hashed:" + plain_password

    bcrypt.checkpw = checkpw
    bcrypt.gensalt = gensalt
    bcrypt.hashpw = hashpw
    sys.modules["bcrypt"] = bcrypt


class FakeStoredResult:
    def __init__(self, rows=None):
        self._rows = list(rows or [])

    def fetchone(self):
        return self._rows.pop(0) if self._rows else None

    def fetchall(self):
        rows = self._rows
        self._rows = []
        return rows


class FakeCursor:
    def __init__(
        self,
        *,
        fetchone_rows=None,
        fetchall_rows=None,
        stored_results=None,
        execute_side_effect=None,
        callproc_side_effect=None,
        lastrowid=101,
    ):
        self.fetchone_rows = list(fetchone_rows or [])
        self.fetchall_rows = list(fetchall_rows or [])
        self._stored_results = list(stored_results or [])
        self.execute_side_effect = execute_side_effect
        self.callproc_side_effect = callproc_side_effect
        self.lastrowid = lastrowid
        self.executed = []
        self.executemany_calls = []
        self.callprocs = []
        self.closed = False

    def execute(self, sql, params=None):
        self.executed.append((sql, params))
        if self.execute_side_effect:
            raise self.execute_side_effect

    def executemany(self, sql, params):
        self.executemany_calls.append((sql, params))
        if self.execute_side_effect:
            raise self.execute_side_effect

    def callproc(self, name, args=None):
        self.callprocs.append((name, list(args or [])))
        if self.callproc_side_effect:
            raise self.callproc_side_effect

    def stored_results(self):
        return list(self._stored_results)

    def fetchone(self):
        return self.fetchone_rows.pop(0) if self.fetchone_rows else None

    def fetchall(self):
        return self.fetchall_rows.pop(0) if self.fetchall_rows else []

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, cursors=None):
        self.cursors = list(cursors or [FakeCursor()])
        self.cursor_calls = []
        self.commits = 0
        self.rollbacks = 0
        self.closed = False
        self.transactions = 0

    @property
    def cursor_obj(self):
        return self.cursors[0]

    def cursor(self, **kwargs):
        self.cursor_calls.append(kwargs)
        if len(self.cursors) == 1:
            return self.cursors[0]
        return self.cursors.pop(0)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True

    def start_transaction(self):
        self.transactions += 1


class FakeView:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def recorder(*args, **kwargs):
            self.calls.append((name, args, kwargs))

        return recorder


def patch_connection(test_case, module, connection):
    patcher = mock.patch.object(module, "get_connection", return_value=connection)
    test_case.addCleanup(patcher.stop)
    return patcher.start()
