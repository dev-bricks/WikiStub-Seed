# WikiStub-Seed

[EN](README.md) | [DE](README_de.md) | [ES](README_es.md) | **JA** | [RU](README_ru.md) | [ZH](README_zh-Hans.md)

**WikiStub-Seedは、AI支援研究・ドキュメント作成・学習システム・LLMワークフロー向けの多言語対応JSONナレッジフレームワークです。** 12の科学・文化ドメインにわたる630件のコンパクトなドイツ語/英語ナレッジスタブ、ES/ZH/JA/RU用の言語スロット、そしてバリデーション・エクスポート・翻訳のためのPythonツールを収録したキュレート済みデータセット `wikistub_seed.json` を提供します。

WikiStub-Seedはナレッジスタブのシードライブラリであり、Wikiではありません。

[![WikiStub-Seed smoke tests](https://github.com/file-bricks/WikiStub-Seed/actions/workflows/tests.yml/badge.svg)](https://github.com/file-bricks/WikiStub-Seed/actions/workflows/tests.yml)
![Stubs](https://img.shields.io/badge/stubs-630%2B-blue)
![Languages](https://img.shields.io/badge/languages-DE%20%7C%20EN%20%7C%20ES%20%7C%20ZH%20%7C%20JA%20%7C%20RU-orange)
![Format](https://img.shields.io/badge/format-JSON-green)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

## 収録内容

- `wikistub_seed.json` に DE/EN コンテンツと ES/ZH/JA/RU 用の準備済み言語スロットを持つ630件のナレッジスタブ
- 数学、物理学、化学、生物学、医学、心理学、AI、工学、社会、経済学、歴史、文化を含む12のトップレベルドメイン
- 短く中立的な定義と関連性ノートを持つ85のサブカテゴリ
- レガシーフィールド `definition_de`、`definition_en`、`relevance` を維持しつつ、正規の `definitions.{lang}` および `relevance_i18n.{lang}` マップを提供
- 統計・バリデーション・整合性チェック・Markdownエクスポートのための Python CLI ツール
- 将来の静的 Web/PWA 利用に向けた文書化済み `wikistub-seed-data-v1` エクスポート方向
- コアのインポート・エクスポート・バリデーション・CLI 利用に外部依存関係は不要

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

現在の権威あるソースは `wikistub_seed.json` です。`EXPORTFORMAT.md` は、Web/PWA・API・LLM エクスポート向けの安定したラッパーフォーマット `wikistub-seed-data-v1` を文書化しています。

## クイックスタート

```bash
git clone https://github.com/file-bricks/WikiStub-Seed.git
cd WikiStub-Seed

python wikistub_seed_cli.py --help
python wikistub_seed_cli.py stats
python wikistub_seed_cli.py check
python wikistub_seed_pipeline.py validate
python wikistub_seed_pipeline.py export --output --english
```

Windows では、`start.bat` が CLI エントリポイントを開きます。エクスポートされたファイルは `output/` に書き込まれます。このフォルダはローカルでバージョン管理されません。

## コアコマンド

| コマンド | 目的 |
|---|---|
| `python wikistub_seed_cli.py stats` | スタブ・カテゴリ・タグの統計を表示 |
| `python wikistub_seed_cli.py check` | JSON データセットの整合性チェックを実行 |
| `python wikistub_seed_pipeline.py validate` | パイプライン入力データをバリデート |
| `python wikistub_seed_pipeline.py export --output --english` | JSON データセットを Markdown にエクスポート |
| `python wikistub_seed_pipeline.py translate` | 設定済みの場合、不足している英語定義をオプションで翻訳 |

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
| `web_publisher/` | 静的 Web/PWA パブリッシャー（PWA・オフラインキャッシュ・検索・DE/EN 切り替え） |

## プライバシー

WikiStub-Seed はローカルファースト設計です。コア使用はローカルの JSON/Markdown ファイルの読み書きのみです。テレメトリーや自動ネットワーク通信はありません。

オプションの翻訳コマンドは、`ANTHROPIC_API_KEY` が設定され、オプションパッケージ `anthropic` がインストールされている場合にのみ外部 API を呼び出す可能性があります。

## ロードマップ

完了済み：

- 12のトップレベルドメインと85のサブカテゴリ
- 単一の JSON マスターファイルに630件のバイリンガルスタブ
- Markdown エクスポートと JSON 同期ツール
- GitHub Actions での CLI スモークテスト、および `wikistub_seed_cli.py check` と `wikistub_seed_pipeline.py validate` 向けの macOS/Linux ソーススモーク
- 検索とオフラインキャッシュを備えた静的 Web/PWA パブリッシャー（`web_publisher/`）
- DE/EN/ES/ZH/JA/RU 用の準備済み言語スロットを持つ `wikistub-seed-data-v1` スキーマラッパー

計画中：

- 統一されたタグのクリーンアップ
- Obsidian/GitHub Pages エクスポートパス
- オプションの埋め込みと検索 API

## Deutsch

**WikiStub-Seed ist ein mehrsprachig vorbereitetes JSON-Wissensgerüst für KI-gestützte Wissensarbeit.** Das Repository enthält 630 kompakte Wissens-Stubs mit Deutsch/Englisch-Inhalten und vorbereiteten Sprachslots für Spanisch, Chinesisch, Japanisch und Russisch, verteilt auf 12 Wissenschafts- und Kulturbereiche. Die Stubs sind kurz, neutral, versionierbar und für Automatisierung, Dokumentation, Lernsysteme und LLM-Kontexte geeignet.

WikiStub-Seed arbeitet standardmäßig lokal mit `wikistub_seed.json`. Die Kernfunktionen benötigen keine externen Pakete. Nur die optionale Übersetzungsfunktion nutzt externe API-Aufrufe, wenn ein API-Key gesetzt und das optionale Paket installiert wurde.

Wichtige Einstiegspunkte:

- `python wikistub_seed_cli.py stats` zeigt Statistik und Kategorien.
- `python wikistub_seed_cli.py check` prüft den Datenbestand.
- `python wikistub_seed_pipeline.py export --output --english` exportiert Markdown.
- `EXPORTFORMAT.md` beschreibt den geplanten stabilen Austauschstandard.
- `web_publisher/` enthält den fertigen statischen Web/PWA-Publisher mit Offline-Cache und DE/EN-Toggle.

## ライセンス

MIT ライセンス。`LICENSE` を参照してください。

このプロジェクトは無償のオープンソース寄贈です。責任はドイツ民法典第521条に基づく故意および重大な過失に限定され、MIT ライセンスの免責事項も適用されます。自己責任でご使用ください。
