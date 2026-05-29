# MetaWiki

**MetaWiki is a bilingual JSON knowledge framework for AI-assisted research, documentation, learning systems and LLM workflows.** It ships a curated `metawiki.json` dataset with 630 compact German/English knowledge stubs across 12 scientific and cultural domains, plus Python tools for validation, export and translation.

MetaWiki is not Wikimedia Meta-Wiki. It is a local-first, repository-based knowledge skeleton: a small ontology-style seed library that can be reused in software projects, research notes, documentation systems, Obsidian exports, static websites or retrieval-augmented generation pipelines.

[![MetaWiki smoke tests](https://github.com/file-bricks/MetaWiki/actions/workflows/tests.yml/badge.svg)](https://github.com/file-bricks/MetaWiki/actions/workflows/tests.yml)
![Stubs](https://img.shields.io/badge/stubs-630%2B-blue)
![Languages](https://img.shields.io/badge/languages-DE%20%7C%20EN-orange)
![Format](https://img.shields.io/badge/format-JSON-green)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

## What It Contains

- 630 bilingual knowledge stubs in `metawiki.json`
- 12 top-level domains, including mathematics, physics, chemistry, biology, medicine, psychology, AI, engineering, society, economics, history and culture
- 85 subcategories with short, neutral definitions and relevance notes
- Python CLI tooling for statistics, validation, consistency checks and Markdown export
- A documented `metawiki-data-v1` export direction for future static Web/PWA use
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
  "tags": ["Informatik", "Software Engineering"]
}
```

The current authoritative source is `metawiki.json`. `EXPORTFORMAT.md` documents the planned stable wrapper format `metawiki-data-v1` for future Web/PWA, API and LLM exports.

## Quick Start

```bash
git clone https://github.com/file-bricks/MetaWiki.git
cd MetaWiki

python metawiki_cli.py --help
python metawiki_cli.py stats
python metawiki_cli.py check
python metawiki_pipeline.py validate
python metawiki_pipeline.py export --output --english
```

On Windows, `start.bat` opens the CLI entry point. Exported files are written to `output/`; that folder is local and not versioned.

## Core Commands

| Command | Purpose |
|---|---|
| `python metawiki_cli.py stats` | Print stub, category and tag statistics |
| `python metawiki_cli.py check` | Run consistency checks over the JSON dataset |
| `python metawiki_pipeline.py validate` | Validate the pipeline input data |
| `python metawiki_pipeline.py export --output --english` | Export the JSON dataset to Markdown |
| `python metawiki_pipeline.py translate` | Optionally translate missing English definitions when configured |

## Repository Map

| Path | Purpose |
|---|---|
| `metawiki.json` | Authoritative bilingual knowledge dataset |
| `01_Mathematik/` ... `12_Kultur_Kunst_Sprache/` | Domain-oriented Markdown source/export structure |
| `metawiki_cli.py` | CLI for stats and checks |
| `metawiki_pipeline.py` | Import, export, validation and optional translation pipeline |
| `md_to_json.py` | Markdown-to-JSON import helper |
| `check_duplicates.py` | Duplicate/consistency helper |
| `EXPORTFORMAT.md` | Stable exchange-format plan |
| `web_publisher/README.md` | Static Web/PWA publisher plan |

## Privacy

MetaWiki is local-first. Core usage reads and writes local JSON/Markdown files only. There is no telemetry and no automatic network communication.

The optional translation command can call an external API only when `ANTHROPIC_API_KEY` is set and the optional `anthropic` package is installed.

## Roadmap

Completed:

- 12 top-level domains and 85 subcategories
- 630 bilingual stubs in a single JSON master file
- Markdown export and JSON synchronization tooling
- CLI smoke tests in GitHub Actions

Planned:

- `metawiki-data-v1` schema wrapper and validation
- Unified tag cleanup
- Static Web/PWA publisher with search and offline cache
- Obsidian/GitHub Pages export paths
- Optional embeddings and search API

## Deutsch

**MetaWiki ist ein zweisprachiges JSON-Wissensgerüst für KI-gestützte Wissensarbeit.** Das Repository enthält 630 kompakte Wissens-Stubs auf Deutsch und Englisch, verteilt auf 12 Wissenschafts- und Kulturbereiche. Die Stubs sind kurz, neutral, versionierbar und für Automatisierung, Dokumentation, Lernsysteme und LLM-Kontexte geeignet.

MetaWiki arbeitet standardmäßig lokal mit `metawiki.json`. Die Kernfunktionen benötigen keine externen Pakete. Nur die optionale Übersetzungsfunktion nutzt externe API-Aufrufe, wenn ein API-Key gesetzt und das optionale Paket installiert wurde.

Wichtige Einstiegspunkte:

- `python metawiki_cli.py stats` zeigt Statistik und Kategorien.
- `python metawiki_cli.py check` prüft den Datenbestand.
- `python metawiki_pipeline.py export --output --english` exportiert Markdown.
- `EXPORTFORMAT.md` beschreibt den geplanten stabilen Austauschstandard.
- `web_publisher/README.md` beschreibt den geplanten statischen Web/PWA-Pfad.

## License

MIT License. See `LICENSE`.

This project is an unpaid open-source donation. Liability is limited to intent and gross negligence under Section 521 of the German Civil Code, with the MIT License disclaimers applying as well. Use at your own risk.
