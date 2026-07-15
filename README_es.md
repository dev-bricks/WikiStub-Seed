![WikiStub-Seed](assets/banner.svg)

# WikiStub-Seed

[EN](README.md) | [DE](README_de.md) | **ES** | [JA](README_ja.md) | [RU](README_ru.md) | [ZH](README_zh-Hans.md)

**WikiStub-Seed es un marco de conocimiento JSON multilingüe para investigación asistida por IA, documentación, sistemas de aprendizaje y flujos de trabajo con LLM.** Incluye 630 stubs en 12 dominios. Las definiciones están completas en DE/EN/ES/ZH/JA/RU; las notas de relevancia están completas en DE/ES/ZH/JA/RU y usan el fallback alemán para los slots ingleses vacíos.

WikiStub-Seed es una biblioteca semilla de stubs de conocimiento, no un wiki.

[![WikiStub-Seed smoke tests](https://github.com/dev-bricks/WikiStub-Seed/actions/workflows/tests.yml/badge.svg)](https://github.com/dev-bricks/WikiStub-Seed/actions/workflows/tests.yml)
![Stubs](https://img.shields.io/badge/stubs-630%2B-blue)
![Languages](https://img.shields.io/badge/languages-DE%20%7C%20EN%20%7C%20ES%20%7C%20ZH%20%7C%20JA%20%7C%20RU-orange)
![Format](https://img.shields.io/badge/format-JSON-green)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

## Contenido

- 630 stubs en `wikistub_seed.json` con definiciones en seis idiomas y notas de relevancia en cinco
- 12 dominios de primer nivel, incluidos matemáticas, física, química, biología, medicina, psicología, IA, ingeniería, sociedad, economía, historia y cultura
- 85 subcategorías con definiciones cortas y neutrales y notas de relevancia
- Mapas canónicos `definitions.{lang}` y `relevance_i18n.{lang}` conservando los campos heredados `definition_de`, `definition_en` y `relevance`
- Herramientas CLI en Python para estadísticas, validación, comprobaciones de consistencia y exportación a Markdown
- Una dirección de exportación documentada `wikistub-seed-data-v1` para uso futuro en sitios Web/PWA estáticos
- Sin dependencias externas requeridas para la importación, exportación, validación o uso de CLI básico

## Casos de uso

- Crear una base de conocimiento local para escritura o investigación asistida por IA
- Construir glosarios de documentación, mapas de aprendizaje o catálogos de conceptos
- Exportar Markdown estructurado para Obsidian, GitHub Pages o sitios estáticos
- Alimentar pipelines de recuperación, embeddings o contexto LLM con stubs de dominio compactos
- Traducir y ampliar un esqueleto de conocimiento neutro en dominio en un formato JSON controlado

## Estructura de datos

Cada stub está intencionalmente diseñado para ser pequeño y legible por máquina:

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

La fuente autoritativa actual es `wikistub_seed.json`. `EXPORTFORMAT.md` documenta el formato envolvente estable `wikistub-seed-data-v1` para exportaciones Web/PWA, API y LLM.

## Inicio rápido

```bash
git clone https://github.com/dev-bricks/WikiStub-Seed.git
cd WikiStub-Seed

python wikistub_seed_cli.py --help
python wikistub_seed_cli.py stats
python wikistub_seed_cli.py check
python wikistub_seed_pipeline.py validate
python wikistub_seed_pipeline.py export --output --english
```

En Windows, `start.bat` abre el punto de entrada de la CLI. Los archivos exportados se escriben en `output/`; esa carpeta es local y no está versionada.

## Comandos principales

| Comando | Propósito |
|---|---|
| `python wikistub_seed_cli.py stats` | Mostrar estadísticas de stubs, categorías y etiquetas |
| `python wikistub_seed_cli.py check` | Ejecutar comprobaciones de consistencia sobre el conjunto de datos JSON |
| `python wikistub_seed_pipeline.py validate` | Validar los datos de entrada de la pipeline |
| `python wikistub_seed_pipeline.py export --output --english` | Exportar el conjunto de datos JSON a Markdown |
| `python wikistub_seed_pipeline.py translate` | Traducir opcionalmente definiciones en inglés faltantes cuando esté configurado |

## Mapa del repositorio

| Ruta | Propósito |
|---|---|
| `wikistub_seed.json` | Conjunto de datos de conocimiento multilingüe autoritativo |
| `01_Mathematik/` ... `12_Kultur_Kunst_Sprache/` | Estructura de fuente/exportación Markdown orientada a dominio |
| `wikistub_seed_cli.py` | CLI para estadísticas y comprobaciones |
| `wikistub_seed_pipeline.py` | Pipeline de importación, exportación, validación y traducción opcional |
| `md_to_json.py` | Herramienta auxiliar de importación Markdown a JSON |
| `check_duplicates.py` | Herramienta auxiliar de duplicados/consistencia |
| `EXPORTFORMAT.md` | Plan de formato de intercambio estable |
| `web_publisher/` | Editor web estático/PWA (caché sin conexión, búsqueda, selector de seis idiomas) |

## Privacidad

WikiStub-Seed es local-first. El uso básico lee y escribe únicamente archivos JSON/Markdown locales. No hay telemetría ni comunicación de red automática.

El comando de traducción opcional puede llamar a una API externa únicamente cuando `ANTHROPIC_API_KEY` está configurado y el paquete opcional `anthropic` está instalado.

## Hoja de ruta

Completado:

- 12 dominios de primer nivel y 85 subcategorías
- 630 stubs multilingües en un único archivo maestro JSON
- Herramientas de exportación a Markdown y sincronización JSON
- Pruebas de humo CLI en GitHub Actions, más pruebas de humo de fuente dedicadas para macOS/Linux de `wikistub_seed_cli.py check` y `wikistub_seed_pipeline.py validate`
- Editor web estático/PWA con búsqueda y caché sin conexión (`web_publisher/`)
- Envolvente de esquema `wikistub-seed-data-v1` con mapas DE/EN/ES/ZH/JA/RU

Planificado:

- Limpieza unificada de etiquetas
- Rutas de exportación para Obsidian/GitHub Pages
- Embeddings opcionales y API de búsqueda

## Deutsch

**WikiStub-Seed ist ein mehrsprachiges JSON-Wissensgerüst.** Definitionen sind in DE/EN/ES/ZH/JA/RU gefüllt; Relevanztexte in DE/ES/ZH/JA/RU, mit deutschem Fallback für Englisch.

WikiStub-Seed arbeitet standardmäßig lokal mit `wikistub_seed.json`. Die Kernfunktionen benötigen keine externen Pakete. Nur die optionale Übersetzungsfunktion nutzt externe API-Aufrufe, wenn ein API-Key gesetzt und das optionale Paket installiert wurde.

Wichtige Einstiegspunkte:

- `python wikistub_seed_cli.py stats` zeigt Statistik und Kategorien.
- `python wikistub_seed_cli.py check` prüft den Datenbestand.
- `python wikistub_seed_pipeline.py export --output --english` exportiert Markdown.
- `EXPORTFORMAT.md` beschreibt den geplanten stabilen Austauschstandard.
- `web_publisher/` enthält den fertigen statischen Web/PWA-Publisher mit Offline-Cache und Sechs-Sprachen-Auswahl.

## Licencia

Licencia MIT. Véase `LICENSE`.

Este proyecto es una donación de código abierto no remunerada. La responsabilidad se limita a la intención y negligencia grave según el artículo 521 del Código Civil alemán, aplicándose también los descargos de responsabilidad de la licencia MIT. Uso bajo su propio riesgo.
