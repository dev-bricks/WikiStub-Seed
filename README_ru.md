![WikiStub-Seed](assets/banner.svg)

# WikiStub-Seed

[EN](README.md) | [DE](README_de.md) | [ES](README_es.md) | [JA](README_ja.md) | **RU** | [ZH](README_zh-Hans.md)

**WikiStub-Seed — это многоязычный JSON-фреймворк знаний.** В нём 630 статей в 12 областях: определения заполнены на DE/EN/ES/ZH/JA/RU, а пояснения значимости — на DE/ES/ZH/JA/RU с немецким fallback для пустых английских слотов.

WikiStub-Seed — это начальная библиотека заглушек знаний, не вики.

[![WikiStub-Seed smoke tests](https://github.com/dev-bricks/WikiStub-Seed/actions/workflows/tests.yml/badge.svg)](https://github.com/dev-bricks/WikiStub-Seed/actions/workflows/tests.yml)
![Stubs](https://img.shields.io/badge/stubs-630%2B-blue)
![Languages](https://img.shields.io/badge/languages-DE%20%7C%20EN%20%7C%20ES%20%7C%20ZH%20%7C%20JA%20%7C%20RU-orange)
![Format](https://img.shields.io/badge/format-JSON-green)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

## Содержимое

- 630 статей в `wikistub_seed.json` с определениями на шести языках
- 12 предметных областей верхнего уровня, включая математику, физику, химию, биологию, медицину, психологию, ИИ, инженерию, общество, экономику, историю и культуру
- 85 подкатегорий с краткими нейтральными определениями и заметками о релевантности
- Канонические карты `definitions.{lang}` и `relevance_i18n.{lang}` при сохранении устаревших полей `definition_de`, `definition_en` и `relevance`
- Инструменты CLI на Python для статистики, валидации, проверок согласованности и экспорта в Markdown
- Документированное направление экспорта `wikistub-seed-data-v1` для будущего использования на статических веб-сайтах/PWA
- Для базового импорта, экспорта, валидации или использования CLI внешние зависимости не требуются

## Варианты использования

- Создание локальной базы знаний для написания текстов или исследований с поддержкой ИИ
- Построение глоссариев документации, карт обучения или каталогов концепций
- Экспорт структурированного Markdown для Obsidian, GitHub Pages или статических сайтов
- Наполнение конвейеров поиска, встраивания или контекста LLM компактными заглушками предметной области
- Перевод и расширение доменно-нейтрального скелета знаний в контролируемом формате JSON

## Структура данных

Каждая заглушка намеренно сделана небольшой и машиночитаемой:

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

Текущим авторитетным источником является `wikistub_seed.json`. `EXPORTFORMAT.md` документирует стабильный формат-обёртку `wikistub-seed-data-v1` для веб-/PWA-, API- и LLM-экспортов.

## Быстрый старт

```bash
git clone https://github.com/dev-bricks/WikiStub-Seed.git
cd WikiStub-Seed

python wikistub_seed_cli.py --help
python wikistub_seed_cli.py stats
python wikistub_seed_cli.py check
python wikistub_seed_pipeline.py validate
python wikistub_seed_pipeline.py export --output --english
```

В Windows `start.bat` открывает точку входа CLI. Экспортированные файлы записываются в `output/`; эта папка является локальной и не версионируется.

## Основные команды

| Команда | Назначение |
|---|---|
| `python wikistub_seed_cli.py stats` | Вывод статистики по заглушкам, категориям и тегам |
| `python wikistub_seed_cli.py check` | Запуск проверок согласованности набора данных JSON |
| `python wikistub_seed_pipeline.py validate` | Валидация входных данных конвейера |
| `python wikistub_seed_pipeline.py export --output --english` | Экспорт набора данных JSON в Markdown |
| `python wikistub_seed_pipeline.py translate` | Опциональный перевод отсутствующих английских определений при наличии настроек |

## Карта репозитория

| Путь | Назначение |
|---|---|
| `wikistub_seed.json` | Авторитетный двуязычный набор данных знаний |
| `01_Mathematik/` ... `12_Kultur_Kunst_Sprache/` | Предметно-ориентированная структура источника/экспорта Markdown |
| `wikistub_seed_cli.py` | CLI для статистики и проверок |
| `wikistub_seed_pipeline.py` | Конвейер импорта, экспорта, валидации и опционального перевода |
| `md_to_json.py` | Вспомогательный инструмент импорта Markdown в JSON |
| `check_duplicates.py` | Вспомогательный инструмент для дубликатов/согласованности |
| `EXPORTFORMAT.md` | План стабильного формата обмена |
| `web_publisher/` | Статический PWA с офлайн-кэшем, поиском и выбором шести языков |

## Конфиденциальность

WikiStub-Seed — это локальное решение прежде всего. Базовое использование читает и записывает только локальные файлы JSON/Markdown. Телеметрия и автоматическое сетевое взаимодействие отсутствуют.

Опциональная команда перевода может обращаться к внешнему API только при условии, что установлен `ANTHROPIC_API_KEY` и установлен опциональный пакет `anthropic`.

## Дорожная карта

Выполнено:

- 12 предметных областей верхнего уровня и 85 подкатегорий
- 630 двуязычных заглушек в едином главном файле JSON
- Инструменты экспорта в Markdown и синхронизации JSON
- Дымовые тесты CLI в GitHub Actions, а также специальные дымовые тесты источника для macOS/Linux для `wikistub_seed_cli.py check` и `wikistub_seed_pipeline.py validate`
- Статический веб-/PWA-издатель с поиском и кэшем офлайн (`web_publisher/`)
- Схема-обёртка `wikistub-seed-data-v1` с языковыми картами DE/EN/ES/ZH/JA/RU

Запланировано:

- Единая очистка тегов
- Пути экспорта для Obsidian/GitHub Pages
- Опциональные встраивания и поисковый API

## Deutsch

**WikiStub-Seed ist ein mehrsprachiges JSON-Wissensgerüst.** Definitionen sind in DE/EN/ES/ZH/JA/RU gefüllt; Relevanztexte in DE/ES/ZH/JA/RU, mit deutschem Fallback für Englisch.

WikiStub-Seed arbeitet standardmäßig lokal mit `wikistub_seed.json`. Die Kernfunktionen benötigen keine externen Pakete. Nur die optionale Übersetzungsfunktion nutzt externe API-Aufrufe, wenn ein API-Key gesetzt und das optionale Paket installiert wurde.

Wichtige Einstiegspunkte:

- `python wikistub_seed_cli.py stats` zeigt Statistik und Kategorien.
- `python wikistub_seed_cli.py check` prüft den Datenbestand.
- `python wikistub_seed_pipeline.py export --output --english` exportiert Markdown.
- `EXPORTFORMAT.md` beschreibt den geplanten stabilen Austauschstandard.
- `web_publisher/` enthält den fertigen statischen Web/PWA-Publisher mit Offline-Cache und Sechs-Sprachen-Auswahl.

## Лицензия

Лицензия MIT. См. `LICENSE`.

Этот проект является безвозмездным вкладом в открытый исходный код. Ответственность ограничена умыслом и грубой небрежностью в соответствии с § 521 Гражданского кодекса Германии, а также применяются отказы от ответственности лицензии MIT. Использование на свой страх и риск.
