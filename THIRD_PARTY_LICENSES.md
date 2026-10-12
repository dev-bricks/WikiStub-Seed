# Declared Dependency and License References

> Snapshot: 2026-10-12
> Project license: [MIT](LICENSE)
> Scope: direct Python project declarations, the optional translation integration, and the built-in Node test runner.
> This is a limited inventory, not an SBOM or a complete resolved dependency graph. It does not assess license compatibility or certify compliance. Transitive dependencies and each release artifact's full contents require separate review.

## Runtime and source scope

The source checkout contains the CLI, editor, static PWA, dataset, and reusable Python modules. The runtime wheel contains only the six reusable modules `data_policy.py`, `language_model.py`, `safe_io.py`, `translate.py`, `wiki_auth.py`, and `wiki_store.py`; it does not contain the CLI, editor, dataset, or PWA. The core local data/API modules use the Python standard library.

The optional translation command imports the Anthropic SDK only when translation is requested and a key is configured. The SDK is not a declared dependency in `requirements.txt` (its example line is commented out). Translation sends the requested text and prompt to Anthropic and may incur charges; the locally calculated ceiling is an estimate, not a provider billing guarantee.

## Direct declarations

| Source | Direct declaration | Scope |
|---|---|---|
| `pyproject.toml` build-system | `setuptools>=77.0.3` | PEP 517 build backend |
| `pyproject.toml` optional `dev` | `ruff>=0.5.0`, `pytest>=8.0.0`, `build>=1.2.0`, `setuptools>=77.0.3` | Development and build checks |
| `pyproject.toml` optional `test` | `pytest>=8.0.0`, `build>=1.2.0`, `setuptools>=77.0.3` | Test and artifact checks |
| `requirements-dev.txt` | `ruff==0.15.18`, `pytest>=8.0.0`, `build>=1.2.0`, `setuptools>=77.0.3` | CI/development environment |
| `requirements.txt` | No active third-party requirement; the Anthropic example is commented out | Optional translation setup |
| Node.js | Built-in `node --test` runner; no npm package manifest is used for PWA tests | PWA test command |

This table records project-level declarations, not versions installed by every user or runner. Consult the upstream project and version-specific license files when redistributing or making a licensing determination:

- [setuptools](https://github.com/pypa/setuptools)
- [pytest](https://github.com/pytest-dev/pytest)
- [Ruff](https://github.com/astral-sh/ruff)
- [build](https://github.com/pypa/build)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [Node.js](https://github.com/nodejs/node)
- [Python licensing](https://docs.python.org/3/license.html)

## Data and network behavior

- Local validation, editing, import/export, and PWA builds operate on selected local files.
- The PWA is a static web application. Its service worker caches the static app and dataset after a successful load; availability and persistence depend on the browser and host.
- Translation is an explicit optional network operation. The CLI requires `--confirm-api-cost` and a positive `--max-budget-usd`; direct API calls require an explicit ceiling. This local estimate does not guarantee the amount charged by the provider.
- The local edit server binds to `127.0.0.1`. This describes its configured bind address, not a general security certification.

For repository attribution, see [NOTICE](NOTICE). For reporting security issues, see [SECURITY.md](SECURITY.md).
