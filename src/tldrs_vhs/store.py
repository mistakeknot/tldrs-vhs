from __future__ import annotations

import hashlib
import os
import shutil
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Optional


DEFAULT_HOME = Path.home() / ".tldrs-vhs"
SCHEME = "vhs://"


@dataclass
class ObjectInfo:
    hash: str
    size: int
    created_at: str
    last_accessed: str


class Store:
    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = (root or Path(os.environ.get("TLDRS_VHS_HOME", DEFAULT_HOME))).expanduser().resolve()
        self.blob_root = self.root / "blobs"
        self.db_path = self.root / "meta.sqlite"
        self.root.mkdir(parents=True, exist_ok=True)
        self.blob_root.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS objects (
                    hash TEXT PRIMARY KEY,
                    size INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL
                )
                """
            )

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _blob_path(self, hash_hex: str) -> Path:
        return self.blob_root / hash_hex[:2] / hash_hex[2:4] / hash_hex

    def has(self, ref: str) -> bool:
        hash_hex = parse_ref(ref)
        if not hash_hex:
            return False
        path = self._blob_path(hash_hex)
        if not path.exists():
            return False
        self._touch(hash_hex)
        return True

    def info(self, ref: str) -> Optional[ObjectInfo]:
        hash_hex = parse_ref(ref)
        if not hash_hex:
            return None
        with self._conn() as conn:
            row = conn.execute(
                "SELECT hash, size, created_at, last_accessed FROM objects WHERE hash = ?",
                (hash_hex,),
            ).fetchone()
        if not row:
            return None
        self._touch(hash_hex)
        return ObjectInfo(*row)

    def list(self, limit: int = 20) -> list[ObjectInfo]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT hash, size, created_at, last_accessed FROM objects ORDER BY last_accessed DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [ObjectInfo(*row) for row in rows]

    def stats(self) -> dict:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*), COALESCE(SUM(size), 0) FROM objects"
            ).fetchone()
        count, total_bytes = row if row else (0, 0)
        return {"count": int(count), "total_bytes": int(total_bytes)}

    def get(self, ref: str, out: Optional[Path] = None) -> None:
        hash_hex = parse_ref(ref)
        if not hash_hex:
            raise ValueError("Invalid ref (expected vhs://<sha256>)")
        path = self._blob_path(hash_hex)
        if not path.exists():
            raise FileNotFoundError(f"Missing blob for {hash_hex}")

        self._touch(hash_hex)

        if out is None:
            with path.open("rb") as f:
                shutil.copyfileobj(f, sys.stdout.buffer)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            with path.open("rb") as f, out.open("wb") as dst:
                shutil.copyfileobj(f, dst)

    def put(self, stream: BinaryIO) -> str:
        hasher = hashlib.sha256()
        temp_path = None
        size = 0

        self.root.mkdir(parents=True, exist_ok=True)
        tmp_dir = self.root / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = tmp_dir / f"upload-{os.getpid()}-{os.urandom(6).hex()}"

        with temp_path.open("wb") as tmp:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                hasher.update(chunk)
                tmp.write(chunk)
                size += len(chunk)

        hash_hex = hasher.hexdigest()
        dest = self._blob_path(hash_hex)
        dest.parent.mkdir(parents=True, exist_ok=True)

        if not dest.exists():
            temp_path.replace(dest)
        else:
            temp_path.unlink()

        now = self._now()
        with self._conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO objects (hash, size, created_at, last_accessed) VALUES (?, ?, ?, ?)",
                (hash_hex, size, now, now),
            )

        return f"{SCHEME}{hash_hex}"

    def delete(self, ref: str) -> bool:
        hash_hex = parse_ref(ref)
        if not hash_hex:
            raise ValueError("Invalid ref (expected vhs://<sha256>)")
        deleted = self._delete_blob(hash_hex)
        if deleted:
            with self._conn() as conn:
                conn.execute("DELETE FROM objects WHERE hash = ?", (hash_hex,))
        return deleted

    def _touch(self, hash_hex: str) -> None:
        now = self._now()
        with self._conn() as conn:
            conn.execute(
                "UPDATE objects SET last_accessed = ? WHERE hash = ?",
                (now, hash_hex),
            )

    def gc(self, max_age_days: Optional[int], max_size_mb: Optional[int], dry_run: bool = False) -> dict:
        now = datetime.now(timezone.utc)
        deleted = 0
        freed_bytes = 0

        with self._conn() as conn:
            if max_age_days is not None:
                cutoff = now.timestamp() - (max_age_days * 86400)
                rows = conn.execute(
                    "SELECT hash, size, last_accessed FROM objects"
                ).fetchall()
                for hash_hex, size, last_accessed in rows:
                    try:
                        last_ts = datetime.fromisoformat(last_accessed).timestamp()
                    except Exception:
                        last_ts = now.timestamp()
                    if last_ts < cutoff:
                        if dry_run:
                            deleted += 1
                            freed_bytes += size
                        else:
                            if self._delete_blob(hash_hex):
                                deleted += 1
                                freed_bytes += size
                                conn.execute("DELETE FROM objects WHERE hash = ?", (hash_hex,))

            if max_size_mb is not None:
                cap_bytes = max_size_mb * 1024 * 1024
                total = conn.execute("SELECT COALESCE(SUM(size), 0) FROM objects").fetchone()[0]
                if total > cap_bytes:
                    rows = conn.execute(
                        "SELECT hash, size FROM objects ORDER BY last_accessed ASC"
                    ).fetchall()
                    for hash_hex, size in rows:
                        if total <= cap_bytes:
                            break
                        if dry_run:
                            deleted += 1
                            freed_bytes += size
                            total -= size
                        else:
                            if self._delete_blob(hash_hex):
                                deleted += 1
                                freed_bytes += size
                                total -= size
                                conn.execute("DELETE FROM objects WHERE hash = ?", (hash_hex,))

        return {
            "deleted": deleted,
            "freed_bytes": freed_bytes,
        }

    def _delete_blob(self, hash_hex: str) -> bool:
        path = self._blob_path(hash_hex)
        if path.exists():
            path.unlink()
            return True
        return False


def parse_ref(ref: str) -> Optional[str]:
    if ref.startswith(SCHEME):
        ref = ref[len(SCHEME):]
    ref = ref.strip()
    if len(ref) != 64:
        return None
    if not all(c in "0123456789abcdef" for c in ref):
        return None
    return ref
