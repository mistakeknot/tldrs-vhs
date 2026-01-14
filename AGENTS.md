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

## Storage Layout

- Root: `~/.tldrs-vhs/` (override via `TLDRS_VHS_HOME`)
- Blobs: `blobs/<aa>/<bb>/<hash>`
- Metadata: `meta.sqlite`

## Design Notes

- CLI-only MVP (no daemon/MCP).
- GC supported via `tldrs-vhs gc --max-age-days` and `--max-size-mb`.
- Avoid non-ASCII in files unless already present.

## Safety

- Never delete store data unless explicitly requested.
- GC should be opt-in and visible to the user.
