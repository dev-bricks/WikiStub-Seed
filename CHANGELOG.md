# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

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
