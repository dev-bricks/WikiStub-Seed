# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added (2026-06-06)
- `web_publisher/` — vollständiger statischer PWA-Publisher: `index.html`, `app.js`, `sw.js`, `manifest.webmanifest`
- `web_publisher/_build.py` — Build-Schritt: kopiert `metawiki.json` nach `data/` (In-SW-Scope) und erzeugt flachen `search-index.json` (630 Einträge)
- `web_publisher/icons/` — 4 PWA-Icons (192/512px, any + maskable) aus `MetaWiki.ico` via Pillow
- `web_publisher/tests/publisher.test.mjs` — 25 statische Node.js-Tests (Schema, Manifest, SW-Assets, Icons, HTML-Integration); 25/25 grün
- Responsive 3-Spalten-Layout (Kategoriebaum + Stub-Liste + Detail), mobile Breakpoints, DE/EN-Toggle mit LocalStorage, Hash-Routing

### Hinzugefügt / Added
- `llms.txt` als maschinenlesbare Kurzbeschreibung mit kanonischen Links, Datenmodell und Privacy-Grenzen ergänzt.
- `PORTIERUNGSPLAN.md`, `EXPORTFORMAT.md` und `web_publisher/README.md` zur Web/PWA-basierten Plattformstrategie ergänzt.
- `.gitattributes` zur einheitlichen UTF-8-/Zeilenenden-Behandlung.
- Lokales MetaWiki-Icon, README-Einstieg für CLI-Nutzung und Windows-Startskript.
- GitHub-Actions-Smoke-Test für CLI, Pipeline-Validierung und Python-Compile-Checks.

### Geändert / Changed
- README auf English-first Discoverability, klare Abgrenzung zu Wikimedia Meta-Wiki und kompaktere GitHub-Nutzung umgestellt.
- Web/PWA-Publisher-Doku und Requirements-Hinweise auf echte Umlaute bereinigt.
- Repository-Metadaten auf `file-bricks/MetaWiki` aktualisiert.
- Deutsche öffentliche Repo-Texte auf echte Umlaute bereinigt.
- Privacy-/Security-Hinweise ohne persönliche Kontaktadresse geschärft.

### Behoben / Fixed
- Veraltete Clone- und Security-Links aus der früheren persönlichen Ablage ersetzt.
- `cmd_import()` bricht jetzt bei defekter oder unlesbarer `metawiki.json` sauber ab, statt den Import mit unbekanntem Zustand fortzusetzen; Regressionstest für den Load-Fehlerpfad ergänzt.

## [1.0.0] - YYYY-MM-DD

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
