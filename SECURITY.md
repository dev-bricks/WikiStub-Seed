# Security Policy / Sicherheitsrichtlinie

[English](#english) | [Deutsch](#deutsch)

## Deutsch

### Versionsstand und Grenzen

Die Paketversion im Repository ist `1.1.12`. Es gibt keine formelle Zusage, ältere Versionszweige unabhängig zu warten; nenne in einer Meldung die betroffene Version und den konkreten Commit oder Release, soweit bekannt.

Die wiederverwendbaren Module können mit ausdrücklich ausgewählten externen Daten- und Authentifizierungspfaden arbeiten. Im Source-Checkout stehen zusätzlich die Projekt-CLI, PWA und lokalen Standarddateien zur Verfügung; das Wheel enthält die API-Module, aber keine Nutzerdatenbank oder PWA. Außerhalb des Source-Checkouts müssen Daten- und Authentifizierungspfade ausdrücklich angegeben werden.

Eine Übersetzung über die CLI ist ein externer Netzwerkvorgang und sendet den ausgewählten Text samt Anweisungen an die Anthropic-API. Dafür verlangt die CLI `ANTHROPIC_API_KEY`, `--confirm-api-cost` und eine positive `--max-budget-usd`-Grenze. Die Modul-APIs `translate_text` und `translate_batch` verlangen stattdessen ein explizites `max_budget_usd`; das CLI-Bestätigungsflag gilt dort nicht. Die lokale Kostenschätzung ist eine Vorabprüfung und garantiert nicht die tatsächliche Providerabrechnung.

Der Editierserver ist für die Bindung an `127.0.0.1` konfiguriert. Das ist keine allgemeine Netzwerksicherheitszertifizierung. Das Passwort wird als PBKDF2-HMAC-SHA256-Hash gespeichert. Lokaler Dateizugriff kann die Schutzwirkung umgehen. Eine vorhandene, beschädigte Authentifizierungsdatei wird abgewiesen; sie wird nicht automatisch überschrieben. Das manuelle Entfernen der Datei setzt die offene Standardrichtlinie ohne Passwort wieder ein.

### Meldeziele, keine garantierten Reaktionszeiten

Die Maintainer bemühen sich, eine Sicherheitsmeldung innerhalb von 48 Stunden zu bestätigen und innerhalb von fünf Werktagen eine erste Triage vorzunehmen. Das sind Ziele, keine garantierten Service-Level. Patch- und Veröffentlichungszeitpunkte hängen von Befund, Kapazität und notwendiger Prüfung ab.

### Sicherheitslücke melden

Bitte eröffne für eine vermutete Schwachstelle kein öffentliches Issue. Nutze nach Möglichkeit [GitHub Private Vulnerability Reporting](https://github.com/dev-bricks/WikiStub-Seed/security/advisories/new) oder einen der veröffentlichten Kontakte:

- `security@open-bricks.org`
- `security@dev-bricks.org`
- `security@ellmos.ai`
- `support@lukasgeiger.com`
- `lukas@open-bricks.org`
- GitHub: [@lukisch](https://github.com/lukisch)

Nenne die betroffene Version/Revision, beobachtetes Verhalten, reproduzierbare Schritte und mögliche Auswirkungen. Füge keine echten Zugangsdaten oder Nutzerdaten bei.

### Geltungsbereich

- Integrität und Validierung des JSON-Datensatzes
- Datei- und Pfadverarbeitung in Import-/Export-Pipeline und API
- Rechteprüfung, Authentifizierung und Sitzungsbehandlung des lokalen Editiermodus
- HTML-/DOM-Ausgabe und Datenabruf im statischen PWA-Publisher

Schwachstellen in Python, Node.js, Betriebssystemen oder anderen Upstream-Komponenten fallen nur dann in den Projektumfang, wenn sich ein konkreter Angriffsweg über WikiStub-Seed belegen lässt.

## English

### Version and Limits

The repository package version is `1.1.12`. There is no formal commitment to maintain older release branches independently; include the affected version and commit or release when known.

The reusable modules can operate on explicitly selected external data and authentication paths. The source checkout additionally provides the project CLI, PWA, and local default files; the wheel contains the API modules but no user database or PWA. Outside the source checkout, data and authentication paths must be supplied explicitly.

Translation through the CLI is an external network operation that sends the selected text and instructions to the Anthropic API. The CLI requires `ANTHROPIC_API_KEY`, `--confirm-api-cost`, and a positive `--max-budget-usd` ceiling. The module APIs `translate_text` and `translate_batch` instead require an explicit `max_budget_usd`; the CLI confirmation flag does not apply there. The local estimate is a preflight check, not a guarantee of the provider's actual bill.

The edit server is configured to bind to `127.0.0.1`; this is not a general network-security certification. Passwords are stored as PBKDF2-HMAC-SHA256 hashes. Local filesystem access can bypass this protection. An existing malformed authentication file is rejected and is not overwritten automatically. Manually removing the file restores the open no-password default policy.

### Response Targets, Not Guarantees

Maintainers aim to acknowledge a security report within 48 hours and perform an initial triage within five business days. These are targets, not guaranteed service levels. Fix and release timing depends on the finding, available capacity, and required review.

### Reporting a Vulnerability

Please do not open a public issue for a suspected vulnerability. Use [GitHub Private Vulnerability Reporting](https://github.com/dev-bricks/WikiStub-Seed/security/advisories/new) when available, or contact one of the published addresses:

- `security@open-bricks.org`
- `security@dev-bricks.org`
- `security@ellmos.ai`
- `support@lukasgeiger.com`
- `lukas@open-bricks.org`
- GitHub: [@lukisch](https://github.com/lukisch)

Include the affected version/revision, observed behavior, reproduction steps, and potential impact. Do not attach real credentials or user data.

### Scope

- Dataset integrity and JSON validation
- File and path handling in import/export pipelines and the API
- Authorization, authentication, and session handling in local edit mode
- HTML/DOM output and data retrieval in the static PWA publisher

Upstream issues in Python, Node.js, operating systems, or other dependencies are in scope only when a concrete exploit path through WikiStub-Seed can be shown.
