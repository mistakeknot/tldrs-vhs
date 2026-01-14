# tldrs-vhs

Local content-addressed store for tool outputs. Designed to let tools return
small references like `cass://<sha256>` instead of large blobs.

## Install

```bash
pip install -e .
```

## Quick Start

```bash
# Store a file
ref=$(tldrs-vhs put path/to/output.txt)

# Store from stdin
cat output.txt | tldrs-vhs put -

# Check if a ref exists
if tldrs-vhs has "$ref"; then echo "ok"; fi

# Retrieve
tldrs-vhs get "$ref" --out restored.txt
```

## CLI

```
tldrs-vhs put [FILE|-]      # store file or stdin, prints cass://<hash>
tldrs-vhs get REF [--out]   # fetch to stdout or file
 tldrs-vhs has REF          # exit 0 if present
 tldrs-vhs info REF         # show metadata
```

## Storage

- Default root: `~/.tldrs-vhs/`
- Blob path: `blobs/<aa>/<bb>/<hash>`
- Metadata: SQLite at `meta.sqlite`

Override root with `TLDRS_VHS_HOME=/path`.
