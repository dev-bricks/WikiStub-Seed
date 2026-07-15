# WikiStub-Seed Export Format

Stand: 2026-06-14

## Schema

`wikistub-seed-data-v1` ist die stabile Austauschhülle für WikiStub-Seed-Daten. Die Hülle bleibt abwärtskompatibel zu den bisherigen Feldern `definition_de`, `definition_en` und `relevance`, enthält aber zusätzlich ein explizites Sprachmodell.

```json
{
  "schema": "wikistub-seed-data-v1",
  "generated_at": "2026-06-14T12:00:00Z",
  "source": "wikistub_seed.json",
  "languages": ["de", "en", "es", "zh", "ja", "ru"],
  "language_model": {
    "version": 1,
    "default_language": "de",
    "required_languages": ["de", "en"],
    "fallback_chain": ["de", "en"]
  },
  "stub_count": 630,
  "data": {
    "MetaWiki": {}
  }
}
```

## Stub-Felder

Jeder Stub führt die alten Felder weiter und hat zusätzlich kanonische Sprachmaps:

```json
{
  "title": "Domain-Driven Design",
  "definition_de": "Ein Ansatz zur Modellierung komplexer Software.",
  "definition_en": "An approach to modelling complex software.",
  "relevance": "Hilft bei der Strukturierung großer Systeme.",
  "definitions": {
    "de": "Ein Ansatz zur Modellierung komplexer Software.",
    "en": "An approach to modelling complex software.",
    "es": "",
    "zh": "",
    "ja": "",
    "ru": ""
  },
  "relevance_i18n": {
    "de": "Hilft bei der Strukturierung großer Systeme.",
    "en": "",
    "es": "",
    "zh": "",
    "ja": "",
    "ru": ""
  },
  "tags": ["Informatik", "Software Engineering"]
}
```

## Regeln

- `definitions.{lang}` ist das kanonische Feld für Definitionen.
- `relevance_i18n.{lang}` ist das kanonische Feld für Relevanztexte.
- `definition_de`, `definition_en` und `relevance` bleiben Legacy-Kompatibilitätsfelder.
- `de` und `en` bleiben Pflichtsprachen im Modell. Der aktuelle Datensatz füllt Definitionen zusätzlich für `es`, `zh`, `ja` und `ru`; Relevanztexte sind in `de`, `es`, `zh`, `ja` und `ru` gefüllt.
- Browser, CLI und Pipeline verwenden die Fallback-Kette `gewählte Sprache -> de -> en -> irgendein vorhandener Text`.
- Fehlende Zusatzsprachen bleiben leer, bis ein kuratierter Übersetzungsworkflow abgeschlossen ist.

## Befehle

```bash
python wikistub_seed_pipeline.py export-data
python wikistub_seed_pipeline.py validate --exchange output/wikistub-seed-data-v1.json -v
python web_publisher/_build.py
```
