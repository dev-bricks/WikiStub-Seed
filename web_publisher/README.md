# WikiStub-Seed Web/PWA Publisher

Stand: 2026-07-15

Dieser Ordner enthält den statischen, serverlosen Web-/PWA-Reader für den maßgeblichen Datensatz `../wikistub_seed.json`.

## Funktionen

- Kategoriebaum, Volltextsuche und Stub-Detailansicht für 630 Einträge.
- Sprachauswahl für Deutsch, Englisch, Spanisch, Chinesisch, Japanisch und Russisch.
- Offline-Cache über einen Service Worker; veränderliche Datendateien werden online zuerst aktualisiert und offline aus dem Cache gelesen.
- Stabile, inhaltsbezogene Deep-Link-IDs statt positionsabhängiger Nummern.
- Keine Konten, Telemetrie, Serverpflicht oder automatische externe API-Kommunikation.

Definitionen sind im Masterdatensatz in allen sechs Sprachen gefüllt. Relevanztexte sind in DE/ES/ZH/JA/RU gefüllt; für die leeren englischen Relevanzslots verwendet der Reader die gemeinsame Fallback-Kette.

## Reproduzierbarer Build

Aus dem Repository-Root:

```bash
python web_publisher/_build.py
node --test web_publisher/tests/publisher.test.mjs
git diff --exit-code -- web_publisher/data
```

`_build.py` validiert die Grundstruktur, normalisiert die Sprachmaps und schreibt `data/wikistub_seed.json` sowie `data/search-index.json` atomar. IDs werden deterministisch aus Kategorie, Subkategorie und Titel abgeleitet; ein wiederholter Build erzeugt dieselben Dateien.

## Hosting und lokaler Smoke

Die Dateien müssen über HTTP(S) bereitgestellt werden, damit Fetch und Service Worker funktionieren. Für einen lokalen Smoke genügt beispielsweise:

```bash
python -m http.server 8000 --directory web_publisher
```

Danach `http://localhost:8000/` öffnen. GitHub Pages oder jeder andere statische Host kann denselben Ordner ausliefern.

## Grenzen

- Kein nativer Android-, iOS- oder Desktop-Clone.
- Keine zweite Datenquelle neben `wikistub_seed.json`.
- Ein echter Browser-/Geräte-Smoke für Installation, Offline-Start und Deep Links bleibt manuell und ist in `../TODO.md` vermerkt.
