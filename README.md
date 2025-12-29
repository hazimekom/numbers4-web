# numbers4-web（公開用Webサイト）テンプレ

このフォルダは、公開用Webサイトを **別リポジトリ（推奨：Public）** として運用するための最小雛形です。

- 目的：検索/LLM/シェア経由の獲得導線
- 原則：公開は「説明・信頼構築・導線」だけ。**予測ロジック詳細・学習手法・パラメータ等は公開しない**
- 内部向け資料（このリポジトリの `docs/`）は直接流用しない

## 1) 新規リポジトリ作成

GitHubで `numbers4-web` を作成し、このテンプレの内容を丸ごと配置します。

推奨構成：
- リポジトリ直下に `mkdocs.yml`
- `docs/` にMarkdown（公開用に書き直したもの）

## 2) ローカルで確認（任意）

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

ブラウザで `http://127.0.0.1:8000/` を確認します。

## 3) Cloudflare Pages 設定（GitHub連携）

Cloudflare Pages → Create → Connect to Git で `numbers4-web` を選択。

初期段階（まず通す）：
- Build command: `pip install -r requirements-docs.txt && python scripts/generate_results_static.py && mkdocs build`
- Build output directory: `site`

補足：`python scripts/generate_results_static.py` は、当選番号ページの静的表示部分に実データを埋め込む前処理です。
（API取得に失敗した場合はビルドを失敗させ、例示データが公開される事故を防ぎます）

参照するAPIは環境変数で差し替えできます：

- `NUMBERS4_API_BASE`（例：`https://<numbers4-api-cf>.pages.dev/api/v1`）

これにより、Web本体を大きく変えずに API 配信元だけ移行できます。

安定後（リンク品質を上げる）：
- Build command: `pip install -r requirements-docs.txt && python scripts/generate_results_static.py && mkdocs build --strict`

## 4) 置いてあるもの

- `mkdocs.yml`：MkDocs設定（Materialテーマ、最小構成）
- `requirements-docs.txt`：ドキュメント用依存（MkDocs + Material）
- `docs/`：公開ページ
  - `index.md`：ランディング（アプリ紹介）
  - `numbers4/`：ナンバーズ4の基本説明（検索流入の主力）
  - `results/`：当選番号（最新＋過去）
  - `download/`：ストア導線
  - `privacy/`：プライバシー
  - `support/`：FAQ/問い合わせ
  - `release/`：リリースノート
  - `assets/`：画像・CSS（任意）
  - `llms.txt`：LLMが要約・引用する際の誤解防止（SEO目的ではない）

## 5) 注意（重要）

- 誇大表現を避ける（Playストアの説明文とWebのトーンを合わせる）
- 「当たる」「必ず勝てる」等の断定表現は避ける
- 内部実装の詳細は出さない（半永久的引用リスクを前提に運用）
