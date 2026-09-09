# Security Policy / Sicherheitsrichtlinie

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
3. **Deterministische Integrität**: Die Datensatz-Validierung und der statische PWA-Build (`web_publisher/_build.py`) arbeiten deterministisch und atomar ohne Root- oder Administrationsrechte (Non-Elevation / RunAsInvoker).
4. **Isolierter lokaler Editiermodus**: `edit_server.py` bindet ausschließlich an `127.0.0.1` (Localhost-only), schützt Passwörter per PBKDF2-HMAC-SHA256 Salt/Hash in `wiki_auth.json` und verhindert versehentliches Löschen durch Soft-Delete in `wikistub_seed_trash.json`.

### Service-Level-Agreements (SLAs)

- **Erste Eingangsbestätigung (Acknowledgement)**: Innerhalb von **48 Stunden**
- **Sicherheits-Triage & Risikobewertung**: Innerhalb von **5 Werktagen**
- **Patch-Bereitstellung**: Nach Schweregrad koordiniert via Coordinated Vulnerability Disclosure (CVD)

### Sicherheitslücke melden

Wenn Sie eine Sicherheitslücke finden, melden Sie diese bitte verantwortungsvoll:

1. **Öffnen Sie kein öffentliches Issue**
2. **Nutzen Sie GitHubs [Private Vulnerability Reporting](https://github.com/dev-bricks/WikiStub-Seed/security/advisories/new)** oder GitHub Security Advisories:
   - Advisories: [GitHub Security Advisories](https://github.com/dev-bricks/WikiStub-Seed/security/advisories)
3. **Kontaktieren Sie uns direkt per E-Mail**:
   - `security@open-bricks.org` (Dachorganisation Open-Bricks)
   - `security@ellmos.ai` (Security-Team)
   - `support@lukasgeiger.com` (Maintainer Support)
   - `lukas@open-bricks.org` (Lead Maintainer)
4. Nennen Sie: Beschreibung, Schritte zur Reproduktion, betroffene Komponenten und mögliche Auswirkungen

### Geltungsbereich

- Datenintegrität des JSON-Hauptbestands (`wikistub_seed.json`)
- Dateisystem- und Pfadvalidierung in Import-/Export-Pipelines
- XSS- und Injektionsschutz im statischen Web- und PWA-Publisher (`web_publisher/`)
- Authentifizierungs-, Autorisierungs- und Session-Validierung in `edit_server.py`, `wiki_store.py` und `wiki_auth.py`

### Reaktion

Kritische Sicherheitsmeldungen werden prioritär bearbeitet. Bitte räumen Sie eine angemessene Frist zur Behebung vor einer öffentlichen Offenlegung ein (Coordinated Vulnerability Disclosure).

---

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
3. **Deterministic Integrity**: Dataset validation and the static PWA build (`web_publisher/_build.py`) operate deterministically and atomically in unprivileged user space (non-elevation / RunAsInvoker).
4. **Isolated Local Edit Mode**: `edit_server.py` binds strictly to `127.0.0.1` (localhost only), hashes passwords with PBKDF2-HMAC-SHA256 in `wiki_auth.json`, and protects against accidental deletion via soft-delete in `wikistub_seed_trash.json`.

### Service Level Agreements (SLAs)

- **Initial Response & Acknowledgement**: Within **48 hours**
- **Vulnerability Triage & Risk Assessment**: Within **5 business days**
- **Remediation & Patch Deployment**: Coordinated release schedule following Coordinated Vulnerability Disclosure (CVD)

### Reporting a Vulnerability

If you find a security vulnerability, please report it responsibly:

1. **Do NOT open a public issue**
2. **Use GitHub's [Private Vulnerability Reporting](https://github.com/dev-bricks/WikiStub-Seed/security/advisories/new)** or view security advisories:
   - Advisories: [GitHub Security Advisories](https://github.com/dev-bricks/WikiStub-Seed/security/advisories)
3. **Contact us directly via email**:
   - `security@open-bricks.org` (Umbrella Organization)
   - `security@ellmos.ai` (Security Team)
   - `support@lukasgeiger.com` (Maintainer Support)
   - `lukas@open-bricks.org` (Lead Maintainer)
4. Include: description, steps to reproduce, affected components, and potential impact

### Scope

- Data integrity of the canonical dataset (`wikistub_seed.json`)
- File system path traversal and sanitization in import/export pipelines
- XSS and DOM injection defenses in the static Web/PWA publisher (`web_publisher/`)
- Authentication, authorization and session handling in `edit_server.py`, `wiki_store.py` and `wiki_auth.py`

### Response

Critical vulnerabilities receive highest priority. Please allow reasonable time for investigation and patch deployment before coordinated public disclosure.
