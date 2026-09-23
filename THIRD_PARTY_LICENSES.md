# Third-Party Licenses & Transparency Notice (Level 1 SBOM)

> **Project:** `dev-bricks/WikiStub-Seed`<br>
> **Audited:** 2026-09-23<br>
> **Repository License:** [MIT License](LICENSE)<br>
> **Repository Attribution Notice:** [NOTICE](NOTICE)<br>
> **Architecture & Privacy:** 100% Local-First, Zero-Egress by default, Unprivileged User-Mode (`RunAsInvoker`), Pure Python Standard Library Core

---

## Executive Summary & Compliance Assurance

`WikiStub-Seed` is engineered under strict architectural and governance invariants: **100% Local-First, Zero-Egress by default, unprivileged user-mode execution (`RunAsInvoker`), and pure offline operation**. The core import, export, validation, CLI, local edit server (`127.0.0.1`), and web publisher operate entirely within local process and filesystem boundaries without unsolicited network communication or telemetry.

All direct, runtime, optional, and development dependencies utilized across `WikiStub-Seed` are distributed under strictly **permissive and free open-source licenses** (MIT, Apache-2.0, PSFL). There are **zero AGPL or restrictive copyleft constraints**, ensuring maximum portability for local knowledge management, RAG pipelines, educational systems, and enterprise documentation workflows.

### Invariant Cross-Reference Matrix

| Invariant ID | Security & Operational Mandate | Technical Enforcement Mechanism | License & Isolation Scope |
|:---|:---|:---|:---|
| `INV-LOCAL-01` | **100% Local-First & Zero Egress** | Core datasets, CLI operations, and exports execute completely offline with zero telemetry and zero external network calls. | [PSFL-2.0](https://docs.python.org/3/license.html) |
| `INV-SEC-02` | **Non-Elevation (`RunAsInvoker`)** | System operates strictly in unprivileged user space without requiring root or administrator elevation. | [MIT](LICENSE) |
| `INV-SCHEMA-03` | **Deterministic Knowledge Schema** | 630 stubs strictly validated across 12 scientific/cultural domains and 85 subcategories with bidirectional consistency checks. | [MIT](LICENSE) |
| `INV-STORE-04` | **Pure Offline Storage & Zero Telemetry** | No tracking, telemetry, user data transmission, or external logging; all state is persisted locally in human-readable JSON or Markdown. | [PSFL-2.0](https://docs.python.org/3/license.html) |
| `INV-SRV-05` | **Localhost-Bound Edit Server** | The optional GUI edit server binds strictly to the loopback interface (`127.0.0.1`), enforces strict JSON content types against CSRF, and validates Host headers against DNS rebinding. | [PSFL-2.0](https://docs.python.org/3/license.html) |
| `INV-AUTH-06` | **PBKDF2 Password Hashing & Soft-Delete Trash** | Optional server passwords use PBKDF2-HMAC-SHA256 hashing; article deletions move safely to soft-delete trash (`wikistub_seed_trash.json`) rather than immediate destruction. | [PSFL-2.0](https://docs.python.org/3/license.html) |
| `INV-PLAT-07` | **Cross-Platform Operating Parity** | Identical behavior, CLI commands, and test verification across Windows, Linux, and macOS environments. | [MIT](LICENSE) |
| `INV-CORE-08` | **Pure Python Standard Library Core** | Core runtime requires zero third-party packages; runs out of the box on standard Python 3.10+. | [PSFL-2.0](https://docs.python.org/3/license.html) |
| `INV-SYNC-09` | **Cloud-Sync Conflict Defense** | Robust repository-level protection against multi-device cloud synchronization collisions (`.gitignore` filters `*.sync-conflict-*`, `*.conflict`, `*-conflict-*`, `LOCK*`). | [MIT](LICENSE) |
| `INV-SLA-10` | **Dual Security Response & Triage SLA** | Commitments to 48-hour response and 5-business-day triage via canonical security channels (`security@open-bricks.org`, `security@dev-bricks.org`, `security@ellmos.ai`). | [SECURITY.md](SECURITY.md) |

---

## Zero-Copyleft Isolation Guarantee & RunAsInvoker Certification

1. **Zero-Copyleft Guarantee:** No component of `WikiStub-Seed` links against, vendors, or invokes any code under GPLv1, GPLv2, GPLv3, AGPLv3, LGPL, SSPL, or CC-BY-SA copyleft licenses. All dependencies and tools are strictly permissive (MIT, Apache-2.0, PSFL-2.0).
2. **Unprivileged Execution (`RunAsInvoker`):** `WikiStub-Seed` requires no administrative privileges, no daemon services, and no root credentials. It operates entirely in unprivileged user space.
3. **Zero-Egress Perimeter:** By default, no network traffic is emitted by `WikiStub-Seed`. When optional translation commands are executed (`wikistub_seed_pipeline.py translate`), network interaction is governed strictly by explicit environment configuration (`ANTHROPIC_API_KEY`).

---

## Runtime Dependency Matrix

The core runtime of `WikiStub-Seed` has **zero external runtime dependencies**.

| Package | Role / Functional Scope | License | Project Repository / Upstream |
|:---|:---|:---|:---|
| **Python Standard Library** | Core CLI, file I/O, JSON processing, HTTP loopback server, hashlib, argparse, pathlib | [PSFL-2.0](https://docs.python.org/3/license.html) | [python/cpython](https://github.com/python/cpython) |
| **Native Web Standards** | Vanilla ES6, HTML5, CSS3, ServiceWorker API, Web App Manifest (Zero npm/bundled JS packages) | [W3C / WHATWG Standards](https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document) | Web Standards |

---

## Optional Runtime Dependencies

| Package | Usage & Purpose | License | Source / Upstream |
|:---|:---|:---|:---|
| **anthropic** (>=0.40.0) | Optional automated AI translation pipeline (`wikistub_seed_pipeline.py translate`) when `ANTHROPIC_API_KEY` is provided | [MIT](https://github.com/anthropics/anthropic-sdk-python/blob/main/LICENSE) | [anthropics/anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python) |

---

## Development & Quality Assurance Tooling

| Package | Usage & Purpose | License | Source / Upstream |
|:---|:---|:---|:---|
| **pytest** (>=8.0.0) | Automated test runner, contract verification suites, mock fixtures | [MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE) | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) |
| **ruff** (>=0.5.0) | High-performance Python linter and code formatting enforcement | [MIT / Apache-2.0](https://github.com/astral-sh/ruff/blob/main/LICENSE-MIT) | [astral-sh/ruff](https://github.com/astral-sh/ruff) |
| **setuptools** (>=77.0.3) | Standard package build backend (PEP 517 / PEP 621 compliant) | [MIT](https://github.com/pypa/setuptools/blob/main/LICENSE) | [pypa/setuptools](https://github.com/pypa/setuptools) |
| **Node.js Test Runner** | Built-in zero-dependency test runner (`node --test`) for static PWA publisher test suite | [MIT](https://github.com/nodejs/node/blob/main/LICENSE) | [nodejs/node](https://github.com/nodejs/node) |

---

## Full License Texts (Excerpts & Notices)

### 1. Python Software Foundation License Version 2 (PSFL-2.0)
Python standard library modules are used under the PSF License Agreement.  
Copyright (c) 2001-2026 Python Software Foundation. All rights reserved.

### 2. MIT License (MIT)
Used by `WikiStub-Seed`, `anthropic`, `pytest`, `setuptools`, and `Node.js`.

> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:  
>  
> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.  
>  
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### 3. Apache License Version 2.0 (Apache-2.0)
Dual-license option used by `ruff`.  
Licensed under the Apache License, Version 2.0. You may obtain a copy of the License at `http://www.apache.org/licenses/LICENSE-2.0`.
