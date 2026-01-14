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
