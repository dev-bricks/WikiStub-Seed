# Portierungsplan - MetaWiki Framework

Stand: 2026-05-27
Automation: SOFTWARE STRANGE NEW WORLDS

## Kurzentscheidung

MetaWiki bleibt zuerst ein öffentliches GitHub-/CLI-/JSON-Projekt. Die sinnvolle plattformübergreifende Linie ist keine native Desktop- oder Mobile-App, sondern ein statischer Web/PWA-Publisher auf Basis von `metawiki.json`: durchsuchbar, offlinefähig, mobil gut lesbar und als GitHub Pages oder anderes statisches Hosting auslieferbar.

Native Android-, iOS-, Windows-Store-, macOS- und Linux-Apps sind erst sinnvoll, wenn der geplante Web-Viewer oder eine Such-API produktiv genutzt wird und eine Store-Hülle echten Zusatznutzen bringt.

## Ausgangslage

- Status: `REL-PUB`, öffentliches SOCIAL-Projekt.
- Kern: `metawiki.json` mit ca. 630 zweisprachigen Wissens-Stubs.
- Bedienung: CLI- und Pipeline-Skripte (`metawiki_cli.py`, `metawiki_pipeline.py`, `md_to_json.py`, `check_duplicates.py`).
- Plattformbasis: Python 3.10+, Kernfunktionen ohne externe Pflichtabhängigkeiten.
- Datenschutz: lokal, keine Telemetrie; nur optionale Übersetzung nutzt externe API bei gesetztem `ANTHROPIC_API_KEY`.
- Bestehende Roadmap: JSON-Schema, Tag-System, Obsidian/GitHub-Pages-Export, Embeddings, REST-Such-API und Web-Interface.

## Plattformbewertung

| Option | Entscheidung | Begründung |
|---|---|---|
| Windows Store | Vorerst kein Ziel | MetaWiki ist aktuell ein CLI-/Datenprojekt ohne GUI. Ein Store-Paket wäre für Normalnutzer erst nach Web-Viewer oder lokaler Suchoberfläche sinnvoll. |
| Android | Web/PWA statt native App | Der mobile Nutzen liegt im Nachschlagen, Suchen und Teilen von Stubs. Das kann eine PWA mit Offline-Cache besser und günstiger leisten als ein nativer Clone. |
| Webapp / PWA | Primärer Plattformpfad | Passt zu GitHub Pages, mobilen Browsern, Desktop-Browsern und LLM-Nutzung. Ein statischer Build aus `metawiki.json` vermeidet Serverbetrieb und hält Datenschutzrisiken klein. |
| iOS | Web/PWA statt native App | Installation über "Zum Home-Bildschirm" reicht für Nachschlagen und Offline-Lesen. App-Store-Aufwand lohnt erst bei aktiver Bearbeitung, Sync oder Accounts. |
| Mac App | Nicht kurzfristig | Python-CLI läuft grundsätzlich auf macOS. Eine signierte App-Hülle wird erst relevant, wenn eine lokale GUI oder ein Desktop-Webviewer existiert. |
| Linux Version | Source-/CLI-Smoke | Linux ist für CLI und JSON-Pipeline naheliegend. Ein AppImage/Flatpak wäre erst bei GUI oder Webviewer mit Desktop-Starter sinnvoll. |

## Zielarchitektur

1. `metawiki.json` bleibt die autoritative Datenquelle.
2. `EXPORTFORMAT.md` dokumentiert ein stabiles Austauschformat `metawiki-data-v1`.
3. `web_publisher/` beschreibt den geplanten statischen Web/PWA-Pfad.
4. Der erste plattformübergreifende Build erzeugt HTML, Suchindex und Manifest aus `metawiki.json`.
5. Mobile Nutzung erfolgt über dieselbe Web/PWA-Oberfläche für Android, iOS und Desktop-Browser.
6. Native Hüllen bleiben optional: nur wenn Web/PWA-Nutzung tatsächliche Nachfrage erzeugt.

## Umsetzungsstatus

| Bereich | Status | Nächster Schritt |
|---|---|---|
| GitHub/CLI | Vorhanden | CLI-Smoke in CI beibehalten und bei Release dokumentieren. |
| Datenformat | Geplant und dokumentiert | `EXPORTFORMAT.md` als stabile Referenz nutzen und später JSON-Schema ergänzen. |
| Web/PWA | Geplant | Statischen Publisher mit Suchindex und Offline-Manifest entwerfen. |
| Android/iOS | Abgeleitet über PWA | Erst nach Web/PWA-Smoke auf echten mobilen Viewports bewerten. |
| Windows Store | Kein aktiver Kanal | Nur neu prüfen, wenn eine GUI oder lokale Webviewer-Hülle entsteht. |
| macOS/Linux | Source-Smoke | Python-CLI auf macOS/Linux prüfen, bevor Pakete geplant werden. |

## Risiken und Leitplanken

- Kein Upload sensibler Nutzerinhalte: Der Web/PWA-Publisher arbeitet mit dem öffentlichen MetaWiki-Datensatz oder lokalen Dateien.
- Keine parallele Datenquelle: Markdown-Exports, Web-Index und PWA-Daten werden aus `metawiki.json` generiert.
- Kein voreiliger App-Store-Aufwand: Native Apps werden nur gestartet, wenn Web/PWA-Nutzung einen klaren Mehrwert oder Nachfrage zeigt.
- Such- und Embedding-Funktionen müssen optional bleiben, damit die statische, datenschutzarme Basis erhalten bleibt.

## Nächste Aufgaben

Die konkreten Aufgaben stehen in `AUFGABEN.txt`. Priorität hat der kleine Web/PWA-Publisher mit stabiler Exporthülle, nicht ein nativer App-Neubau.
