import contextvars
from concurrent.futures import ThreadPoolExecutor

from netbox_unifi_sync.services import sync_engine

_marker = contextvars.ContextVar("marker", default=None)


def _read_marker():
    return _marker.get()


def test_plain_submit_loses_context():
    # Documents why the helper exists: worker threads start with an empty context.
    token = _marker.set("request")
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            assert executor.submit(_read_marker).result() is None
    finally:
        _marker.reset(token)


def test_submit_with_context_keeps_context():
    token = _marker.set("request")
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [sync_engine._submit_with_context(executor, _read_marker) for _ in range(8)]
            assert [f.result() for f in futures] == ["request"] * 8
    finally:
        _marker.reset(token)


def test_submit_with_context_survives_nested_pools():
    # Controllers -> sites -> devices are three nested pools in the sync engine.
    def outer():
        with ThreadPoolExecutor(max_workers=2) as inner:
            return sync_engine._submit_with_context(inner, _read_marker).result()

    token = _marker.set("request")
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            assert sync_engine._submit_with_context(executor, outer).result() == "request"
    finally:
        _marker.reset(token)


def test_submit_with_context_passes_args_and_kwargs():
    def add(a, b=0):
        return a + b

    with ThreadPoolExecutor(max_workers=1) as executor:
        assert sync_engine._submit_with_context(executor, add, 2, b=3).result() == 5
