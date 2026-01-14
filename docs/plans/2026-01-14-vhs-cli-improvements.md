# VHS CLI Improvements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Bead:** [none] (no bead provided)

**Goal:** Add keep-last GC protection, JSONL listing output, and auto-threshold compression with tests.

**Architecture:** Extend Store GC to protect newest N items, extend CLI flags for GC/LS/PUT, and update tests+docs. Stay in main worktree per user request.

**Tech Stack:** Python 3, argparse, sqlite3, pytest

### Task 1: Add TDD tests for new CLI/store behavior

**Files:**
- Modify: `tests/test_gc.py`
- Modify: `tests/test_store.py`

**Step 1: Write the failing test (GC keep-last)**

```python
result = store.gc(max_age_days=None, max_size_mb=0, keep_last=1)
assert store.has(ref_newest) is True
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_gc.py::test_gc_keep_last -q`
Expected: FAIL with unexpected keyword or missing behavior

**Step 3: Write the failing test (compression threshold)**

```python
ref = store.put(BytesIO(payload), compress_min_bytes=1024)
info = store.info(ref)
assert info.compression == ""
```

**Step 4: Run test to verify it fails**

Run: `python -m pytest tests/test_store.py::test_compress_min_bytes -q`
Expected: FAIL with unexpected keyword or missing behavior

**Step 5: Commit**

```bash
git add tests/test_gc.py tests/test_store.py
git commit -m "test: add keep-last and compression threshold tests"
```

### Task 2: Implement store behavior

**Files:**
- Modify: `src/tldrs_vhs/store.py`

**Step 1: Write minimal implementation for keep-last**

```python
protected = set(row[0] for row in conn.execute(
    "SELECT hash FROM objects ORDER BY last_accessed DESC LIMIT ?",
    (keep_last,),
))
```

**Step 2: Update GC loops to skip protected**

```python
if hash_hex in protected:
    continue
```

**Step 3: Implement compress-min-bytes by spooling raw input, then conditionally compressing**

```python
if do_compress:
    _compress_file(raw_tmp, compressed_tmp)
    temp_path = compressed_tmp
```

**Step 4: Run tests to verify pass**

Run: `python -m pytest tests/test_gc.py::test_gc_keep_last tests/test_store.py::test_compress_min_bytes -q`
Expected: PASS

**Step 5: Commit**

```bash
git add src/tldrs_vhs/store.py
git commit -m "feat: add gc keep-last and compression threshold"
```

### Task 3: CLI and docs updates

**Files:**
- Modify: `src/tldrs_vhs/cli.py`
- Modify: `README.md`
- Modify: `AGENTS.md`

**Step 1: Add CLI flags**

```python
put_p.add_argument("--compress-min-bytes", type=int, default=None)
ls_p.add_argument("--jsonl", action="store_true")
gc_p.add_argument("--keep-last", type=int, default=0)
```

**Step 2: Update output formatting for JSONL**

```python
if args.jsonl:
    for item in items:
        print(json.dumps(item.__dict__))
```

**Step 3: Run tests**

Run: `python -m pytest -q`
Expected: PASS

**Step 4: Commit**

```bash
git add src/tldrs_vhs/cli.py README.md AGENTS.md
git commit -m "feat: add cli flags for jsonl and keep-last"
```

