# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

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
