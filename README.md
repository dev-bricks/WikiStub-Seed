![WikiStub-Seed](assets/banner.svg)

# WikiStub-Seed

**EN** | [DE](README_de.md) | [ES](README_es.md) | [JA](README_ja.md) | [RU](README_ru.md) | [ZH](README_zh-Hans.md)

**WikiStub-Seed is a multilingual JSON knowledge framework for AI-assisted research, documentation, learning systems and LLM workflows.** It ships 630 compact knowledge stubs across 12 scientific and cultural domains. Definitions are populated in DE/EN/ES/ZH/JA/RU; relevance notes are populated in DE/ES/ZH/JA/RU and use the documented German fallback for the currently empty English relevance slots.

WikiStub-Seed is a knowledge-stub seed library, not a wiki.

[![WikiStub-Seed smoke tests](https://github.com/dev-bricks/WikiStub-Seed/actions/workflows/tests.yml/badge.svg)](https://github.com/dev-bricks/WikiStub-Seed/actions/workflows/tests.yml)
![Stubs](https://img.shields.io/badge/stubs-630%2B-blue)
![Languages](https://img.shields.io/badge/languages-DE%20%7C%20EN%20%7C%20ES%20%7C%20ZH%20%7C%20JA%20%7C%20RU-orange)
![Format](https://img.shields.io/badge/format-JSON-green)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

## Start Here

| If you want to... | Open this |
|---|---|
| Inspect the dataset | `wikistub_seed.json` |
| Run a quick local check | `python wikistub_seed_cli.py check` |
| Export Markdown for docs or notes | `python wikistub_seed_pipeline.py export --output --english` |
| Understand the exchange format | `EXPORTFORMAT.md` |
| Browse the static PWA source | `web_publisher/` |
| Read the German guide | `README_de.md` |

## Discovery Context

Use the canonical repository name `dev-bricks/WikiStub-Seed` when linking or searching. The project was formerly connected to `file-bricks/MetaWiki`, but the current repo is the dev-bricks knowledge-stub seed library.

Search phrases that describe this project well:

- `WikiStub-Seed JSON knowledge stubs`
- `bilingual JSON knowledge base Python`
- `local-first ontology seed library for LLM workflows`
- `multilingual knowledge stubs framework`
- `RAG knowledge base German English JSON`

## What It Contains

- 630 knowledge stubs in `wikistub_seed.json` with definitions in six languages and relevance notes in five languages
- 12 top-level domains, including mathematics, physics, chemistry, biology, medicine, psychology, AI, engineering, society, economics, history and culture
- 85 subcategories with short, neutral definitions and relevance notes
- Canonical `definitions.{lang}` and `relevance_i18n.{lang}` maps while retaining legacy `definition_de`, `definition_en` and `relevance`
- Python CLI tooling for statistics, validation, consistency checks and Markdown export
- A documented `wikistub-seed-data-v1` export direction for future static Web/PWA use
- No required external dependencies for core import, export, validation or CLI use

## Use Cases

- Seed a local knowledge base for AI-assisted writing or research
- Build documentation glossaries, learning maps or concept catalogs
- Export structured Markdown for Obsidian, GitHub Pages or static sites
- Feed retrieval, embeddings or LLM context pipelines with compact domain stubs
- Translate and extend a domain-neutral knowledge skeleton in a controlled JSON format

## Data Shape

Each stub is intentionally small and machine-readable:

```json
{
  "title": "Domain-Driven Design",
  "definition_de": "Ein Ansatz zur Modellierung komplexer Software, der die Fachdomäne in den Mittelpunkt stellt.",
  "definition_en": "An approach to modeling complex software that places the business domain at the center of development.",
  "relevance": "Hilft, komplexe Systeme verständlich und wartbar zu gestalten.",
  "definitions": {
    "de": "Ein Ansatz zur Modellierung komplexer Software, der die Fachdomäne in den Mittelpunkt stellt.",
    "en": "An approach to modeling complex software that places the business domain at the center of development.",
    "es": "Un enfoque para modelar software complejo que sitúa el dominio de especialidad en el centro.",
    "zh": "一种对复杂软件进行建模的方法，它将专业领域置于中心位置。",
    "ja": "専門領域をその中心に据える、複雑なソフトウェアをモデリングするためのアプローチ。",
    "ru": "Подход к моделированию сложного программного обеспечения, который ставит предметную область в центр внимания."
  },
  "relevance_i18n": {
    "de": "Hilft, komplexe Systeme verständlich und wartbar zu gestalten.",
    "en": "",
    "es": "Ayuda a que los sistemas complejos sean comprensibles y mantenibles.",
    "zh": "有助于使复杂系统更易于理解和维护。",
    "ja": "複雑なシステムを理解しやすく、保守しやすく構築するのに役立ちます。",
    "ru": "Помогает сделать сложные системы понятными и простыми в сопровождении."
  },
  "tags": ["Informatik", "Software Engineering"]
}
```

The current authoritative source is `wikistub_seed.json`. `EXPORTFORMAT.md` documents the stable wrapper format `wikistub-seed-data-v1` for Web/PWA, API and LLM exports.

## Quick Start

```bash
git clone https://github.com/dev-bricks/WikiStub-Seed.git
cd WikiStub-Seed

python wikistub_seed_cli.py --help
python wikistub_seed_cli.py stats
python wikistub_seed_cli.py check
python wikistub_seed_pipeline.py validate
python wikistub_seed_pipeline.py export --output --english
```

On Windows, `start.bat` opens the CLI entry point. Exported files are written to `output/`; that folder is local and not versioned.

## Core Commands

| Command | Purpose |
|---|---|
| `python wikistub_seed_cli.py stats` | Print stub, category and tag statistics |
| `python wikistub_seed_cli.py check` | Run consistency checks over the JSON dataset |
| `python wikistub_seed_pipeline.py validate` | Validate the pipeline input data |
| `python wikistub_seed_pipeline.py export --output --english` | Export the JSON dataset to Markdown |
| `python wikistub_seed_pipeline.py translate` | Optionally translate missing English definitions when configured |

## Repository Map

| Path | Purpose |
|---|---|
| `wikistub_seed.json` | Authoritative multilingual knowledge dataset |
| `01_Mathematik/` ... `12_Kultur_Kunst_Sprache/` | Domain-oriented Markdown source/export structure |
| `wikistub_seed_cli.py` | CLI for stats and checks |
| `wikistub_seed_pipeline.py` | Import, export, validation and optional translation pipeline |
| `md_to_json.py` | Markdown-to-JSON import helper |
| `check_duplicates.py` | Duplicate/consistency helper |
| `EXPORTFORMAT.md` | Stable exchange-format plan |
| `web_publisher/` | Static Web/PWA publisher (offline cache, search, six-language selector) |

## Privacy

WikiStub-Seed is local-first. Core usage reads and writes local JSON/Markdown files only. There is no telemetry and no automatic network communication.

The optional translation command can call an external API only when `ANTHROPIC_API_KEY` is set and the optional `anthropic` package is installed.

## Roadmap

Completed:

- 12 top-level domains and 85 subcategories
- 630 multilingual stubs in a single JSON master file
- Markdown export and JSON synchronization tooling
- CLI smoke tests in GitHub Actions, plus dedicated macOS/Linux source smokes for `wikistub_seed_cli.py check` and `wikistub_seed_pipeline.py validate`
- Static Web/PWA publisher with search and offline cache (`web_publisher/`)
- `wikistub-seed-data-v1` schema wrapper with DE/EN/ES/ZH/JA/RU language maps

Planned:

- Unified tag cleanup
- Obsidian/GitHub Pages export paths
- Optional embeddings and search API

## Deutsch

**WikiStub-Seed ist ein mehrsprachiges JSON-Wissensgerüst für KI-gestützte Wissensarbeit.** Das Repository enthält 630 kompakte Wissens-Stubs mit Definitionen in Deutsch, Englisch, Spanisch, Chinesisch, Japanisch und Russisch. Relevanztexte liegen in allen diesen Sprachen außer Englisch vor; dort greift der dokumentierte deutsche Fallback.

WikiStub-Seed arbeitet standardmäßig lokal mit `wikistub_seed.json`. Die Kernfunktionen benötigen keine externen Pakete. Nur die optionale Übersetzungsfunktion nutzt externe API-Aufrufe, wenn ein API-Key gesetzt und das optionale Paket installiert wurde.

Wichtige Einstiegspunkte:

- `python wikistub_seed_cli.py stats` zeigt Statistik und Kategorien.
- `python wikistub_seed_cli.py check` prüft den Datenbestand.
- `python wikistub_seed_pipeline.py export --output --english` exportiert Markdown.
- `EXPORTFORMAT.md` beschreibt den geplanten stabilen Austauschstandard.
- `web_publisher/` enthält den fertigen statischen Web/PWA-Publisher mit Offline-Cache und Sechs-Sprachen-Auswahl.

## License

MIT License. See `LICENSE`.

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence under Section 521 of the German Civil Code, with the MIT License disclaimers applying as well. Use at your own risk.
