# Beitragsrichtlinie / Contributing Guide

## Deutsch

Danke, dass du zu WikiStub-Seed beitragen möchtest.

### Beiträge und Pull Requests

1. Melde Fehler oder schlage Funktionen über GitHub Issues vor.
2. Arbeite in einem eigenen Branch und beschreibe im Pull Request die beobachtete Änderung.
3. Führe die passenden lokalen Prüfungen aus und nenne übersprungene optionale Abhängigkeiten oder Plattformgrenzen offen.
4. Behalte die eingefrorene Paketversion `1.1.12` bei. Nicht veröffentlichte Änderungen gehören unter `## [Unreleased]` in `CHANGELOG.md`.

### Prüfungen

```bash
python -m pytest
node --test web_publisher/tests/publisher.test.mjs
ruff check .
python -m compileall -q .
python wikistub_seed_cli.py stats
python wikistub_seed_cli.py check
python wikistub_seed_pipeline.py validate
python web_publisher/_build.py
git diff --exit-code -- web_publisher/data
```

Die Python-Testmatrix läuft in GitHub Actions auf Ubuntu und Windows mit Python 3.10 bis 3.13. Ein separater Python-3.11-Source-Smoke läuft auf Ubuntu und macOS; die PWA-Tests laufen auf Ubuntu mit Node.js. Das belegt keine vollständige Verhaltensparität auf allen Betriebssystemen.

### Daten, Netzwerk und Paketgrenzen

Die vollständige CLI-, Editor-, Dataset- und PWA-Anwendung wird aus einem Source-Checkout verwendet. Das Python-Wheel enthält nur sechs wiederverwendbare API-Module; es enthält weder CLI, Editor, Dataset noch PWA. Installierte API-Aufrufe benötigen ausdrücklich ausgewählte externe Daten- und Authentifizierungspfade und verwenden `site-packages` nicht als Nutzerdatenspeicher.

Der lokale Kern bearbeitet ausgewählte Dateien. Die optionale Übersetzung über die CLI sendet den ausgewählten Text und die Übersetzungsanweisungen an Anthropic. Dafür verlangt die CLI `ANTHROPIC_API_KEY`, das optionale SDK, `--confirm-api-cost` und eine positive `--max-budget-usd`-Grenze. Die Modul-APIs `translate_text` und `translate_batch` verlangen stattdessen ein explizites `max_budget_usd`; das CLI-Bestätigungsflag gilt dort nicht. Die lokale Kostenschätzung ist keine Garantie für die Providerabrechnung. Tests dürfen keine echten Provider, Schlüssel, Nutzerprofile oder Datenbanken kontaktieren.

### Arbeitsweise

- Quell- und Dokumentationsdateien werden als UTF-8 gespeichert. Deutsche Texte verwenden echte Umlaute.
- Datenpfade und Authentifizierungsdateien bleiben außerhalb installierter Paketverzeichnisse.
- Quelländerungen werden durch passende Regressionstests belegt; Dokumentationsänderungen brauchen keine Tests, die lediglich denselben Wortlaut spiegeln.

---

## English

Thank you for contributing to WikiStub-Seed.

### Contributions and Pull Requests

1. Report bugs or propose features through GitHub Issues.
2. Work on your own branch and describe the observed behavior in the pull request.
3. Run the relevant checks and report optional dependency or platform limitations accurately.
4. Keep the frozen package version at `1.1.12`. Record unreleased changes under `## [Unreleased]` in `CHANGELOG.md`.

### Checks

```bash
python -m pytest
node --test web_publisher/tests/publisher.test.mjs
ruff check .
python -m compileall -q .
python wikistub_seed_cli.py stats
python wikistub_seed_cli.py check
python wikistub_seed_pipeline.py validate
python web_publisher/_build.py
git diff --exit-code -- web_publisher/data
```

The Python test matrix runs on Ubuntu and Windows with Python 3.10 through 3.13. A separate Python 3.11 source smoke runs on Ubuntu and macOS; PWA tests run on Ubuntu with Node.js. This does not establish full behavioral parity on every operating system.

### Data, Network, and Packaging Boundaries

Use a source checkout for the full CLI, editor, dataset, and PWA application. The Python wheel contains only six reusable API modules; it does not include the CLI, editor, dataset, or PWA. Installed API calls require explicitly selected external data and authentication paths and must not use `site-packages` as user-data storage.

The local core works with selected files. Optional translation through the CLI sends the selected text and instructions to Anthropic. The CLI requires `ANTHROPIC_API_KEY`, the optional SDK, `--confirm-api-cost`, and a positive `--max-budget-usd` ceiling. The module APIs `translate_text` and `translate_batch` instead require an explicit `max_budget_usd`; the CLI confirmation flag does not apply there. The local cost estimate is not a guarantee of provider billing. Tests must not contact real providers or use real keys, user profiles, or databases.

### Working Practices

- Store source and documentation as UTF-8; German text uses actual umlauts.
- Keep data paths and authentication files outside installed package directories.
- Use regression tests for source behavior; documentation tests should not simply mirror prose.
