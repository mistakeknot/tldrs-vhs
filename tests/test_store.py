from io import BytesIO
from pathlib import Path

from tldrs_vhs.store import Store


def test_put_get_has_info_roundtrip(tmp_path: Path) -> None:
    store = Store(root=tmp_path)
    data = b"hello world\n"
    src = tmp_path / "input.txt"
    src.write_bytes(data)

    with src.open("rb") as f:
        ref = store.put(f)

    assert ref.startswith("vhs://")
    assert store.has(ref) is True

    info = store.info(ref)
    assert info is not None
    assert info.size == len(data)

    out = tmp_path / "out.txt"
    store.get(ref, out=out)
    assert out.read_bytes() == data


def test_list_stats_delete(tmp_path: Path) -> None:
    store = Store(root=tmp_path)
    refs = []
    for payload in (b"one", b"two", b"three"):
        ref = store.put(BytesIO(payload))
        refs.append(ref)

    stats = store.stats()
    assert stats["count"] == 3
    assert stats["total_bytes"] == len(b"one") + len(b"two") + len(b"three")

    items = store.list(limit=2)
    assert len(items) == 2
    assert all(item.hash for item in items)

    deleted = store.delete(refs[0])
    assert deleted is True
    assert store.has(refs[0]) is False


def test_compressed_roundtrip(tmp_path: Path) -> None:
    store = Store(root=tmp_path)
    payload = b"hello compressed" * 100
    ref = store.put(BytesIO(payload), compress=True)

    out = tmp_path / "out.bin"
    store.get(ref, out=out)
    assert out.read_bytes() == payload


def test_compress_min_bytes(tmp_path: Path) -> None:
    store = Store(root=tmp_path)

    small = b"small payload"
    ref_small = store.put(BytesIO(small), compress_min_bytes=1024)
    info_small = store.info(ref_small)
    assert info_small is not None
    assert info_small.compression == ""

    big = b"x" * 2048
    ref_big = store.put(BytesIO(big), compress_min_bytes=1)
    info_big = store.info(ref_big)
    assert info_big is not None
    assert info_big.compression == "zlib"
