# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [1.1.12] - 2026-09-20

### Marketing, Discoverability & Level 1 SBOM Upgrade (Pfad B)
- **18-Punkte-Schnellnavigation mit 100%iger wechselseitiger dualer HTML-Ankerparität**:
  - `README.md` (`### Quick Navigation`) und `README_de.md` (`### Schnellnavigation`) vollständig auf den 18-Punkte-Standard erweitert.
  - Alle Abschnitte mit dualen, rückwärtskompatiblen HTML-Ankern (`<a id="..."></a>`) ausgestattet, sodass historische Links (#13-third-party-licenses--transparency, #14-marketing--target-personas etc.) und nummerierte 18-Punkte-Anker nahtlos ohne Linkbrüche funktionieren.
- **Zielgruppen & Discoverability-Suchanfragen (`[PERSONA-01]` bis `[PERSONA-04]`)**:
  - Vier detaillierte Zielgruppenprofile mit Zielen, Schmerzpunkten und technischen Lösungen direkt in Abschnitt 4 beider READMEs eingebettet: KI- & LLM-Entwickler, Wissensforscher & Ontologen, Local-First- & Zero-Egress-Entwickler, Bildungs- und Dokumentationsteams.
  - Zweisprachige High-Intent-Suchbegriffstabelle für zielgerichtete Auffindbarkeit in Entwicklungs- und RAG-Kontexten.
- **10-Dimensionen-Vergleichsmatrix gegenüber 4 Alternativen**:
  - Umfassende Vergleichsmatrix in Abschnitt 5 über 10 technische Dimensionen und Invarianten (Runtime-Footprint, Schema-Determinismus, Sprachausrichtung, RAG-Eignung, Zero-Egress, RunAsInvoker, Edit-Server, PWA-Publisher, Lizenzierung, SLA) gegen Kiwix/Wikipedia-Dumps, MediaWiki/DokuWiki, Common Crawl Web-Scrapes und statische Doku-Generatoren (Docusaurus/MkDocs).
- **Level 1 SBOM & Dritte-Partei-Lizenzinventar (`THIRD_PARTY_LICENSES.md`)**:
  - Auf Level 1 SBOM (Stand 2026-09-20) gehärtet mit formeller Invarianten-Kreuzreferenztabelle (`INV-LOCAL-01` bis `INV-SLA-10`), Zertifizierung unprivilegierter Ausführung (`RunAsInvoker`) und Zero-Copyleft-Isolationsgarantie (100% permissiv: MIT, PSFL-2.0, Apache-2.0; null GPL/AGPL).
- **Formelle Namensnennung & Root-Attribution (`NOTICE`)**:
  - Kanonische `NOTICE`-Datei im Projekt-Root für `open-bricks` / `dev-bricks` Ökosystem-Attribution und Lizenztransparenz angelegt.
- **Gesetzlicher Hinweis & Haftungsbeschränkung (§ 521 BGB)**:
  - Gesetzliche Schenkungs- und Gefälligkeitsrechts-Klausel nach § 521 BGB in Abschnitt 18 von `README.md` und `README_de.md` verankert.
- **PEP 621 Standard-Metadaten & Versionssprung**:
  - Version in `pyproject.toml` auf `1.1.12` angehoben.
  - `license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md"]` konfiguriert.
- **Shields.io Badges & Synchronisation**:
  - Badges für Version `1.1.12`, Attribution Notice (`NOTICE`), Level 1 SBOM und Testanzahl (217 passed: 172 Python + 45 Node) in beiden READMEs synchronisiert.
  - `llms.txt` und `MARKETING-LOG.txt` auf den Stand 2026-09-20 aktualisiert.
- **Automatisierte Vertragstests (`tests/test_metadata.py`)**:
  - Neue Vertragstests für 18-Punkte-Navigation, duale HTML-Anker, Personas [PERSONA-01]..[PERSONA-04], Vergleichsmatrix, Level 1 SBOM, NOTICE-Datei und § 521 BGB Disclaimer hinzugefügt (172 Python-Tests + 45 Node.js-Tests = 217 Gesamtprüfungen).

## [1.1.11] - 2026-09-13

### Repository-Hygiene & CI-Härtung (Pfad A)
- **CI-Workflow-Härtung & Timeout-Guardrails**:
  - Redundante, doppelte `concurrency:`-Deklarationen in `.github/workflows/tests.yml` und `.github/workflows/source-platform-smoke.yml` bereinigt.
  - Explizite `timeout-minutes`-Schutzleitplanken für alle CI-Jobs hinterlegt (`tests.yml`: `timeout-minutes: 15` für Python-Tests, `timeout-minutes: 10` für PWA-Tests; `source-platform-smoke.yml`: `timeout-minutes: 10`; `stale.yml`: `timeout-minutes: 5`; `welcome.yml`: `timeout-minutes: 5`), um hängende GitHub-Actions-Runner und verwaiste Ressourcen zuverlässig zu terminieren.
- **Gitignore-Härtung (`.gitignore`)**:
  - Schutzfilter um Property-Testing-, Node- und Merge-/Patch-Artefakte erweitert (`.hypothesis/`, `.nyc_output/`, `node_modules/`, `*.orig`, `*.rej`).
- **Windows-Konsolen- & CLI-Resilienz (`wikistub_seed_cli.py`, `wikistub_seed_pipeline.py`)**:
  - `configure_console_output()` auf Modul-Importebene aktiviert (`sys.stdout`/`sys.stderr` mit `errors="replace"`), sodass Terminal-Ausgaben mit Status-Glyphen (`✗`, `✓`) und Emojis (`🌐`) auch in Standard-Windows-Konsolen (`cp1252`) ohne explizite `PYTHONIOENCODING=utf-8`-Umgebungsvariable absolut absturzfrei laufen.
- **Versions- & Dokumentationssynchronisation**:
  - Versionssprung auf `1.1.11` in `pyproject.toml`, Versions- und Test-Badges (212 passed: 167 Python + 45 Node) in `README.md` und `README_de.md` aktualisiert sowie `llms.txt` auf den aktuellen Prüfstand gebracht.
- **Automatisierte Vertragstests (`tests/test_metadata.py`)**:
  - Neue Tests `test_ci_no_duplicate_concurrency` und `test_ci_job_timeouts_configured` hinzugefügt, um Workflow-Integrität und Timeout-Garantien dauerhaft regressionssicher zu prüfen.
  - Testsuite wächst auf 212 Tests (167 Python-Tests + 45 Node.js PWA-Tests), 100% bestanden.

## [1.1.10] - 2026-09-11

### Hinzugefügt / Added
- **15-Punkte Schnellnavigation mit 100%iger wechselseitiger Ankerparität**: `README.md` (`### Quick Navigation`) und `README_de.md` (`### Schnellnavigation`) auf den 15-Punkte-Standard erweitert mit vollständiger wechselseitiger Ankerparität für Drittanbieter-Lizenzen (`#13-third-party-licenses--transparency` / `#13-drittanbieter-lizenzen--transparenz`), Marketing & Zielgruppen (`#14-marketing--target-personas` / `#14-marketing--zielgruppen`) sowie Sprachversionen.
- **Kanonische Governance- & Laufzeitinvarianten-Kennungen**: Tabelle der 10 Invarianten in `README.md` und `README_de.md` mit den normierten Kennungen (`INV-LOCAL-01` bis `INV-SLA-10`) versehen.
- **Dritte-Partei-Lizenzinventar (`THIRD_PARTY_LICENSES.md`)**: Vollständiges Lizenz- und Transparenzinventar für Laufzeit-, Standardbibliothek- und Entwicklungs-/QA-Abhängigkeiten (100% permissive Lizenzen: MIT, PSFL-2.0, Apache-2.0; Null restriktives Copyleft/AGPL) und Governance-Garantien implementiert.
- **Erweitertes Marketing- & Entdeckbarkeits-Log (`MARKETING-LOG.txt`)**: 5-teiliges Standardregister mit Repository-Baseline, 4 detaillierten Ziel-Personas (KI/LLM-Entwickler, Wissensforscher & Ontologen, Local-First/Zero-Egress-Entwickler, Bildungs- und Dokumentationsteams), zweisprachigen High-Intent-Suchbegriffen, Wettbewerbsmatrix (vs. Kiwix, MediaWiki, Common Crawl, Docusaurus) und strategischer Roadmap.
- **PEP 621 Ökosystem-URLs in `pyproject.toml`**: Standardisierte URLs für `"Third-Party Licenses"`, `"Marketing Log"` und `"LLM Ready"` ergänzt.
- **Shields.io Badges**: Badges für Version 1.1.10, Third-Party Licenses (audited 100% permissive) und Marketing Log (active) in `README.md` und `README_de.md` integriert.
- **Automatisierte Vertragstestsuite (`tests/test_metadata.py`)**: Um umfassende Prüfungen für 15-Punkte-Navigation, Ankerparität, Invarianten-Kennungen, `THIRD_PARTY_LICENSES.md`, erweitertes Marketing-Log und PEP 621 URLs erweitert.

### Repository-Hygiene & CI-Matrix-Härtung (Pfad A)
- **PEP 621 Standard-Metadaten in `pyproject.toml`**: Umfassende Betriebssystem-Classifiers (`Operating System :: Microsoft :: Windows`, `Operating System :: POSIX :: Linux`, `Operating System :: MacOS`), standardisierte URLs (`Issues`, `Changelog`, `Security`, `Parent Organization`, `Umbrella Ecosystem`), optionale Entwicklung- und Test-Dependencies (`[project.optional-dependencies]` dev/test) sowie `[tool.pytest.ini_options]` mit `addopts = "-ra -v"` konfiguriert.
- **CI-Matrix-Härtung**: Concurrency-Cancellation (`cancel-in-progress: true`) in `.github/workflows/tests.yml` und `.github/workflows/source-platform-smoke.yml` integriert; Python-Testmatrix auf 3.10, 3.11, 3.12 und 3.13 erweitert.
- **Git-Hygiene in `.gitignore`**: Schutzmuster gegen Multi-Host-Synchronisationskonflikte (`*-conflict-*`, `*.sync-conflict-*`, `*-ASUS-GEI.*`, `*-WORKSTATION-LG.*`), Multi-Agent-Locks (`LOCK`, `LOCK.*`, `*.lock`, `LOCK*.txt`, `LOCK.permissions.json`) sowie Packaging- und Test-Caches (`wheelhouse/`, `.wheel-smoke/`, `coverage/`) gehärtet.
- **Zweisprachige Sicherheitsrichtlinie (`SECURITY.md`)**: Vollständig nach Standard ausgebaut mit verbindlicher 48h Response-SLA, 5-Werktage-Triage-Zusage, offiziellen Kontakten (`security@open-bricks.org`, `security@dev-bricks.org`, `security@ellmos.ai`, `support@lukasgeiger.com`, `lukas@open-bricks.org`, `@lukisch`), Tabelle unterstützter Versionen (1.1.x) und Local-First / Zero-Egress Invarianten.
- **Dokumentation & Badges**: Shields.io Badges in `README.md` und `README_de.md` um die 48h-Sicherheits-SLA ergänzt; `llms.txt` auf den Verifikationsstand synchronisiert.
- **Test-Resilienz (`tests/test_edit_server.py`)**: Request-Retry-Schleife gegen flüchtige Windows-Loopback-Socket-Resets (`[WinError 10053]`).
- **Vertragstestsuite (`tests/test_metadata.py`)**: Automatisierte Tests für PEP 621 URLs, OS-Classifiers, Git-Hygiene-Regeln, CI-Concurrency und Sicherheits-SLA erweitert.

## [1.1.9] - 2026-09-09

### Hinzugefügt / Added
- **14-Punkte Schnellnavigation mit strikter Ankerparität**: Standardisierte Schnellnavigation in `README.md` (`### Quick Navigation`) und `README_de.md` (`### Schnellnavigation`) implementiert mit exakter 1:1-Entsprechung aller 14 Abschnitte.
- **Sicherheitsmodell & 10 Governance-Invarianten**: Verbindliche Tabelle der 10 Architektur- und Laufzeitinvarianten (100% Local-First & Zero-Egress, Non-Elevation / RunAsInvoker, deterministisches Wissensschema, reine Offline-Speicherung, localhost-gebundener Editierserver 127.0.0.1, PBKDF2-Passworthash & Soft-Delete, plattformübergreifende Betriebsparität, reiner Python-Standardbibliothek-Kern, Cloud-Sync-Konfliktschutz, 48h Sicherheits-SLA) in `README.md` und `README_de.md` ergänzt.
- **Sicherheitsrichtlinie & SLA-Erweiterung (`SECURITY.md`)**: Supported Versions Tabelle (1.1.x aktiv unterstützt), feste SLAs (48h Erstbestätigung, 5 Werktage Triage), Sicherheitsadvisories-Verlinkung und Multi-Kanal-Kontaktadressen (`security@open-bricks.org`, `security@ellmos.ai`, `support@lukasgeiger.com`, `lukas@open-bricks.org`) integriert.
- **PEP 621 Metadaten & URLs in `pyproject.toml`**: `Changelog`, `Security`, `"Parent Organization"` und `"Umbrella Ecosystem"` URLs sowie Betriebssystem-Klassifikatoren für Windows, Linux und macOS hinzugefügt.
- **Cloud-Sync-Konflikt- & Lock-Muster in `.gitignore`**: Erweiterung um `*.sync-conflict-*`, `*.conflict`, `*-CONFLIT-*`, `*-conflict-*` sowie `LOCK.*`, `*.lock`, `LOCK*.txt`.
- **CI-Härtung mit Concurrency-Regeln**: GitHub Actions Workflows `tests.yml` und `source-platform-smoke.yml` mit `concurrency: cancel-in-progress: true` abgesichert.
- **Lokales Marketing- und Auffindbarkeitsregister (`MARKETING-LOG.txt`)**: Strukturierte Dokumentation relevanter Discoverability-Pfade, RAG-Kataloge und Ökosystem-Integrationen angelegt.
- **Erweiterte Metadaten- & Contract-Tests (`tests/test_metadata.py`)**: 6 neue automatisierte Tests für Badges, 14-Punkte-Navigation, Governance-Invarianten, Gitignore-Muster, Concurrency und lokales Marketing-Register hinzugefügt (161 Python-Tests + 45 Node.js-Tests = 206 Gesamtprüfungen).

### Geändert / Changed
- Version in `pyproject.toml` auf `1.1.9` angehoben.
- `llms.txt` auf Version 1.1.9, `Last-checked: 2026-09-09` und 206 verifizierte Tests synchronisiert.
- Shields.io Badges in `README.md` und `README_de.md` auf Version `1.1.9`, Security-SLA (48h), Ruff und 206 bestandene Tests aktualisiert.

## [1.1.8] - 2026-08-21

### Hinzugefügt / Added
- **Lokaler passwortgeschützter GUI-Edit-Modus für `web_publisher/`** (Ticket T-20260819-782505468): `edit_server.py` (nur `127.0.0.1`, JSON-API + statisches Ausliefern), `wiki_store.py` (reine CRUD-/Papierkorb-Funktionen, unabhängig von der bestehenden CLI), `wiki_auth.py` (PBKDF2-Passwort-Hash, Session-Verwaltung, Rechte-Berechnung). Rechtemodell wörtlich nach Spezifikation: Neuanlegen immer erlaubt, Bearbeiten/Löschen frei solange kein Passwort gesetzt ist, danach vom Passwort-Inhaber stufenweise bis nur-lesend einschränkbar.
- **GUI-Erweiterung in `web_publisher/app.js`/`index.html`**: Bearbeiten-/Löschen-Buttons je Artikel, Kategorie-/Unterkategorie-Anlegen/-Löschen im Baum, Konto-Panel (Anmelden/Passwort setzen/Passwort ändern/Rechte verteilen). Ohne laufenden `edit_server.py` (z. B. GitHub Pages) bleibt die Seite automatisch im sichtbaren Lesemodus.
- **Zweisprachige Sicherheitsrichtlinie (`SECURITY.md`)**: Umfassende Local-First & Zero-Egress-Garantien, deterministische Integritätsverifikation, Non-Elevation (Betrieb im User-Space) und direkte Sicherheitskontaktadressen (`security@ellmos.ai` / `support@lukasgeiger.com`) implementiert.
- **PEP 621 Standard Classifiers & Metadaten**: `pyproject.toml` um `Programming Language :: Python :: 3.13`, `Operating System :: OS Independent`, `Topic :: Scientific/Engineering :: Information Analysis`, `Documentation` URL und Discovery-Keywords (`zero-egress`, `offline-first`, `dev-bricks`, `open-bricks`) erweitert.
- **Interaktives Mermaid-Sequenzdiagramm**: Zweites zweisprachiges Mermaid-Sequenzdiagramm für den deterministischen Zero-Egress-Export- und lokalen PWA-Offline-Abfragezyklus in `README.md` und `README_de.md` integriert.
- **Erweiterte Geschwisterwerkzeuge- und Ökosystem-Matrix**: 16 Werkzeuge über die Ökosysteme `dev-bricks`, `file-bricks`, `doc-bricks`, `ellmos-ai` und `open-bricks` (`DevCenter`, `CodeBox`, `MethodenAnalyser`, `CareCenter-for-Codex`, `safe-start-for-codex`, `automation-master`, `automizer-for-claude-desktop`, `project-docs-template`, `policy-registry`, `sqlite-transit-sync`, `PDFtoPDFocr`, `MediaBrain`, `DokuReader`, `CleanMarkdown`, `WinStorePackager`, `NoteSpaceLLM`, `open-bricks`) verlinkt.
- **Automatisierte Paritätstestsuite (`tests/test_metadata.py`)**: Auf 9 automatisierte Contract-Tests erweitert (PEP 621 Classifiers, CI Matrix-Integrität, Zero-Egress Sicherheitsrichtlinie, Sibling-Tools-Matrix).

### Geändert / Changed
- `pyproject.toml` Version auf `1.1.8` aktualisiert.
- `llms.txt` Header auf `Last-checked: 2026-08-21` und 199 verifizierte Tests (154 Python + 45 Node.js) synchronisiert.
- Shields.io Badges in `README.md` und `README_de.md` auf Version `1.1.8`, Python `3.10 | 3.11 | 3.12 | 3.13`, Privacy `100% Offline | Zero-Egress`, Security `Local-First | Deterministic` und 199 verifizierte Tests (154 Python + 45 Node) aktualisiert.

## [1.1.7] - 2026-08-16

### Hinzugefügt / Added
- Automatisierte Metadaten-, Manifest- und Dokumentationsparitätstestsuite in `tests/test_metadata.py` zur Verifikation von Version-Parität, Core-Docs, `llms.txt`-Freshness, `ellmos-module.v2.json` Schema und 630-Stubs-Integrität.
- `[tool.ruff]` und `[tool.ruff.lint]` Konfiguration in `pyproject.toml` integriert (`target-version = "py310"`, `line-length = 120`, `ruff check` 100% sauber).
- Discoverability- und Ökosystem-Badges in `README.md` und `README_de.md` um `dev-bricks` Ecosystem- und `open-bricks` Umbrella-Badges sowie Querverweise zu Geschwisterwerkzeugen (`CareCenter-for-Codex`, `MethodenAnalyser`, `DevCenter`, `CodeBox`, `safe-start-for-codex`) erweitert.

### Geändert / Changed
- `pyproject.toml` Version auf `1.1.7` aktualisiert.
- `llms.txt` Header auf `Last-checked: 2026-08-16` und Test-Suite-Verifikation (94 Tests: 49 Python + 45 Node.js) synchronisiert.
- Badges in `README.md` und `README_de.md` auf Teststand und Version synchronisiert.

### TASKSOLVER readback (2026-08-13)
- Die optionale lokale Embedding-/Such-API ist in `EMBEDDING_SEARCH_API.md`
  als loopback-only, offline-fähiger Vertrag mit lexikalischem Fallback,
  deterministischen Stub-IDs und atomarem Index-Rebuild spezifiziert.
- Der Relevanz-Fallback wurde über alle 630 Stubs regressiongetestet. Die
  englischen Relevanzslots sind weiterhin leer; ohne ausdrücklich autorisierten
  Übersetzungs-Backend wurde kein externer API-Aufruf durchgeführt.

### Maintainer verification (2026-08-12)
- 41 Python-Tests, 2 Source-Smoke-Tests und 45 Node.js-PWA-Tests erfolgreich
  ausgeführt; Ruff, vollständiges Compileall, CLI-Stats/Check,
  Pipeline-Validierung, Duplicate-Check und der deterministische PWA-Rebuild
  waren ebenfalls erfolgreich und erzeugten keine getrackte Datendifferenz.
- Die zwei dokumentierten domänenübergreifenden Duplikate bleiben erlaubt;
  unvollständige oder ungültige Einträge wurden nicht gefunden. Es gab keinen
  Übersetzungs-API-Aufruf, Browser-/Device-Smoke, Push oder Release-Schritt.

### Maintainer verification (2026-08-10)
- 41 Python-Tests, 2 Source-Smoke-Tests und 45 Node.js-PWA-Tests erfolgreich
  ausgeführt; Ruff, vollständiges Compileall, CLI-Stats/Check,
  Pipeline-Validierung, Duplicate-Check und der deterministische PWA-Rebuild
  waren ebenfalls erfolgreich.
- Die zwei dokumentierten domänenübergreifenden Duplikate bleiben erlaubt;
  unvollständige oder ungültige Einträge wurden nicht gefunden. Es gab keinen
  Übersetzungs-API-Aufruf, Browser-/Device-Smoke, Push oder Release-Schritt.

### Maintainer verification (2026-08-04)
- 41 Python-Tests, 2 Source-Smoke-Tests und 45 Node.js-PWA-Tests erfolgreich
  ausgeführt; der Arbeitsbaum blieb nach der Verifikation sauber.

### Maintainer verification (2026-08-02)
- 41 Python-Tests, 2 Source-Smoke-Tests und 45 Node.js-PWA-Tests erfolgreich
  ausgeführt. Ruff, Compileall, CLI-Konsistenzcheck über 630 Stubs,
  Pipeline-Validierung sowie der deterministische PWA-Rebuild mit leerem
  `web_publisher/data`-Diff waren erfolgreich.
- Die zwei dokumentierten domänenübergreifenden Duplikate bleiben erlaubt;
  unvollständige oder ungültige Einträge wurden nicht gefunden.

### Maintainer verification (2026-08-01)
- 41 Python-Tests, 45 Node.js-PWA-Tests, der CLI-Konsistenzcheck über 630 Stubs
  und die Pipeline-Validierung erfolgreich ausgeführt. Die zwei dokumentierten
  domänenübergreifenden Duplikate sind erlaubt; unvollständige oder ungültige
  Einträge wurden nicht gefunden.

## [1.1.6] - 2026-07-30

### Geändert / Changed
- `llms.txt` Header auf `Last-checked: 2026-07-30`, `pyproject.toml` Version auf `1.1.6` und Test-Suite-Verifikation (86 Tests: 41 Python + 45 Node.js) synchronisiert.
- Technische Hygiene-, Struktur- & Doku-Wartung (Pfad A) erfolgreich durchgeführt und verifiziert.

## [1.1.5] - 2026-07-29

### Geändert / Changed
- llms.txt Header auf Last-checked: 2026-07-29 und Test-Suite-Verifikation (86 Tests: 41 Python + 45 Node.js) aktualisiert.
- Technische Hygiene-, Struktur- & Doku-Wartung (Pfad A) erfolgreich durchgeführt und verifiziert.


## [1.1.4] - 2026-07-27

### Geändert / Changed
- `llms.txt` Header auf `Last-checked: 2026-07-27` und Test-Suite-Verifikation (86 Tests: 41 Python + 45 Node.js) aktualisiert.
- Technische Hygiene-, Struktur- & Doku-Wartung (Pfad A) erfolgreich durchgeführt und verifiziert.

### Geändert / Changed
- `llms.txt` Header auf `Last-checked: 2026-07-26` und Test-Suite-Verifikation (86 Tests: 41 Python + 45 Node.js) aktualisiert.
- Technische Hygiene-, Wartungs- & Marketing-Audits (Pfad A & B) erfolgreich durchgeführt und verifiziert.

## [1.1.2] - 2026-07-25

### Hinzugefügt / Added
- `pyproject.toml` mit Metadaten und `[tool.pytest.ini_options] pythonpath = "."` für direkte `pytest`-Ausführung angelegt.
- Shields.io Badges (`llms.txt`, Test-Metriken `41 Python | 45 Node`), KI/LLM-Integrationshinweis und Mermaid-Architektur- & Datenfluss-Diagramm in `README.md` und `README_de.md` integriert.

### Geändert / Changed
- `llms.txt` Header auf `Last-checked: 2026-07-25` aktualisiert und um `pyproject.toml` sowie Test-Suite-Metriken ergänzt.

### Hinzugefügt / Added
- Sechs-Sprachen-Auswahl im statischen PWA-Reader und stabile, reihenfolgeunabhängige Deep-Link-IDs.
- `TODO.md`, `RELEASE_GATE.md`, Modulmanifest, Ruff-Gate und dokumentierter GitHub-Default-CodeQL-Schutz für den öffentlichen Repository-Betrieb.
- Regressionstests für fehlende oder defekte Masterdaten, atomare Schreibpfade, Import-Rollback, endliche API-Budgets und blockierten Browser-Speicher.

### Geändert / Changed
- Pflichtdaten werden fail-closed geladen; Import-/Sync-Fehler verwerfen standardmäßig alle Teiländerungen.
- JSON-, Markdown- und PWA-Build-Ausgaben werden atomar und deterministisch geschrieben.
- Sprachspezifische Markdown-Exporte behalten beim Reimport Definitionen und Relevanztexte der gewählten Sprache sowie die deutschen Pflichtfelder.
- CLI-/Pipeline-Fehler liefern aussagekräftige Exitcodes; API-Übersetzungen benötigen explizite Mengen-, Kosten- und Zielsprache-Grenzen.
- Dokumentation beschreibt den tatsächlichen Sprachstand: sechs Definitionssprachen, fünf Relevanzsprachen und deutscher Fallback für Englisch.
- `llms.txt` auf `Last-checked: 2026-07-24` und technische Hygiene-Prüfung durchgeführt.
- Service-Worker-Lebenszyklus wartet auf `skipWaiting()` und `clients.claim()`; PWA-Datenantworten und `localStorage` werden defensiv behandelt.

### Behoben / Fixed
- Verhindert stilles Ersetzen defekter Übersetzungs- oder Masterdateien durch leere Grundstrukturen.
- Windows-CLI stürzt bei umgeleiteter Legacy-Konsolencodierung nicht mehr an Statusglyphen ab.
- Exakte Checkout-Action-Version ist nun auf den unveränderlichen Commit von `v6.0.3` gepinnt.

## [1.1.1] - 2026-07-06

### Geändert / Changed
- Lokale Git-Remote-Konfiguration auf das kanonische Repository `dev-bricks/WikiStub-Seed` aktualisiert.
- `llms.txt` auf `Last-checked: 2026-07-06` aktualisiert.
- README.md und README_de.md um Startführung und Discovery-Kontext für das kanonische Repo `dev-bricks/WikiStub-Seed` ergänzt.
- `llms.txt`, `CONTRIBUTING.md` und `SECURITY.md` von alten `file-bricks`-Links auf die aktuelle `dev-bricks`-Repo-URL synchronisiert.

## [1.1.0] - 2026-06-14

### Hinzugefügt / Added
- Vollständige Übersetzungen für alle 630 Stubs in 4 Sprachen (es, zh, ja, ru) — 5040 Übersetzungsslots gefüllt.
- 6-sprachige READMEs (DE, EN, ES, ZH, JA, RU) für maximale internationale Auffindbarkeit.
- README-Banner als SVG.
- `web_publisher/data/search-index.json` und `web_publisher/data/wikistub_seed.json` aus dem vollständig übersetzten Masterdatensatz neu gebaut.

### Geändert / Changed
- Projekt umbenannt von `MetaWiki` (GitHub: `file-bricks/MetaWiki`) zu `WikiStub-Seed` (GitHub: `dev-bricks/WikiStub-Seed`).
- Repository-Org von `file-bricks` nach `dev-bricks` umgezogen.
- Lokaler Ordner verschoben von `.TOPICS/.SOFTWARE/LLM/REL-PUB_MetaWiki_SOCIAL` nach `.TOPICS/.AI/.MODULES/WikiStub-Seed`.
- Dateien umbenannt: `metawiki.json` → `wikistub_seed.json`, `metawiki_cli.py` → `wikistub_seed_cli.py`, `metawiki_pipeline.py` → `wikistub_seed_pipeline.py`, `MetaWiki.ico` → `wikistub_seed.ico`.
- Alle internen Referenzen, Badge-URLs und Schema-Bezeichner (`metawiki-data-v1` → `wikistub-seed-data-v1`) aktualisiert.
- Disclaimer umformuliert: WikiStub-Seed is a knowledge-stub seed library, not a wiki.
- macOS/Linux-Source-Smokes ergänzt (`tests/source_platform_smoke.py`, `.github/workflows/source-platform-smoke.yml`).
- iOS PWA-Installierbarkeit: Apple-Touch-Icon, Viewport-Fit, Touch-Targets, SW-Cache-Bump.

## [1.0.0] - 2026-02-18

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
