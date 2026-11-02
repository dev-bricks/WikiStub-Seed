---
name: wikistub-seed
version: 1.1.12
type: product-skill
author: dev-bricks
created: 2026-11-02
updated: 2026-11-02
status: production
description: >
  Local-first multilingual JSON knowledge-stub framework with 630+ stubs across
  12 scientific and cultural domains for AI research, documentation, RAG and LLM workflows.
---

# WikiStub-Seed — Product Skill

## 1. Overview & Capabilities

WikiStub-Seed is a local-first, multilingual JSON knowledge-stub starter framework and concept library. It provides 630 curated knowledge stubs across 12 scientific and cultural domains and 85 subcategories. Definitions are provided in German, English, Spanish, Chinese, Japanese, and Russian; relevance notes are provided in German, Spanish, Chinese, Japanese, and Russian with a documented German fallback for currently unpopulated English relevance slots.

### Primary Use Cases
- **AI & RAG Pipelines**: Feed structured multilingual concept stubs into embedding models, vector stores, and LLM context windows.
- **Documentation & Learning Systems**: Export domain stubs into structured Markdown hierarchies for Obsidian vaults, static site generators, and educational curricula.
- **Offline Knowledge Scaffolding**: Fast, local lookup of verified concept definitions without cloud dependency.
- **Static Web / PWA**: Lightweight progressive web app in `web_publisher/` for offline concept exploration.

### Limitations & Out-of-Scope
- WikiStub-Seed is a **seed library**, not a live MediaWiki or collaborative cloud CMS.
- Does not transmit telemetry, track users, or perform unprompted network calls.
- Optional machine translation (`translate.py` / `wikistub_seed_pipeline.py translate`) requires an explicit Anthropic API key, confirmation flags, and a defined finite budget (`max_budget_usd`).

---

## 2. Prerequisites & Environment

- **Python**: 3.10, 3.11, 3.12, or 3.13.
- **Core Dependencies**: Source CLI commands and exports use the Python standard library only.
- **Development & Testing**:
  ```bash
  pip install -r requirements-dev.txt
  ```
- **Node.js**: Required only for static PWA automated test execution (`node --test`).

---

## 3. Human & Agent Execution Patterns

### A. Consistency & Integrity Check
Verify dataset structure, stub counts, and allowed cross-domain duplicates:
```bash
python wikistub_seed_cli.py check
```
- **Expected Output**: 630 stubs checked, 2 allowed cross-domain duplicates (`Graphentheorie`, `Metalle`), 0 incomplete entries.
- **Exit Code**: `0` on success.

### B. Domain Statistics
Inspect stub distribution across all 12 domains:
```bash
python wikistub_seed_cli.py stats
```

### C. Search & Sampling
Query concept definitions or sample stubs:
```bash
# Keyword and definition search
python wikistub_seed_cli.py search "<term>" --lang de
python wikistub_seed_cli.py search "<term>" --lang en

# Random sampling for prompt context
python wikistub_seed_cli.py sample --count 5
```

### D. Pipeline Validation & Markdown Export
Validate the canonical JSON dataset and export structured Markdown files:
```bash
# Structural validation
python wikistub_seed_pipeline.py validate

# Export markdown files into a target directory
python wikistub_seed_pipeline.py export --output ./exported_stubs --english
```

### E. Static PWA Build & Verification
Rebuild generated web assets and verify against regression tests:
```bash
python web_publisher/_build.py
git diff --exit-code -- web_publisher/data
node --test web_publisher/tests/publisher.test.mjs
```

---

## 4. Local Edit Server (Optional)

For local modifications with password protection and soft-delete trash:
```bash
python edit_server.py --port 8080 --host 127.0.0.1
```
- **Boundaries**: Binds to `127.0.0.1` by default; no public exposure.
- **Storage**: Updates are written atomically; soft-deleted items move to `wikistub_seed_trash.json` (gitignored).

---

## 5. Test & Quality Gates

Run all regression suites before committing or proposing changes:
```bash
# Python unit and contract tests (200+ tests)
python -m pytest

# Python source linting
ruff check .

# Static PWA test suite (45 tests)
node --test web_publisher/tests/publisher.test.mjs
```

---

## 6. Safety & Operational Invariants

1. **Zero Egress by Default**: Standard CLI commands (`check`, `stats`, `search`, `export`, `sample`) run entirely offline.
2. **Atomic Writes**: All exports, pipeline writes, and store updates use atomic replace routines (`safe_io.py`) to prevent corrupt files.
3. **No Unbounded Cost**: Translation commands require `--confirm` and will fail closed if budget parameters or API keys are missing.
4. **Version Protection**: Automated hygiene runs do not bump package versions without formal release authorization.
