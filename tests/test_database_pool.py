from contextlib import contextmanager
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import database


class FakeCursor:
    def __init__(self):
        self.closed = False

    def execute(self, query, params):
        raise RuntimeError("query failed")

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.rollbacks = 0

    def cursor(self):
        return self.cursor_instance

    def rollback(self):
        self.rollbacks += 1


def test_pooled_connection_returns_connection_only_once(monkeypatch):
    returned = []
    monkeypatch.setattr(database, "_return_to_pool", returned.append)
    raw_connection = object()

    connection = database._PooledConnection(raw_connection)
    connection.close()
    connection.close()

    assert returned == [raw_connection]


def test_db_execute_rolls_back_failed_transactions(monkeypatch):
    connection = FakeConnection()

    @contextmanager
    def get_connection():
        yield connection

    monkeypatch.setattr(database, "get_connection", get_connection)

    try:
        database.db_execute("SELECT broken")
    except RuntimeError as error:
        assert str(error) == "query failed"
    else:
        raise AssertionError("db_execute must re-raise database errors")

    assert connection.rollbacks == 1
    assert connection.cursor_instance.closed
