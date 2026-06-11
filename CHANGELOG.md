# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Geändert / Changed (2026-06-11)
- `llms.txt`: `## Last-checked: 2026-06-11`-Header ergänzt; `## Audience`-Abschnitt (5 Zielgruppen) hinzugefügt; `## Search Phrases` als Fenced-Block formatiert; Test-Anzahl von web_publisher auf 34 korrigiert (war 25, nach iOS-PWA-Commit).
- `PORTIERUNGSPLAN.md` aus dem Git-Tracking entfernt (`git rm --cached`); Datei war trotz `.gitignore`-Eintrag noch getrackt.

### Hinzugefügt / Added (2026-06-10) — iOS PWA-Installierbarkeit
- `web_publisher/icons/apple-touch-icon-180.png` — 180×180 px Icon für iOS-Homescreen (via Pillow LANCZOS aus Icon-192.png)
- `web_publisher/index.html`: `viewport-fit=cover`, `apple-mobile-web-app-title`, `apple-mobile-web-app-status-bar-style`, `<link rel="apple-touch-icon">`, `env(safe-area-inset-*)` CSS auf `body`, 44 px Touch-Targets auf `#search` und `#lang-toggle`
- `web_publisher/sw.js`: `CACHE_NAME` auf `metawiki-v3` gebumpt, `apple-touch-icon-180.png` in ASSETS, `{ignoreSearch: true}` in `caches.match()` für Offline-Stabilität
- `web_publisher/tests/publisher.test.mjs`: 9 neue iOS-Tests (Suite 8) — 34/34 Tests grün
- Manuelles iOS-Smoke-Runbook in `AUFGABEN.txt` (Safari/Chrome → "Zum Home-Bildschirm", Offline, Notch-Viewport, Touch-Targets, Status-Bar)

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

### Behoben / Fixed (2026-06-08)
- `translator.py` `_is_german()`: Umlaut-Erkennung auf echte Unicode-Zeichen (ä, ö, ü, Ä, Ö, Ü, ß) korrigiert; `web_publisher/data/metawiki.json` und `search-index.json` mit korrekten Umlaut-Werten synchronisiert.

### Behoben / Fixed
- Veraltete Clone- und Security-Links aus der früheren persönlichen Ablage ersetzt.
- `cmd_import()` bricht jetzt bei defekter oder unlesbarer `metawiki.json` sauber ab, statt den Import mit unbekanntem Zustand fortzusetzen; Regressionstest für den Load-Fehlerpfad ergänzt.

## [1.0.0] - 2026-02-18

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
