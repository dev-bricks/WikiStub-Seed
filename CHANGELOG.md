# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

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
