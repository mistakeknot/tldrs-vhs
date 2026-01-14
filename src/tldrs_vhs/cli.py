from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .store import Store
from . import __version__


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="tldrs-vhs",
        description="Local content-addressed store for tool outputs",
    )
    parser.add_argument("--version", action="version", version=__version__)

    sub = parser.add_subparsers(dest="command", required=True)

    put_p = sub.add_parser("put", help="Store a file or stdin")
    put_p.add_argument("file", nargs="?", default="-", help="File path or '-' for stdin")

    get_p = sub.add_parser("get", help="Fetch a ref to stdout or file")
    get_p.add_argument("ref", help="cass://<hash> or raw hash")
    get_p.add_argument("--out", default=None, help="Output file path")

    has_p = sub.add_parser("has", help="Check if ref exists (exit 0/1)")
    has_p.add_argument("ref", help="cass://<hash> or raw hash")

    info_p = sub.add_parser("info", help="Show metadata for a ref")
    info_p.add_argument("ref", help="cass://<hash> or raw hash")

    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    store = Store()

    if args.command == "put":
        if args.file == "-":
            ref = store.put(sys.stdin.buffer)
        else:
            with open(args.file, "rb") as f:
                ref = store.put(f)
        print(ref)
        return 0

    if args.command == "get":
        out = Path(args.out) if args.out else None
        try:
            store.get(args.ref, out=out)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.command == "has":
        return 0 if store.has(args.ref) else 1

    if args.command == "info":
        info = store.info(args.ref)
        if info is None:
            print("{}")
            return 1
        print(json.dumps(info.__dict__, indent=2))
        return 0

    print("Unknown command", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
