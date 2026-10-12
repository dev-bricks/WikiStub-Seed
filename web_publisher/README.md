# WikiStub-Seed Web/PWA Publisher

Stand: 2026-07-15

Dieser Ordner enthält den statischen, serverlosen Web-/PWA-Reader für den maßgeblichen Datensatz `../wikistub_seed.json`.

## Funktionen

- Kategoriebaum, Volltextsuche und Stub-Detailansicht für 630 Einträge.
- Sprachauswahl für Deutsch, Englisch, Spanisch, Chinesisch, Japanisch und Russisch.
- Der Service Worker lädt veränderliche Datendateien zuerst aus dem Netzwerk und kann erfolgreiche Antworten für einen Offline-Fallback zwischenspeichern. Erstaufruf und Aktualisierungen benötigen Zugriff auf den Host; Cache-Verfügbarkeit hängt von Browser und Host ab.
- Stabile, inhaltsbezogene Deep-Link-IDs statt positionsabhängiger Nummern.
- Kein Backend, Konto oder Telemetriedienst ist Teil der statischen PWA. Der ausgewählte statische Host liefert App, Ressourcen und Datensatz; die PWA ruft keine externe API auf.

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

## Lokaler Edit-Modus

Diese Kombination aus `python -m http.server`/GitHub Pages liest nur — sie kann nicht schreiben. Für GUI-Editing (Artikel/Kategorien anlegen, bearbeiten, löschen) `python edit_server.py` (Repository-Root) statt eines einfachen HTTP-Servers starten: liefert dieselben Dateien aus diesem Ordner UND eine `/api/`-JSON-Schnittstelle fürs Schreiben, ausschließlich an `127.0.0.1` gebunden. Details, Rechtemodell und Sicherheitshinweise: `../README.md`/`../README_de.md`, Abschnitt „Lokaler Edit-Modus". Ohne laufenden `edit_server.py` (also z. B. auf GitHub Pages) zeigt die Seite automatisch einen Lesemodus-Hinweis und blendet alle Bearbeiten-Bedienelemente aus.

## Grenzen

- Kein nativer Android-, iOS- oder Desktop-Clone.
- Keine zweite Datenquelle neben `wikistub_seed.json`.
- Ein echter Browser-/Geräte-Smoke für Installation, Offline-Start und Deep Links bleibt manuell und ist in `../TODO.md` vermerkt.
