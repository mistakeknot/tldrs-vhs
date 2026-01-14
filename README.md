# tldrs-vhs

Local content-addressed store for tool outputs. Designed to let tools return
small references like `vhs://<sha256>` instead of large blobs.

## Install

**One-liner (recommended)**

```bash
curl -fsSL https://raw.githubusercontent.com/mistakeknot/tldrs-vhs/main/scripts/install.sh | bash
```

**Manual**

```bash
git clone https://github.com/mistakeknot/tldrs-vhs
cd tldrs-vhs
pip install -e .
```

## Quick Start

```bash
# Store a file
ref=$(tldrs-vhs put path/to/output.txt)

# Store from stdin
cat output.txt | tldrs-vhs put -

# Optional compression
cat output.txt | tldrs-vhs put - --compress

# Check if a ref exists
if tldrs-vhs has "$ref"; then echo "ok"; fi

# Retrieve
tldrs-vhs get "$ref" --out restored.txt

# GC (optional)
tldrs-vhs gc --max-age-days 30
tldrs-vhs gc --max-size-mb 500
```

## CLI

```
tldrs-vhs put [FILE|-]      # store file or stdin, prints vhs://<hash>
  --compress               # store compressed payload (zlib)
tldrs-vhs get REF [--out]   # fetch to stdout or file
 tldrs-vhs cat REF          # stdout alias for get
 tldrs-vhs has REF          # exit 0 if present
 tldrs-vhs info REF         # show metadata
 tldrs-vhs rm REF           # delete a ref
 tldrs-vhs ls [--limit N]   # list recent refs
 tldrs-vhs stats            # summary stats
 tldrs-vhs gc [options]     # cleanup (age/size)
```

## Storage

- Default root: `~/.tldrs-vhs/`
- Blob path: `blobs/<aa>/<bb>/<hash>`
- Metadata: SQLite at `meta.sqlite`

Override root with `TLDRS_VHS_HOME=/path`.

## Add to AGENTS.md / CLAUDE.md

Copy/paste this into a project’s `AGENTS.md` or `CLAUDE.md` to enable
`vhs://` refs for large tool outputs:

```md
## VHS (Optional Large Output Storage)

We use `tldrs-vhs` to store large tool outputs locally and pass `vhs://` refs.

Install:
```bash
curl -fsSL https://raw.githubusercontent.com/mistakeknot/tldrs-vhs/main/scripts/install.sh | bash
```

Usage:
```bash
# Store tldrs context as ref
tldrs context <entry> --project . --output vhs

# Include a stored ref in output
tldrs context <entry> --project . --include vhs://<hash>
```

Notes:
- Store location: `~/.tldrs-vhs/` (override with `TLDRS_VHS_HOME`)
- Refs are local-only; include inline output when sharing
```

## Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/mistakeknot/tldrs-vhs/main/scripts/uninstall.sh | bash
```

To also remove local store data:

```bash
curl -fsSL https://raw.githubusercontent.com/mistakeknot/tldrs-vhs/main/scripts/uninstall.sh | bash -s -- --purge-store
```
