![WikiStub-Seed](assets/banner.svg)

# WikiStub-Seed

[EN](README.md) | [DE](README_de.md) | [ES](README_es.md) | **JA** | [RU](README_ru.md) | [ZH](README_zh-Hans.md)

**WikiStub-Seedは、AI支援研究・ドキュメント作成・学習システム・LLMワークフロー向けの多言語JSONナレッジフレームワークです。** 630件のスタブの定義はDE/EN/ES/ZH/JA/RUで、関連性テキストはDE/ES/ZH/JA/RUで実装され、空の英語スロットにはドイツ語フォールバックを使います。

WikiStub-Seedはナレッジスタブのシードライブラリであり、Wikiではありません。

[![WikiStub-Seed test gates](https://github.com/dev-bricks/WikiStub-Seed/actions/workflows/tests.yml/badge.svg)](https://github.com/dev-bricks/WikiStub-Seed/actions/workflows/tests.yml)
[![Version](https://img.shields.io/badge/version-1.1.12-blue.svg)](pyproject.toml)
[![Ecosystem: dev-bricks](https://img.shields.io/badge/ecosystem-dev--bricks-blue.svg)](https://github.com/dev-bricks)
[![Umbrella: open-bricks](https://img.shields.io/badge/umbrella-open--bricks-indigo.svg)](https://github.com/open-bricks)
![Stubs](https://img.shields.io/badge/stubs-630%2B-blue)
![Languages](https://img.shields.io/badge/languages-DE%20%7C%20EN%20%7C%20ES%20%7C%20ZH%20%7C%20JA%20%7C%20RU-orange)
![Format](https://img.shields.io/badge/format-JSON-green)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-yellow)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Attribution Notice](https://img.shields.io/badge/attribution-NOTICE-informational.svg)](NOTICE)
[![Marketing Log](https://img.shields.io/badge/marketing%20log-active-blue.svg)](MARKETING-LOG.txt)
[![llms.txt](https://img.shields.io/badge/llms.txt-%E5%88%A9%E7%94%A8%E5%8F%AF%E8%83%BD-blueviolet)](llms.txt)
![ライセンス](https://img.shields.io/badge/%E3%83%A9%E3%82%A4%E3%82%BB%E3%83%B3%E3%82%B9-MIT-green)

## まずはここから

| したいこと | 開くファイル |
|---|---|
| データセットを確認する | `wikistub_seed.json` |
| ローカルで簡易チェックを実行する | `python wikistub_seed_cli.py check` |
| ドキュメントやメモ用に Markdown をエクスポートする | `python wikistub_seed_pipeline.py export --output --english` |
| 交換フォーマットを理解する | `EXPORTFORMAT.md` |
| 静的 PWA のソースを見る | `web_publisher/` |
| AI/LLM インデックスファイルを読む | [llms.txt](llms.txt) |
| 英語ガイドを読む | [README.md](README.md) |

> [!NOTE]
> **AI・LLM 統合**: 機械可読コンテキスト、リポジトリ構造、検索フレーズ、LLM ガイドラインについては [llms.txt](llms.txt) を参照してください。

## アーキテクチャとデータフロー

```mermaid
flowchart TD
    A["wikistub_seed.json<br/>(630件の多言語スタブ)"] --> B["wikistub_seed_cli.py<br/>(統計と検証)"]
    A --> C["wikistub_seed_pipeline.py<br/>(Markdown・JSONエクスポーター)"]
    A --> D["web_publisher/ _build.py<br/>(静的PWAパブリッシャー)"]
    A --> E["RAG・LLMコンテキストパイプライン<br/>(AIワークフローと埋め込み)"]
    C --> F["構造化Markdown<br/>(Obsidian / GitHub Pages / ドキュメント)"]
    D --> G["PWA Webフロントエンド<br/>(データ検索 / 6つのコンテンツ言語)"]
```

## 検出コンテキスト

リンクや検索の際には、正規のリポジトリ名 `dev-bricks/WikiStub-Seed` を使用してください。このプロジェクトは以前 `file-bricks/MetaWiki` と関連していましたが、現在のリポジトリは dev-bricks のナレッジスタブ・シードライブラリです。

このプロジェクトをよく表す検索フレーズ:

- `WikiStub-Seed JSON knowledge stubs`
- `bilingual JSON knowledge base Python`
- `local-first ontology seed library for LLM workflows`
- `multilingual knowledge stubs framework`
- `RAG knowledge base German English JSON`

## 収録内容

- `wikistub_seed.json` に6言語の定義と5言語の関連性テキストを持つ630件のナレッジスタブ
- 数学、物理学、化学、生物学、医学、心理学、AI、工学、社会、経済学、歴史、文化を含む12のトップレベルドメイン
- 短く中立的な定義と関連性ノートを持つ85のサブカテゴリ
- レガシーフィールド `definition_de`、`definition_en`、`relevance` を維持しつつ、正規の `definitions.{lang}` および `relevance_i18n.{lang}` マップを提供
- 統計・バリデーション・整合性チェック・Markdownエクスポートのための Python CLI ツール
- 将来の静的 Web/PWA 利用に向けた文書化済み `wikistub-seed-data-v1` エクスポート方向
- ソースチェックアウトの主なデータ確認・統計・エクスポートには Python 標準ライブラリを使用します。オプションの翻訳、検索連携、開発用チェックには別途依存関係があります。

## ユースケース

- AI支援の執筆や研究のためのローカルナレッジベースの構築
- ドキュメントグロッサリー、学習マップ、コンセプトカタログの作成
- Obsidian、GitHub Pages、または静的サイト向けの構造化 Markdown のエクスポート
- コンパクトなドメインスタブを使った検索・埋め込み・LLMコンテキストパイプラインへの供給
- 制御された JSON 形式でドメインニュートラルなナレッジスケルトンの翻訳と拡張

## データ構造

各スタブは意図的に小さく、機械可読な形式になっています：

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

現在の権威あるソースは `wikistub_seed.json` です。`EXPORTFORMAT.md` は、Web/PWA・API・LLM エクスポート向けの安定したラッパーフォーマット `wikistub-seed-data-v1` を文書化しています。

## クイックスタート

```bash
git clone https://github.com/dev-bricks/WikiStub-Seed.git
cd WikiStub-Seed

python wikistub_seed_cli.py --help
python wikistub_seed_cli.py stats
python wikistub_seed_cli.py check
python wikistub_seed_pipeline.py validate
python wikistub_seed_pipeline.py export --output --english
```

CLI、データセット、PWA を含む完全な利用方法はソースチェックアウトです。wheel には再利用可能な 6 つの API モジュールが含まれますが、CLI と PWA は含まれません。インストール済み API からデータを変更するには、外部のデータパスと認証パスを明示的に指定します。site-packages をユーザーデータの保存先にはしません。

Windows では、`start.bat` が CLI エントリポイントを開きます。エクスポートされたファイルは `output/` に書き込まれます。このフォルダはローカルでバージョン管理されません。

## コアコマンド

| コマンド | 目的 |
|---|---|
| `python wikistub_seed_cli.py stats` | スタブ・カテゴリ・タグの統計を表示 |
| `python wikistub_seed_cli.py check` | JSON データセットの整合性チェックを実行 |
| `python wikistub_seed_pipeline.py validate` | パイプライン入力データをバリデート |
| `python wikistub_seed_pipeline.py export --output --english` | JSON データセットを Markdown にエクスポート |
| `python wikistub_seed_pipeline.py translate --confirm-api-cost --max-budget-usd AMOUNT` | 費用を確認し上限を指定して、不足する英語定義を翻訳 |

## リポジトリマップ

| パス | 目的 |
|---|---|
| `wikistub_seed.json` | 権威あるバイリンガルナレッジデータセット |
| `01_Mathematik/` ... `12_Kultur_Kunst_Sprache/` | ドメイン指向の Markdown ソース/エクスポート構造 |
| `wikistub_seed_cli.py` | 統計とチェックのための CLI |
| `wikistub_seed_pipeline.py` | インポート・エクスポート・バリデーション・オプション翻訳パイプライン |
| `md_to_json.py` | Markdown から JSON へのインポートヘルパー |
| `check_duplicates.py` | 重複/整合性ヘルパー |
| `EXPORTFORMAT.md` | 安定した交換フォーマット計画 |
| `web_publisher/` | 静的 PWA。読み込み後にサイトのリソースとデータをキャッシュでき、選択欄はコンテンツ言語を切り替えます |

## プライバシー

CLI の検証とエクスポートはローカルファイルを扱います。静的 PWA は同一オリジンからデータとリソースを取得し、正常に読み込んだ後は service worker がそれらをキャッシュできます。初回アクセスと更新にはサイトへの接続が必要です。
PWA の言語選択はデータの言語を切り替えるもので、画面全体を翻訳するものではありません。定義は 6 言語、英語の関連性欄が空の場合の fallback はドイツ語です。
オプションの翻訳は Anthropic API にリクエストを送信します。CLI には `ANTHROPIC_API_KEY`、オプションの `anthropic` パッケージ、`--confirm-api-cost`、正の `--max-budget-usd` が必要です。モジュール API の `translate_text` と `translate_batch` は `max_budget_usd` を明示的に受け取ります。ローカル見積もりは実際の請求額を保証しません。

## ロードマップ

完了済み：

- 12のトップレベルドメインと85のサブカテゴリ
- 単一の JSON マスターファイルに630件のバイリンガルスタブ
- Markdown エクスポートと JSON 同期ツール
- GitHub Actions での CLI スモークテスト、および `wikistub_seed_cli.py check` と `wikistub_seed_pipeline.py validate` 向けの macOS/Linux ソーススモーク
- 静的 PWA は検索を提供し、読み込み後にサイトのリソースとデータをキャッシュできます（`web_publisher/`）。
- DE/EN/ES/ZH/JA/RU 言語マップを持つ `wikistub-seed-data-v1` スキーマラッパー

計画中：

- 統一されたタグのクリーンアップ
- Obsidian/GitHub Pages エクスポートパス
- オプションの埋め込みと検索 API

## Deutsch

**WikiStub-Seed ist ein mehrsprachiges JSON-Wissensgerüst.** Definitionen sind in DE/EN/ES/ZH/JA/RU gefüllt; Relevanztexte in DE/ES/ZH/JA/RU, mit deutschem Fallback für Englisch.

WikiStub-Seed arbeitet mit den lokal angegebenen JSON-/Markdown-Dateien. Die statische PWA lädt Daten und Ressourcen vom selben Ursprung und kann sie nach dem Laden im Service Worker zwischenspeichern; Erstaufruf und Aktualisierungen benötigen den Zugriff auf die Website. Die Sprachauswahl wechselt die Inhaltssprache, nicht die gesamte Oberfläche. Die optionale Übersetzung sendet Anfragen an Anthropic und erfordert `ANTHROPIC_API_KEY` sowie das optionale Paket `anthropic`. Die CLI verlangt zusätzlich `--confirm-api-cost` und ein positives `--max-budget-usd`; die Modul-APIs `translate_text` und `translate_batch` verlangen ein explizites `max_budget_usd`. Die lokale Schätzung garantiert nicht den abgerechneten Betrag.

Wichtige Einstiegspunkte:

- `python wikistub_seed_cli.py stats` zeigt Statistik und Kategorien.
- `python wikistub_seed_cli.py check` prüft den Datenbestand.
- `python wikistub_seed_pipeline.py export --output --english` exportiert Markdown.
- `EXPORTFORMAT.md` beschreibt den geplanten stabilen Austauschstandard.
- `web_publisher/` enthält eine statische PWA mit Suche und einem Sprachwähler für die Inhalte; geladene Website-Ressourcen und Daten können im Service Worker zwischengespeichert werden.

<!-- BEGIN ELLMOS BUNDLE DISCOVERY JA -->

## バンドルとパートナー

`catalog:v4-bundles`
（`546290dafbaafd810df1d59ef5a3d7183738472b48cd5a8a81f1e8f2b64d852e`）
から生成された、`module:WikiStub-Seed` の検証済み Discovery
プロジェクションです。対象リポジトリの可視性は `public` です。
メンバーシップの権威は引き続き Bundle Manifest にあり、この節は
コンポーネントをインストールも有効化もしません。承認根拠は公開
Module Registry レコードと、default-deny の明示的な Bundle Allowlist です。

### `ellmos-knowledge-bundle`

- Bundle Recipe の可視性: `private`、役割: `declared-component`、
  要件: `recommended`。
- Module パートナー: `module:KnowledgeDigest`,
  `module:project-docs-template`, `module:report-forge`,
  `module:web-scraper`。
- Skill パートナー: `skill:bilingual-doc-sync`, `skill:docs-analysis`,
  `skill:document-chunker`。

Composition と Runtime の詳細は意図的に省略しています。

<!-- END ELLMOS BUNDLE DISCOVERY JA -->

## ライセンス

MIT ライセンス。`LICENSE` を参照してください。
