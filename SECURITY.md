# Security Policy / Sicherheitsrichtlinie

## Deutsch

### Sicherheitsphilosophie & Zero-Egress-Garantie

WikiStub-Seed ist als **lokal-zentriertes Wissensgerüst (Local-First)** konzipiert.
1. **Kein unerwarteter Netzwerkverkehr (Zero-Egress)**: Kern-Import, Export, Konsistenzprüfungen und CLI-Befehle arbeiten vollständig offline auf lokalen JSON- und Markdown-Dateien. Es existiert keine Telemetrie und kein Hintergrund-Tracking.
2. **Isolierte optionale Übersetzungs-Schnittstelle**: Externe API-Aufrufe erfolgen ausschließlich bei expliziter Nutzeraktion über den Übersetzungs-Befehl, wenn `ANTHROPIC_API_KEY` konfiguriert und das optionale Paket installiert ist.
3. **Deterministische Integrität**: Die Datensatz-Validierung und der statische PWA-Build (`web_publisher/_build.py`) arbeiten deterministisch und atomar ohne Root- oder Administrationsrechte (Non-Elevation).

### Sicherheitslücke melden

Wenn Sie eine Sicherheitslücke finden, melden Sie diese bitte verantwortungsvoll:

1. **Öffnen Sie kein öffentliches Issue**
2. **Nutzen Sie GitHubs [Private Vulnerability Reporting](https://github.com/dev-bricks/WikiStub-Seed/security/advisories/new)** oder kontaktieren Sie uns direkt per E-Mail:
   - `security@ellmos.ai`
   - `support@lukasgeiger.com`
3. Nennen Sie: Beschreibung, Schritte zur Reproduktion, betroffene Komponenten und mögliche Auswirkungen

### Geltungsbereich

- Datenintegrität des JSON-Hauptbestands (`wikistub_seed.json`)
- Dateisystem- und Pfadvalidierung in Import-/Export-Pipelines
- XSS- und Injektionsschutz im statischen Web- und PWA-Publisher (`web_publisher/`)

### Reaktion

Kritische Sicherheitsmeldungen werden prioritär bearbeitet. Bitte räumen Sie eine angemessene Frist zur Behebung vor einer öffentlichen Offenlegung ein (Coordinated Vulnerability Disclosure).

---

## English

### Security Philosophy & Zero-Egress Guarantee

WikiStub-Seed is designed as a **local-first knowledge framework**.
1. **Zero-Egress by Default**: Core data import, Markdown export, consistency checks and CLI operations run completely offline on local JSON and Markdown files. No telemetry, analytics, or background network calls exist.
2. **Isolated Optional Translation Boundary**: External API communication is restricted to explicit user invocation of the translation command and requires an explicitly configured `ANTHROPIC_API_KEY`.
3. **Deterministic Integrity**: Dataset validation and the static PWA build (`web_publisher/_build.py`) operate deterministically and atomically in unprivileged user space (non-elevation).

### Reporting a Vulnerability

If you find a security vulnerability, please report it responsibly:

1. **Do NOT open a public issue**
2. **Use GitHub's [Private Vulnerability Reporting](https://github.com/dev-bricks/WikiStub-Seed/security/advisories/new)** or contact us directly via email:
   - `security@ellmos.ai`
   - `support@lukasgeiger.com`
3. Include: description, steps to reproduce, affected components, and potential impact

### Scope

- Data integrity of the canonical dataset (`wikistub_seed.json`)
- File system path traversal and sanitization in import/export pipelines
- XSS and DOM injection defenses in the static Web/PWA publisher (`web_publisher/`)

### Response

Critical vulnerabilities receive highest priority. Please allow reasonable time for investigation and patch deployment before coordinated public disclosure.
