# WikiStub-Seed

[EN](README.md) | **DE** | [ES](README_es.md) | [JA](README_ja.md) | [RU](README_ru.md) | [ZH](README_zh-Hans.md)

**WikiStub-Seed ist ein mehrsprachig vorbereitetes JSON-Wissensgerüst für KI-gestützte Forschung, Dokumentation, Lernsysteme und LLM-Workflows.** Es enthält einen kuratierten `wikistub_seed.json`-Datensatz mit 630 kompakten Deutsch/Englisch-Wissens-Stubs über 12 Wissenschafts- und Kulturbereiche, vorbereiteten ES/ZH/JA/RU-Sprachslots sowie Python-Werkzeugen für Validierung, Export und Übersetzung.

WikiStub-Seed ist eine Wissens-Stub-Seed-Bibliothek, kein Wiki.

[![WikiStub-Seed smoke tests](https://github.com/file-bricks/WikiStub-Seed/actions/workflows/tests.yml/badge.svg)](https://github.com/file-bricks/WikiStub-Seed/actions/workflows/tests.yml)
![Stubs](https://img.shields.io/badge/stubs-630%2B-blue)
![Languages](https://img.shields.io/badge/languages-DE%20%7C%20EN%20%7C%20ES%20%7C%20ZH%20%7C%20JA%20%7C%20RU-orange)
![Format](https://img.shields.io/badge/format-JSON-green)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

## Inhalt

- 630 Wissens-Stubs in `wikistub_seed.json` mit DE/EN-Inhalten und vorbereiteten ES/ZH/JA/RU-Sprachslots
- 12 Oberbereiche, darunter Mathematik, Physik, Chemie, Biologie, Medizin, Psychologie, KI, Ingenieurwesen, Gesellschaft, Wirtschaft, Geschichte und Kultur
- 85 Unterkategorien mit kurzen, neutralen Definitionen und Relevanzhinweisen
- Kanonische `definitions.{lang}`- und `relevance_i18n.{lang}`-Zuordnungen unter Beibehaltung der Legacy-Felder `definition_de`, `definition_en` und `relevance`
- Python-CLI-Werkzeuge für Statistiken, Validierung, Konsistenzprüfungen und Markdown-Export
- Eine dokumentierte `wikistub-seed-data-v1`-Exportrichtung für zukünftige statische Web-/PWA-Nutzung
- Keine externen Abhängigkeiten für den Kern-Import, -Export, die Validierung oder CLI-Nutzung erforderlich

## Anwendungsfälle

- Lokale Wissensbasis für KI-gestütztes Schreiben oder Recherchieren anlegen
- Dokumentationsglossare, Lernkarten oder Konzeptkataloge erstellen
- Strukturiertes Markdown für Obsidian, GitHub Pages oder statische Websites exportieren
- Retrieval-, Embedding- oder LLM-Kontext-Pipelines mit kompakten Domänen-Stubs befüllen
- Ein domänenneutrales Wissensgerüst in einem kontrollierten JSON-Format übersetzen und erweitern

## Datenstruktur

Jeder Stub ist bewusst klein und maschinenlesbar gehalten:

```json
{
  "title": "Domain-Driven Design",
  "definition_de": "Ein Ansatz zur Modellierung komplexer Software, der die Fachdomäne in den Mittelpunkt stellt.",
  "definition_en": "An approach to modeling complex software that places the business domain at the center of development.",
  "relevance": "Hilft, komplexe Systeme verständlich und wartbar zu gestalten.",
  "definitions": {
    "de": "Ein Ansatz zur Modellierung komplexer Software, der die Fachdomäne in den Mittelpunkt stellt.",
    "en": "An approach to modeling complex software that places the business domain at the center of development.",
    "es": "",
    "zh": "",
    "ja": "",
    "ru": ""
  },
  "relevance_i18n": {
    "de": "Hilft, komplexe Systeme verständlich und wartbar zu gestalten.",
    "en": "",
    "es": "",
    "zh": "",
    "ja": "",
    "ru": ""
  },
  "tags": ["Informatik", "Software Engineering"]
}
```

Die aktuelle maßgebliche Quelle ist `wikistub_seed.json`. `EXPORTFORMAT.md` dokumentiert das stabile Wrapper-Format `wikistub-seed-data-v1` für Web-/PWA-, API- und LLM-Exporte.

## Schnellstart

```bash
git clone https://github.com/file-bricks/WikiStub-Seed.git
cd WikiStub-Seed

python wikistub_seed_cli.py --help
python wikistub_seed_cli.py stats
python wikistub_seed_cli.py check
python wikistub_seed_pipeline.py validate
python wikistub_seed_pipeline.py export --output --english
```

Unter Windows öffnet `start.bat` den CLI-Einstiegspunkt. Exportierte Dateien werden in `output/` abgelegt; dieser Ordner ist lokal und nicht versioniert.

## Kernbefehle

| Befehl | Zweck |
|---|---|
| `python wikistub_seed_cli.py stats` | Stub-, Kategorie- und Tag-Statistiken ausgeben |
| `python wikistub_seed_cli.py check` | Konsistenzprüfungen über den JSON-Datensatz ausführen |
| `python wikistub_seed_pipeline.py validate` | Pipeline-Eingabedaten validieren |
| `python wikistub_seed_pipeline.py export --output --english` | JSON-Datensatz als Markdown exportieren |
| `python wikistub_seed_pipeline.py translate` | Optional fehlende englische Definitionen übersetzen, wenn konfiguriert |

## Repository-Überblick

| Pfad | Zweck |
|---|---|
| `wikistub_seed.json` | Maßgeblicher zweisprachiger Wissensdatensatz |
| `01_Mathematik/` ... `12_Kultur_Kunst_Sprache/` | Domänenorientierte Markdown-Quell-/Exportstruktur |
| `wikistub_seed_cli.py` | CLI für Statistiken und Prüfungen |
| `wikistub_seed_pipeline.py` | Import-, Export-, Validierungs- und optionale Übersetzungs-Pipeline |
| `md_to_json.py` | Markdown-zu-JSON-Import-Hilfsprogramm |
| `check_duplicates.py` | Duplikat-/Konsistenz-Hilfsprogramm |
| `EXPORTFORMAT.md` | Stabiler Austauschformat-Plan |
| `web_publisher/` | Statischer Web-/PWA-Publisher (PWA, Offline-Cache, Suche, DE/EN-Umschalter) |

## Datenschutz

WikiStub-Seed arbeitet standardmäßig lokal. Der Kernbetrieb liest und schreibt ausschließlich lokale JSON-/Markdown-Dateien. Es gibt keine Telemetrie und keine automatische Netzwerkkommunikation.

Der optionale Übersetzungsbefehl kann eine externe API aufrufen, wenn `ANTHROPIC_API_KEY` gesetzt und das optionale Paket `anthropic` installiert ist.

## Roadmap

Abgeschlossen:

- 12 Oberbereiche und 85 Unterkategorien
- 630 zweisprachige Stubs in einer einzigen JSON-Hauptdatei
- Markdown-Export- und JSON-Synchronisierungswerkzeuge
- CLI-Smoke-Tests in GitHub Actions sowie dedizierte macOS/Linux-Quell-Smokes für `wikistub_seed_cli.py check` und `wikistub_seed_pipeline.py validate`
- Statischer Web-/PWA-Publisher mit Suche und Offline-Cache (`web_publisher/`)
- `wikistub-seed-data-v1`-Schema-Wrapper mit vorbereiteten DE/EN/ES/ZH/JA/RU-Sprachslots

Geplant:

- Einheitliche Tag-Bereinigung
- Obsidian-/GitHub-Pages-Exportpfade
- Optionale Embeddings und Such-API

## Deutsch

**WikiStub-Seed ist ein mehrsprachig vorbereitetes JSON-Wissensgerüst für KI-gestützte Wissensarbeit.** Das Repository enthält 630 kompakte Wissens-Stubs mit Deutsch/Englisch-Inhalten und vorbereiteten Sprachslots für Spanisch, Chinesisch, Japanisch und Russisch, verteilt auf 12 Wissenschafts- und Kulturbereiche. Die Stubs sind kurz, neutral, versionierbar und für Automatisierung, Dokumentation, Lernsysteme und LLM-Kontexte geeignet.

WikiStub-Seed arbeitet standardmäßig lokal mit `wikistub_seed.json`. Die Kernfunktionen benötigen keine externen Pakete. Nur die optionale Übersetzungsfunktion nutzt externe API-Aufrufe, wenn ein API-Key gesetzt und das optionale Paket installiert wurde.

Wichtige Einstiegspunkte:

- `python wikistub_seed_cli.py stats` zeigt Statistik und Kategorien.
- `python wikistub_seed_cli.py check` prüft den Datenbestand.
- `python wikistub_seed_pipeline.py export --output --english` exportiert Markdown.
- `EXPORTFORMAT.md` beschreibt den geplanten stabilen Austauschstandard.
- `web_publisher/` enthält den fertigen statischen Web/PWA-Publisher mit Offline-Cache und DE/EN-Toggle.

## Lizenz

MIT-Lizenz. Siehe `LICENSE`.

Dieses Projekt ist eine unentgeltliche Open-Source-Spende. Die Haftung ist gemäß § 521 BGB auf Vorsatz und grobe Fahrlässigkeit beschränkt; die Haftungsausschlüsse der MIT-Lizenz gelten ebenfalls. Nutzung auf eigene Gefahr.
