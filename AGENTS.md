# AGENTS.md - tldrs-vhs

## Scope

`tldrs-vhs` is a local-only, CLI-first content-addressed store for tool outputs.
It emits `vhs://<sha256>` references for stored blobs.

## Quick Commands

```bash
# Install (dev)
pip install -e .

# Run tests
uv run --with pytest python -m pytest -q

# Basic usage
ref=$(tldrs-vhs put path/to/file)
tldrs-vhs get "$ref" --out restored.txt
```

### CLI Extras

```bash
tldrs-vhs ls --limit 20
tldrs-vhs ls --limit 50 --jsonl
tldrs-vhs stats
tldrs-vhs rm "$ref"
tldrs-vhs gc --dry-run --max-size-mb 500
tldrs-vhs gc --max-size-mb 500 --keep-last 10
```

## Storage Layout

- Root: `~/.tldrs-vhs/` (override via `TLDRS_VHS_HOME`)
- Blobs: `blobs/<aa>/<bb>/<hash>`
- Metadata: `meta.sqlite`

## Design Notes

- CLI-only MVP (no daemon/MCP).
- GC supported via `tldrs-vhs gc --max-age-days`, `--max-size-mb`, and `--keep-last`.
- Avoid non-ASCII in files unless already present.

## Safety

- Never delete store data unless explicitly requested.
- GC should be opt-in and visible to the user.
