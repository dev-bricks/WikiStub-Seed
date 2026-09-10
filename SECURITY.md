# Security Policy / Sicherheitsrichtlinie

[English](#english) | [Deutsch](#deutsch)

---

<a name="deutsch"></a>
## Deutsch

### Unterstützte Versionen (Supported Versions)

| Version | Unterstützt | Status & Anmerkungen |
|---|---|---|
| **1.1.x** | :white_check_mark: Ja | Aktuelle Hauptversion, aktive Sicherheits- & Bugfix-Wartung |
| **1.0.x** | :warning: Eingeschränkt | Nur kritische Sicherheitsfixes |
| **< 1.0** | :x: Nein | End of Life (EOL), bitte auf neuere Version migrieren |

### Sicherheitsphilosophie & Zero-Egress-Garantie

WikiStub-Seed ist als **lokal-zentriertes Wissensgerüst (Local-First)** konzipiert.
1. **Kein unerwarteter Netzwerkverkehr (Zero-Egress)**: Kern-Import, Export, Konsistenzprüfungen und CLI-Befehle arbeiten vollständig offline auf lokalen JSON- und Markdown-Dateien. Es existiert keine Telemetrie und kein Hintergrund-Tracking.
2. **Isolierte optionale Übersetzungs-Schnittstelle**: Externe API-Aufrufe erfolgen ausschließlich bei expliziter Nutzeraktion über den Übersetzungs-Befehl, wenn `ANTHROPIC_API_KEY` konfiguriert und das optionale Paket installiert ist.
3. **Deterministische Integrität**: Die Datensatz-Validierung und der statische PWA-Build (`web_publisher/_build.py`) arbeiten deterministisch und atomar im unprivilegierten Benutzerkontext ohne Root- oder Administrationsrechte (Non-Elevation / RunAsInvoker).
4. **Isolierter lokaler Editiermodus & Authentifizierung**: `edit_server.py` bindet ausschließlich an `127.0.0.1` (Localhost-only), schützt Passwörter per PBKDF2-HMAC-SHA256 Salt/Hash (`wiki_auth.py` in `wiki_auth.json`) und verhindert versehentliches Löschen durch Soft-Delete in `wikistub_seed_trash.json`.

### Service-Level-Agreements (SLAs) & Reaktionszeiten

- **Erste Eingangsbestätigung (Acknowledgement)**: Innerhalb von **48 Stunden** mit Eingangsbestätigung und Tracking-Referenz.
- **Sicherheits-Triage & Risikobewertung**: Innerhalb von **5 Werktagen**.
- **Patch-Bereitstellung & Behebung**: Koordiniertes Release und Security Advisory in der Regel innerhalb von **30 bis 90 Tagen** je nach Komplexität.

### Sicherheitslücke melden

Wenn Sie eine Sicherheitslücke finden, melden Sie diese bitte verantwortungsvoll:

1. **Öffnen Sie kein öffentliches Issue**
2. **Nutzen Sie GitHubs [Private Vulnerability Reporting](https://github.com/dev-bricks/WikiStub-Seed/security/advisories/new)** (bevorzugt) oder kontaktieren Sie uns direkt per E-Mail:
   - Primär (Dachorganisation): `security@open-bricks.org`
   - Organisation: `security@dev-bricks.org`
   - Partnernetzwerk: `security@ellmos.ai`
   - Maintainer-Support: `support@lukasgeiger.com`
   - Maintainer direkt: `lukas@open-bricks.org`
   - GitHub: [`@lukisch`](https://github.com/lukisch)
3. Nennen Sie: Beschreibung, Schritte zur Reproduktion, betroffene Komponenten und mögliche Auswirkungen.

### Service-Level-Agreements (SLA) & Reaktionszeiten

- **Erstrückmeldung:** Verbindlich innerhalb von **48 Stunden** mit Eingangsbestätigung und Tracking-Referenz.
- **Triage & Einstufung:** Qualifizierte Bewertung und Bestätigung innerhalb von **5 Werktagen**.
- **Behebung:** Koordiniertes Release und Security Advisory in der Regel innerhalb von **30 bis 90 Tagen** je nach Komplexität.

### Geltungsbereich (In-Scope)

- Datenintegrität des JSON-Hauptbestands (`wikistub_seed.json`)
- Dateisystem- und Pfadvalidierung in Import-/Export-Pipelines (`wikistub_seed_pipeline.py`, `wiki_store.py`)
- Authentifizierung, Sitzungsverwaltung und Rechteprüfung in `edit_server.py` und `wiki_auth.py`
- XSS- und Injektionsschutz im statischen Web- und PWA-Publisher (`web_publisher/`)
- Authentifizierungs-, Autorisierungs- und Session-Validierung in `edit_server.py`, `wiki_store.py` und `wiki_auth.py`

### Außerhalb des Geltungsbereichs (Out-of-Scope)

- Physischer Zugriff auf den Host-Rechner oder vorangegangene administrative Kompromittierung
- Upstream-Schwachstellen in Python- oder Node.js-Laufzeitumgebungen ohne nachweisbaren Angriffsvektor in WikiStub-Seed

---

<a name="english"></a>
## English

### Supported Versions

| Version | Supported | Status & Notes |
|---|---|---|
| **1.1.x** | :white_check_mark: Yes | Current active release branch, full security & bugfix support |
| **1.0.x** | :warning: Limited | Critical security vulnerabilities only |
| **< 1.0** | :x: No | End of Life (EOL), please upgrade to current version |

### Security Philosophy & Zero-Egress Guarantee

WikiStub-Seed is designed as a **local-first knowledge framework**.
1. **Zero-Egress by Default**: Core data import, Markdown export, consistency checks and CLI operations run completely offline on local JSON and Markdown files. No telemetry, analytics, or background network calls exist.
2. **Isolated Optional Translation Boundary**: External API communication is restricted to explicit user invocation of the translation command and requires an explicitly configured `ANTHROPIC_API_KEY`.
3. **Deterministic Integrity & Non-Elevation**: Dataset validation and the static PWA build (`web_publisher/_build.py`) operate deterministically and atomically in unprivileged user space without administrative elevation (RunAsInvoker).
4. **Isolated Local Edit Mode & Authentication**: `edit_server.py` binds strictly to `127.0.0.1` (localhost only), hashes passwords with PBKDF2-HMAC-SHA256 (`wiki_auth.py` in `wiki_auth.json`), and protects against accidental deletion via soft-delete in `wikistub_seed_trash.json`.

### Service Level Agreements (SLAs)

- **Initial Response & Acknowledgement**: Within **48 hours** with tracking reference.
- **Vulnerability Triage & Risk Assessment**: Within **5 business days**.
- **Remediation & Patch Deployment**: Coordinated release schedule following Coordinated Vulnerability Disclosure (CVD), typically within 30–90 days.

### Reporting a Vulnerability

If you find a security vulnerability, please report it responsibly:

1. **Do NOT open a public issue**
2. **Use GitHub's [Private Vulnerability Reporting](https://github.com/dev-bricks/WikiStub-Seed/security/advisories/new)** (preferred) or contact us directly via email:
   - Primary (Umbrella Ecosystem): `security@open-bricks.org`
   - Organization: `security@dev-bricks.org`
   - Partner Network: `security@ellmos.ai`
   - Maintainer Support: `support@lukasgeiger.com`
   - Maintainer Direct: `lukas@open-bricks.org`
   - GitHub: [`@lukisch`](https://github.com/lukisch)
3. Include: description, steps to reproduce, affected components, and potential impact.

### Response Commitments & SLAs

- **Initial Response:** Within **48 hours** with an acknowledgment and tracking reference.
- **Triage Assessment:** Within **5 business days** confirming validity, severity classification, and reproduction steps.
- **Remediation & Advisory:** Coordinated release typically within **30–90 days**, depending on vulnerability complexity.

### Scope (In-Scope)

- Data integrity of the canonical dataset (`wikistub_seed.json`)
- File system path traversal and sanitization in import/export pipelines (`wikistub_seed_pipeline.py`, `wiki_store.py`)
- Authentication, session validation, and authorization in `edit_server.py` and `wiki_auth.py`
- XSS and DOM injection defenses in the static Web/PWA publisher (`web_publisher/`)
- Authentication, authorization and session handling in `edit_server.py`, `wiki_store.py` and `wiki_auth.py`

### Out of Scope

- Physical access to the local machine or prior administrative compromise
- Upstream vulnerabilities in standard Python or Node.js runtimes without an exploitable vector in WikiStub-Seed
