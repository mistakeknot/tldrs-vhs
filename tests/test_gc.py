from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from tldrs_vhs.store import Store


def _set_last_accessed(store: Store, hash_hex: str, ts: str) -> None:
    with store._conn() as conn:
        conn.execute(
            "UPDATE objects SET last_accessed = ? WHERE hash = ?",
            (ts, hash_hex),
        )


def _hash_from_ref(ref: str) -> str:
    return ref.replace("vhs://", "")


def test_gc_max_age(tmp_path: Path) -> None:
    store = Store(root=tmp_path)

    ref_old = store.put(BytesIO(b"old"))
    ref_new = store.put(BytesIO(b"new"))

    old_ts = datetime(2000, 1, 1, tzinfo=timezone.utc).isoformat()
    _set_last_accessed(store, _hash_from_ref(ref_old), old_ts)

    result = store.gc(max_age_days=1, max_size_mb=None)
    assert result["deleted"] == 1
    assert store.has(ref_old) is False
    assert store.has(ref_new) is True


def test_gc_max_size(tmp_path: Path) -> None:
    store = Store(root=tmp_path)

    ref_a = store.put(BytesIO(b"aaa"))
    ref_b = store.put(BytesIO(b"bbb"))

    # Force a very small cap to delete everything
    result = store.gc(max_age_days=None, max_size_mb=0)
    assert result["deleted"] >= 1
    assert store.has(ref_a) is False
    assert store.has(ref_b) is False
