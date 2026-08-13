# Optional Local Embedding and Search API

Status: specification, not an enabled runtime component
Version: `wikistub-local-search-v1`
Scope: local-first retrieval over the `wikistub-seed-data-v1` export

This contract describes an optional process that can provide semantic search
without adding a network dependency or a mandatory package to WikiStub-Seed.
The existing CLI, pipeline, JSON format and static PWA remain usable without
the service.

## Design constraints

- The service binds to loopback only (`127.0.0.1`) or an explicitly selected
  local IPC transport. It must never expose a public listener by default.
- No request, model, embedding or query is sent to a cloud service. A model
  file must be supplied locally and its identifier, dimension and checksum are
  recorded in the index metadata.
- The core repository keeps its standard-library-only boundary. The optional
  adapter may use a user-installed embedding backend, but importing the core
  CLI must not import it.
- The canonical input is `output/wikistub-seed-data-v1.json` or an equivalent
  local `wikistub_seed.json` snapshot. The source is read-only while an index
  is built; generated indexes stay outside the public dataset by default.
- Query text is not written to persistent logs. Diagnostics redact query
  contents and model paths unless an operator explicitly enables local debug
  logging.

## Stable identifiers and indexed text

The service reuses the PWA identity rule so a result can be opened in the
existing reader:

```text
id = sha256(category + "\\0" + subcategory + "\\0" + title).hexdigest()[:20]
```

One searchable document is built per stub. Its fields are:

| Field | Source | Indexing rule |
| --- | --- | --- |
| `id` | deterministic identity above | exact filter / result key |
| `title` | `data.MetaWiki.*.*[].title` | weighted lexical and semantic text |
| `tags` | `tags[]` | weighted lexical text and filters |
| `definitions` | `definitions.{lang}` | selected language, then fallback |
| `relevance_i18n` | `relevance_i18n.{lang}` | selected language, then fallback |
| `cat`, `sub` | enclosing map keys | exact filters and result metadata |

The language fallback is the project rule: selected language, German, English,
then any non-empty language. An empty English relevance slot therefore remains
safe for search and display; it does not silently become an empty document.

## Transport and endpoints

The default base URL is `http://127.0.0.1:<port>/v1`. A Unix-domain socket or
Windows named pipe may be used by a host application, but it must expose the
same JSON contract. CORS is disabled by default; a local UI may opt in for its
own loopback origin.

### `GET /v1/health`

Returns readiness without loading a model on demand:

```json
{
  "status": "ready",
  "api": "wikistub-local-search-v1",
  "backend": "lexical",
  "index_state": "ready",
  "stub_count": 630,
  "indexed_at": "2026-08-13T00:00:00Z"
}
```

`status` is `ready`, `degraded` (lexical fallback only), or `error`.

### `GET /v1/capabilities`

Reports what is installed without probing the network:

```json
{
  "api": "wikistub-local-search-v1",
  "modes": ["lexical", "hybrid"],
  "embedding": {
    "available": false,
    "model_id": null,
    "dimension": null
  },
  "languages": ["de", "en", "es", "zh", "ja", "ru"]
}
```

The `semantic` mode is advertised only when a local embedding backend and a
matching index are ready.

### `POST /v1/search`

Request:

```json
{
  "q": "offline semantic search",
  "lang": "en",
  "mode": "hybrid",
  "top_k": 10,
  "filters": {
    "categories": ["07_Informatik_KI"],
    "subcategories": [],
    "tags": []
  }
}
```

Rules:

- `q` is required, trimmed UTF-8 text, with a bounded request length.
- `lang` defaults to `de` and must be one of the dataset languages.
- `mode` is `lexical`, `semantic` or `hybrid`; `top_k` is bounded by the
  implementation (recommended maximum: 100).
- Filters are exact normalized category, subcategory and tag filters. An empty
  filter means no restriction.
- `hybrid` combines the lexical score with cosine similarity. The weights and
  model metadata are returned so clients can explain a result.

Response:

```json
{
  "api": "wikistub-local-search-v1",
  "mode_requested": "hybrid",
  "mode_used": "lexical",
  "fallback": "embedding_backend_unavailable",
  "results": [
    {
      "id": "0123456789abcdef0123",
      "title": "Domain-Driven Design",
      "cat": "07_Informatik_KI",
      "sub": "Software_Engineering",
      "score": 0.91,
      "match": "lexical",
      "snippet": "...business domain..."
    }
  ]
}
```

If a requested semantic backend is unavailable, the service must return a
successful lexical result with an explicit `fallback` value. It must not make
an implicit network request or claim that embeddings were used.

### `POST /v1/index/rebuild` (optional host-only operation)

This operation is not exposed by the PWA. A local operator may request a
rebuild with `{ "source": "<approved local path>" }`. The implementation must
validate the source, write a temporary index, verify its count and checksum,
then atomically replace the previous index. A failed rebuild leaves the old
index usable. The endpoint must not accept arbitrary remote URLs.

## Index backends and lifecycle

The baseline backend is a deterministic lexical index over the existing JSON
search fields. An optional semantic backend may store vectors in a local
SQLite/sidecar format chosen by the host application. Every index records:

```json
{
  "schema": "wikistub-local-search-v1",
  "source_sha256": "...",
  "stub_count": 630,
  "model_id": null,
  "dimension": null,
  "metric": "cosine",
  "created_at": "..."
}
```

Source changes invalidate the index by `source_sha256`; a stale index is
reported as `degraded` and is never silently mixed with a newer dataset.

## Errors and safety

Errors use a stable envelope:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "q must not be empty",
    "retryable": false
  }
}
```

The service must reject malformed JSON, unsupported languages/modes, excessive
`top_k`, missing index metadata and paths outside the approved local source
root. It must not persist credentials, accept arbitrary code, or claim medical
or other domain-specific certainty from a similarity score.

## Acceptance checklist for a future implementation

1. Core CLI and PWA tests pass with the optional backend absent.
2. Loopback-only health, capability and search contract tests pass.
3. Lexical and semantic/hybrid results use the same deterministic IDs.
4. Language fallback and explicit `relevance_i18n.en` values are both tested.
5. Atomic rebuild, stale-index detection, path allowlist and redacted logging
   are tested.
6. A local fixture proves that no DNS, HTTP or cloud SDK call occurs.
