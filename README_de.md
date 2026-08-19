![WikiStub-Seed](assets/banner.svg)

# WikiStub-Seed

[EN](README.md) | **DE** | [ES](README_es.md) | [JA](README_ja.md) | [RU](README_ru.md) | [ZH](README_zh-Hans.md)

**WikiStub-Seed ist ein mehrsprachiges JSON-Wissensgerüst für KI-gestützte Forschung, Dokumentation, Lernsysteme und LLM-Workflows.** Es enthält 630 kompakte Wissens-Stubs über 12 Wissenschafts- und Kulturbereiche. Definitionen sind in DE/EN/ES/ZH/JA/RU gefüllt; Relevanztexte in DE/ES/ZH/JA/RU, während leere englische Relevanzslots den dokumentierten deutschen Fallback nutzen.

WikiStub-Seed ist eine Wissens-Stub-Seed-Bibliothek, kein Wiki.

[![WikiStub-Seed smoke tests](https://github.com/dev-bricks/WikiStub-Seed/actions/workflows/tests.yml/badge.svg)](https://github.com/dev-bricks/WikiStub-Seed/actions/workflows/tests.yml)
[![Version](https://img.shields.io/badge/version-1.1.7-blue.svg)](pyproject.toml)
[![Ecosystem: dev-bricks](https://img.shields.io/badge/ecosystem-dev--bricks-blue.svg)](https://github.com/dev-bricks)
[![Umbrella: open-bricks](https://img.shields.io/badge/umbrella-open--bricks-indigo.svg)](https://github.com/open-bricks)
![Stubs](https://img.shields.io/badge/stubs-630%2B-blue)
![Languages](https://img.shields.io/badge/languages-DE%20%7C%20EN%20%7C%20ES%20%7C%20ZH%20%7C%20JA%20%7C%20RU-orange)
![Format](https://img.shields.io/badge/format-JSON-green)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![Tests](https://img.shields.io/badge/tests-150%20Python%20%7C%2045%20Node%20passed-success)
[![llms.txt](https://img.shields.io/badge/llms.txt-verf%C3%BCgbar-blueviolet)](llms.txt)
![License](https://img.shields.io/badge/license-MIT-green)

## Einstieg

| Wenn du... | Öffne dies |
|---|---|
| Den Datensatz prüfen willst | `wikistub_seed.json` |
| Einen schnellen lokalen Check ausführen willst | `python wikistub_seed_cli.py check` |
| Markdown für Doku oder Notizen exportieren willst | `python wikistub_seed_pipeline.py export --output --english` |
| Das Austauschformat verstehen willst | `EXPORTFORMAT.md` |
| Den optionalen lokalen Suchvertrag lesen willst | `EMBEDDING_SEARCH_API.md` |
| Die statische PWA-Quelle ansehen willst | `web_publisher/` |
| Die KI/LLM-Indexdatei lesen willst | [llms.txt](llms.txt) |
| Die englische Anleitung lesen willst | [README.md](README.md) |

> [!NOTE]
> **KI- & LLM-Integration**: Für maschinenlesbaren Kontext, Repository-Struktur, Suchphrasen und LLM-Richtlinien siehe [llms.txt](llms.txt).

## Architektur & Datenfluss

```mermaid
flowchart TD
    A["wikistub_seed.json<br/>(630 Mehrsprachige Stubs)"] --> B["wikistub_seed_cli.py<br/>(Statistik & Validierung)"]
    A --> C["wikistub_seed_pipeline.py<br/>(Markdown & JSON Exporter)"]
    A --> D["web_publisher/ _build.py<br/>(Statischer PWA-Publisher)"]
    A --> E["RAG & LLM Kontext-Pipelines<br/>(KI-Workflows & Embeddings)"]
    C --> F["Strukturiertes Markdown<br/>(Obsidian / GitHub Pages / Doku)"]
    D --> G["PWA Web-Frontend<br/>(Offline-Suche / 6 Sprachen)"]
```

## Auffindbarkeit

Nutze beim Verlinken oder Suchen den kanonischen Reponamen `dev-bricks/WikiStub-Seed`. Das Projekt war früher mit `file-bricks/MetaWiki` verbunden; aktuell ist es die dev-bricks-Bibliothek für strukturierte Wissens-Stubs.

Passende Suchphrasen:

- `WikiStub-Seed JSON knowledge stubs`
- `bilingual JSON knowledge base Python`
- `local-first ontology seed library LLM workflows`
- `multilingual knowledge stubs framework`
- `RAG Wissensbasis Deutsch Englisch JSON`

## Inhalt

- 630 Wissens-Stubs in `wikistub_seed.json` mit Definitionen in sechs und Relevanztexten in fünf Sprachen
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

Die aktuelle maßgebliche Quelle ist `wikistub_seed.json`. `EXPORTFORMAT.md` dokumentiert das stabile Wrapper-Format `wikistub-seed-data-v1` für Web-/PWA-, API- und LLM-Exporte.

## Schnellstart

```bash
git clone https://github.com/dev-bricks/WikiStub-Seed.git
cd WikiStub-Seed

python wikistub_seed_cli.py --help
python wikistub_seed_cli.py stats
python wikistub_seed_cli.py check
python wikistub_seed_pipeline.py validate
python wikistub_seed_pipeline.py export --output --english
```

Unter Windows öffnet `start.bat` den CLI-Einstiegspunkt. Exportierte Dateien werden in `output/` abgelegt; dieser Ordner ist lokal und nicht versioniert.

## Lokaler Edit-Modus

`web_publisher/` ist eine statische Seite (kein Server, nur `fetch()`) und kann nicht schreiben. `edit_server.py` legt einen kleinen, ausschließlich an `127.0.0.1` gebundenen HTTP-Server darüber, sodass dieselbe Leseoberfläche Artikel/Kategorien anlegen, bearbeiten und löschen kann:

```bash
python edit_server.py            # Standardport 8879, öffnet den Browser
```

**Rechtemodell** (wörtlich aus der spezifizierenden Anfrage übernommen, und die eine verbindliche Regel, der dieses Feature folgt):

- Neuanlegen ist standardmäßig für jeden erlaubt.
- Bearbeiten und Löschen sind für jeden erlaubt, **solange kein Passwort hinterlegt ist**.
- Ist ein Passwort hinterlegt, entscheidet der Hinterleger, was ohne Anmeldung noch erlaubt bleibt — von "alles" bis nur-lesend (Neuanlegen/Bearbeiten/Löschen sind einzeln entziehbar, über das "Konto"-Panel im Header).
- Es gibt bewusst nur **ein** Passwort/eine Rolle. Mehrere Tokens mit unterschiedlichen Rechten plus eine Administrator-Rolle wurden erwogen, aber als "vielleicht etwas übertrieben" eingestuft und weiter unten als Roadmap-Idee dokumentiert, nicht gebaut.

**Sicherheitshinweise:**

- Der Server bindet ausschließlich an `127.0.0.1` — nicht konfigurierbar, kein Cloud-/Netz-Exposure per Design.
- Das Passwort wird als PBKDF2-HMAC-SHA256-Hash gespeichert (`wiki_auth.json`, gitignored), nie im Klartext. Dieser Hash schützt davor, dass ein beiläufiges Lesen der Datei ein (möglicherweise wiederverwendetes) Passwort preisgibt — er schützt **nicht** vor lokalem Dateisystemzugriff; wer bereits Dateien auf dem Rechner lesen/schreiben kann, kann `wiki_auth.json` ohnehin ersetzen. Passwort vergessen? `wiki_auth.json` löschen, um zum Standard (kein Passwort, volle Rechte für alle) zurückzukehren.
- Jede schreibende Anfrage muss `Content-Type: application/json` tragen (verhindert klassisches formularbasiertes CSRF, das diesen Content-Type ohne einen von diesem Server unbeantworteten CORS-Preflight nicht senden kann) sowie einen `Host`-Header aus `localhost`/`127.0.0.1` (verhindert DNS-Rebinding).
- Löschungen sind weich: Artikel und Kategorien wandern in `wikistub_seed_trash.json` (gitignored) statt endgültig entfernt zu werden, und können über die API wiederhergestellt werden.
- **`web_publisher/data/wikistub_seed.json` und `search-index.json` sind getrackte, committete Build-Artefakte.** Jeder erfolgreiche Schreibvorgang im Edit-Modus baut sie über dasselbe `_build.py` neu, das auch die CI dieses Repos nutzt. Wer den lokalen Edit-Server zum Ausprobieren genutzt hat: vor dem Commit `git status` prüfen — ein lokaler Testedit verschmutzt diese beiden Dateien genauso wie ein echter, und nichts hier ignoriert sie automatisch (sie müssen für GitHub-Pages-Hosting ohne Build-Schritt getrackt bleiben).

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
| `wikistub_seed.json` | Maßgeblicher mehrsprachiger Wissensdatensatz |
| `01_Mathematik/` ... `12_Kultur_Kunst_Sprache/` | Domänenorientierte Markdown-Quell-/Exportstruktur |
| `wikistub_seed_cli.py` | CLI für Statistiken und Prüfungen |
| `wikistub_seed_pipeline.py` | Import-, Export-, Validierungs- und optionale Übersetzungs-Pipeline |
| `md_to_json.py` | Markdown-zu-JSON-Import-Hilfsprogramm |
| `check_duplicates.py` | Duplikat-/Konsistenz-Hilfsprogramm |
| `EXPORTFORMAT.md` | Stabiler Austauschformat-Plan |
| `web_publisher/` | Statischer Web-/PWA-Publisher (Offline-Cache, Suche, Sechs-Sprachen-Auswahl) |
| `edit_server.py` | Nur-lokaler (`127.0.0.1`) HTTP-Server, ergänzt `web_publisher/` um GUI-Neuanlegen/Bearbeiten/Löschen |
| `wiki_store.py` | Reine CRUD- + Papierkorb-Funktionen, die der Edit-Server (und jeder künftige Aufrufer) nutzt |
| `wiki_auth.py` | Passwort-Hashing, Rechtemodell und Session-Verwaltung für den Edit-Server |

## Datenschutz

WikiStub-Seed arbeitet standardmäßig lokal. Der Kernbetrieb liest und schreibt ausschließlich lokale JSON-/Markdown-Dateien. Es gibt keine Telemetrie und keine automatische Netzwerkkommunikation.

Der optionale Übersetzungsbefehl kann eine externe API aufrufen, wenn `ANTHROPIC_API_KEY` gesetzt und das optionale Paket `anthropic` installiert ist.

`edit_server.py` (siehe „Lokaler Edit-Modus" oben) bindet ausschließlich an `127.0.0.1` und spricht von sich aus nie mit dem Netz; die einzigen neuen lokalen Dateien sind `wiki_auth.json` (ein Passwort-Hash, gitignored) und `wikistub_seed_trash.json` (weich gelöschter Inhalt, gitignored).

## Roadmap

Abgeschlossen:

- 12 Oberbereiche und 85 Unterkategorien
- 630 mehrsprachige Stubs in einer einzigen JSON-Hauptdatei
- Markdown-Export- und JSON-Synchronisierungswerkzeuge
- CLI-Smoke-Tests in GitHub Actions sowie dedizierte macOS/Linux-Quell-Smokes für `wikistub_seed_cli.py check` und `wikistub_seed_pipeline.py validate`
- Statischer Web-/PWA-Publisher mit Suche und Offline-Cache (`web_publisher/`)
- `wikistub-seed-data-v1`-Schema-Wrapper mit DE/EN/ES/ZH/JA/RU-Sprachmaps
- Lokaler, passwortgeschützter GUI-Edit-Modus für die PWA (`edit_server.py`, `wiki_store.py`, `wiki_auth.py`) — Neuanlegen/Bearbeiten/Löschen für Artikel und Kategorien, Papierkorb, vollständige Testabdeckung der Rechte-Matrix

Geplant:

- Einheitliche Tag-Bereinigung
- Obsidian-/GitHub-Pages-Exportpfade
- Optionale Embeddings und Such-API (in [`EMBEDDING_SEARCH_API.md`](EMBEDDING_SEARCH_API.md) spezifiziert; Implementierung bleibt optional)
- **Enterprise-Edit-Modus-Konzept (hier dokumentiert, nicht gebaut):** mehrere benannte Zugangstokens mit unabhängig konfigurierten Rechten, plus eine eigene Administrator-Rolle, die diese Tokens verwaltet. Der aktuelle Edit-Modus hat bewusst nur ein Passwort/eine Rolle — das wurde vom Spezifizierenden als „vielleicht etwas übertrieben" eingestuft und ist hier als bewusst erwogene, vorerst zurückgestellte Ausbaustufe festgehalten, nicht als stille Lücke.

## Deutsch

**WikiStub-Seed ist ein mehrsprachiges JSON-Wissensgerüst für KI-gestützte Wissensarbeit.** Das Repository enthält 630 kompakte Wissens-Stubs mit Definitionen in Deutsch, Englisch, Spanisch, Chinesisch, Japanisch und Russisch. Relevanztexte liegen in allen diesen Sprachen außer Englisch vor; dort greift der dokumentierte deutsche Fallback.

WikiStub-Seed arbeitet standardmäßig lokal mit `wikistub_seed.json`. Die Kernfunktionen benötigen keine externen Pakete. Nur die optionale Übersetzungsfunktion nutzt externe API-Aufrufe, wenn ein API-Key gesetzt und das optionale Paket installiert wurde.

Wichtige Einstiegspunkte:

- `python wikistub_seed_cli.py stats` zeigt Statistik und Kategorien.
- `python wikistub_seed_cli.py check` prüft den Datenbestand.
- `python wikistub_seed_pipeline.py export --output --english` exportiert Markdown.
- `EXPORTFORMAT.md` beschreibt den geplanten stabilen Austauschstandard.
- `web_publisher/` enthält den fertigen statischen Web/PWA-Publisher mit Offline-Cache und Sechs-Sprachen-Auswahl.

<!-- BEGIN ELLMOS BUNDLE DISCOVERY DE -->

## Bundles und Partner

Geprüfte Discovery-Projektion für `module:WikiStub-Seed` aus
`catalog:v4-bundles`
(`546290dafbaafd810df1d59ef5a3d7183738472b48cd5a8a81f1e8f2b64d852e`).
Das Ziel-Repository ist `public`. Die Bundle-Manifeste bleiben die Autorität
für Mitgliedschaften; dieser Abschnitt installiert oder aktiviert keine
Komponenten. Die Freigabe beruht auf einem öffentlichen Modul-Registry-Eintrag
und einer ausdrücklichen Default-deny-Allowlist für Bundles.

### `ellmos-knowledge-bundle`

- Sichtbarkeit des Bundle-Rezepts: `private`; Rolle: `declared-component`;
  Anforderung: `recommended`.
- Modulpartner: `module:KnowledgeDigest`, `module:project-docs-template`,
  `module:report-forge`, `module:web-scraper`.
- Skill-Partner: `skill:bilingual-doc-sync`, `skill:docs-analysis`,
  `skill:document-chunker`.

Kompositions- und Runtime-Details werden bewusst nicht offengelegt.

<!-- END ELLMOS BUNDLE DISCOVERY DE -->

## Geschwisterwerkzeuge & Ökosystem
 
WikiStub-Seed ist Teil des **dev-bricks** Ökosystems und der übergeordneten **open-bricks** Familie:
 
| Werkzeug | Zweck | Status |
|---|---|---|
| [`dev-bricks/CareCenter-for-Codex`](https://github.com/dev-bricks/CareCenter-for-Codex) | Workspace-Gesundheitscheck, Diagnose & Test-Orchestrierung | Production |
| [`dev-bricks/MethodenAnalyser`](https://github.com/dev-bricks/MethodenAnalyser) | AST-basierte Python-Codeanalyse, Import-Optimierung & Dead-Code-Erkennung | Production |
| [`dev-bricks/DevCenter`](https://github.com/dev-bricks/DevCenter) | Zentrales Entwickler-Dashboard, Repo-Health-Übersicht & Projekt-Starter | Production |
| [`dev-bricks/CodeBox`](https://github.com/dev-bricks/CodeBox) | Schlanke PySide6 Desktop-IDE mit Syntax-Highlighting & Terminal | Beta |
| [`dev-bricks/safe-start-for-codex`](https://github.com/dev-bricks/safe-start-for-codex) | Sichere Initialisierung und Verifikation für Entwicklungs-Workspaces | Production |
| [`ellmos-ai/project-docs-template`](https://github.com/ellmos-ai/project-docs-template) | Standardisierter Dokumentations-Generator und Compliance-Framework | Production |
 
## Lizenz

MIT-Lizenz. Siehe `LICENSE`.

Dieses Projekt ist eine unentgeltliche Open-Source-Spende. Die Haftung ist gemäß § 521 BGB auf Vorsatz und grobe Fahrlässigkeit beschränkt; die Haftungsausschlüsse der MIT-Lizenz gelten ebenfalls. Nutzung auf eigene Gefahr.
