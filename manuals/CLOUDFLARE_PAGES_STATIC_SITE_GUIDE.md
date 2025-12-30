# Cloudflare Pages で静的サイト公開（GitHub連携）ガイド

目的：Playストア検索だけでは届かない層を、Web（検索/LLM/シェア）経由で獲得するために、**Markdown中心の静的サイト**を Cloudflare Pages で公開し、**GitHub連携で自動デプロイ**できる状態を作る。

重要：公開用Webは「説明・信頼構築・導線」に限定し、**予測ロジックの詳細・学習手法・パラメータ等は一切公開しない**（Playストア審査・法務・炎上対策として有効）。

## 1. 現状の環境整理（このリポジトリ）

このリポジトリは **Python中心の予測/分析プロジェクト**で、ドキュメントは `docs/` 配下にすでに階層化されています。

確認できたポイント：
- `docs/` 配下に `index.md` があり、ドキュメントの情報設計（setup/specs/phases/reports 等）は既にある
- ただし **MarkdownをHTMLに変換するサイトジェネレータ（MkDocs等）の設定ファイルは未導入**（`mkdocs.yml` などが見当たらない）
- `github_pages_api/` は GitHub Pages 用の「静的 JSON 配信 + index.html」用途で、**公開リポジトリを分離する運用思想**が既にある（機密を混ぜない）
- `pwa/` には PWA 資産（`manifest.json`, `service-worker.js`, `offline.html` 等）があり、Web公開資産として流用できる可能性がある

結論：
- **「公開用Webサイト（獲得用）」は、機密/重量級のコード資産と分離するのが安全**
- ただし、運用コストを抑えるために「同一リポジトリでCloudflare Pagesに公開」も可能（ソースはPrivateでもサイトはPublicにできる）

## 2. 推奨方針（結論）

### 推奨：公開用Webサイトは分離（Public推奨）
- リポジトリ例：`numbers4-web`（静的サイト専用）
- 収録するもの：
  - `index.md`（ランディング）
  - `privacy/`（プライバシーポリシー）
  - `support/`（問い合わせ・FAQ）
  - `release/`（リリースノートの公開版）
  - （必要なら）`pwa/` の資産を最小限だけ

理由：
- 検索/LLMで拾われる = 半永久的に引用され得るため、後から「消したい内部情報」が残り続けるリスクを避ける
- Playストア審査・法務観点でも安全側に倒せる
- 誤って「内部仕様・学習/予測ロジック・運用情報」を出さないようにする
- Cloudflare Pages は PR プレビューが強いので、**公開用コンテンツだけ**がレビュー対象になる

### 代替：このリポジトリ内に `web/` を作ってPages公開
- リポジトリを増やしたくない場合に有効
- 注意：公開範囲を厳密に限定する（ビルド出力に `docs/` 全体を載せない/内部手順を除外する）

## 3. 生成方式（静的HTML / Markdown）

Cloudflare Pagesは「静的HTML」を配信します。Markdownをそのまま置くだけではHTMLにならないため、**ビルドでHTMLに変換**するのが基本です。

### 推奨：MkDocs（Pythonで完結、Markdown中心）
- このプロジェクトはPython前提なので、Nodeを増やさずに済む
- 生成物が完全に静的で、SEOにもLLM参照にも向く（SPAにならない）

最小構成の考え方：
- `mkdocs.yml`（サイト設定）
- `docs/`（Markdown）
- `mkdocs build` → `site/`（HTML出力）

⚠️ 安全のための推奨運用（重要）：
- **このリポジトリの `docs/` は触らない**（内部向けのため）
- 公開用の `numbers4-web/docs/` は **新規に作る**
- 必要な説明だけを **書き直す / 要約する**（内部資料の直接流用はしない）

理由：
- 内部向けdocsは「LLMに見せる前提」で書かれていない
- 将来「公開してはいけない記述」が混ざる可能性が高い

※重要：MkDocsは「`docs/` 配下しか参照できない」ため、`docs/` 外への相対リンクは壊れます。公開サイトは `numbers4-web/docs/` の中で完結させてください。

## 4. 情報設計（検索/LLMに拾われやすい構造）

### 4.1 URL設計
- 変えないURLを先に決める（リンク資産が積み上がるため）
- 例：
  - `/` ランディング
  - `/download/` ストア導線
  - `/privacy/` プライバシー
  - `/support/` サポート（FAQ/問い合わせ/不具合報告）
  - `/release/` リリースノート

### 4.2 1ページの構造（LLM/検索両対応）
- タイトル直下に「3〜5行の要約（何ができる/誰向け/導線）」
- 見出しは `h2/h3` を中心に階層を揃える（長文の壁を作らない）
- 重要語を本文に明示する（「ナンバーズ4」「予想」「統計」「エンタメ戦略」「オフライン」「TFLite」など）
- 画像だけで説明しない（代替テキスト/本文説明を必ず添える）

### 4.3 LLM向けの追加ファイル（推奨）
- `llms.txt`（サイトの要約・主要ページ一覧・利用上の注意）
  - 置き場所：サイトルート（例：`/llms.txt`）
- 位置づけ：これはSEO（検索順位向上）のためではなく、**LLMによる要約・引用時の誤解防止（引用精度向上）**が主目的です。

## 5. Cloudflare Pages セットアップ手順（GitHub連携）

### 5.1 事前に決めること
- どのリポジトリで公開するか（推奨：`numbers4-web`）
- 公開ドメイン（Cloudflareの `*.pages.dev` で開始 → 後で独自ドメイン）
- ビルド方式（推奨：MkDocs）

### 5.2 Cloudflare Pages の作成
1. Cloudflare Dashboard → **Workers & Pages** → **Create** → **Pages**
2. **Connect to Git** を選択し、GitHubを接続
3. 対象リポジトリ/ブランチを選ぶ（例：`main`）
4. Build settings を設定

MkDocs想定（初期段階のおすすめ）：
- **Build command**: `python -m pip install -r requirements-docs.txt && mkdocs build`
- **Build output directory**: `site`

補足：
- `--strict` はリンク切れ等をエラーにするため品質が上がりますが、最初は「とにかく通す」方がスムーズです。安定したら `mkdocs build --strict` に切り替えます。
- Pythonバージョン指定が必要なら、Cloudflareの設定（Build image / env）に合わせて調整します。
- Cloudflare Pages のビルド環境によっては `python3` コマンドが無いことがあります。Build command は `python`（推奨：`python -m pip`）を使ってください。

### 5.3 プレビュー運用
- Pull Request を作ると **Preview Deployment** が作られ、レビューしやすい
- main にマージで本番反映

### 5.4 独自ドメイン（任意）
- Pages → Custom domains から設定
- `example.com` / `www.example.com` などを追加

## 6. SEOの最低限チェックリスト

Cloudflare Pages + 静的HTMLの場合、最低限これだけ押さえると強いです。

- `sitemap.xml` を出す（MkDocs/Material が自動生成）
- `robots.txt` を用意する（クロール拒否をしない）
- `canonical`（正規URL）を設定する（テーマが `site_url` を元に自動設定）
- ページタイトルとdescriptionを各ページに入れる
- 404ページ（最低限）

実装メモ（このリポジトリの現状）：

- `sitemap.xml`
  - `mkdocs.yml` の `site_url` を正しい正規URL（例：`https://numbers4-web.pages.dev/`）に設定する
  - Material テーマは `sitemap.xml` をテンプレートとして生成する（追加プラグイン不要）
- `robots.txt`
  - `docs/robots.txt` を作成する（MkDocsが静的ファイルとして site 直下にコピーする）
  - `Sitemap: https://numbers4-web.pages.dev/sitemap.xml` を記載する
- `canonical`
  - Material テーマは `site_url` を元に `<link rel="canonical" ...>` を出す
  - Cloudflare Pages の Preview URL（`https://<hash>.numbers4-web.pages.dev/...`）で見た場合も、正規URLへ寄せられる

## 7. 次のアクション（おすすめ順）

0) Playストア表現とWeb表現のトーンを一致させる（誇大表現防止）
1) 公開用サイトを「分離リポジトリ」で作る（推奨：分離）
2) 公開するページ範囲を決める（内部実装/運用/学習詳細は出さない）
3) MkDocsの最小構成でビルドが通るところまで作る（まずは `mkdocs build`）
4) Cloudflare Pages をGitHub連携し、PRプレビューで回す
5) 安定後に `--strict` を有効化してリンク品質を担保する

## 8. Webページ公開までの実行計画（チェックリスト）

### Phase 0: 事前整合（完了）
- [x] Playストアの説明文/注意書きと、Webの表現トーンを合わせる（完了：テンプレに反映済み）
- [x] Webで「言っていいこと/言わないこと」を決める（完了：ガイドおよびテンプレに反映済み）

### Phase 1: 公開用リポジトリ構成の作成（完了）
- [x] 新規リポジトリ `numbers4-web` 用の構成を作成（完了：`web_templates/numbers4-web/` に集約）
- [x] 初期構成を作成
  - [x] `mkdocs.yml`
  - [x] `requirements-docs.txt`
  - [x] `docs/index.md`（ランディング）
  - [x] `docs/numbers4/index.md`（ナンバーズ4解説）
  - [x] `docs/results/index.md`（当選番号・静的埋め込み対応）
  - [x] `docs/privacy/index.md`
  - [x] `docs/support/index.md`
  - [x] `docs/release/index.md`

### Phase 2: コンテンツの実装（完了）
- [x] ランディングの主要要素作成（完了：LSTM予測・投資管理の詳説、誤認防止コピー）
- [x] `llms.txt` の作成（完了：`docs/llms.txt` に配置）
- [x] 当選番号のビルド時埋め込みスクリプト作成（完了：`scripts/generate_results_static.py`）

### Phase 3: Cloudflare Pages 接続（次ステップ）
- [ ] GitHubで新規リポジトリ `numbers4-web` を作成し、テンプレを移植
- [ ] Cloudflare Pages を作成し GitHub を接続
- [ ] `Build command`: `python -m pip install -r requirements-docs.txt && python scripts/generate_results_static.py && mkdocs build`
- [ ] `Build output directory`: `site`
- [ ] PRプレビューで表示/リンク/日本語崩れを確認

### Phase 4: 品質強化（半日〜）
- [ ] 主要ページのタイトル/要約を整える（見出し階層を揃える）
- [ ] リンク切れが減ったら `mkdocs build --strict` に切り替える
- [ ] `robots.txt` / `sitemap.xml` の整備（必要ならMkDocsプラグインで自動化）

完了条件（Definition of Done）：
- Cloudflare Pages 本番URLで `index` / `privacy` / `support` が表示できる
- Google Play への導線が機能している
- 公開サイトに内部情報（実装/学習/運用の詳細）が含まれていない

---

必要なら、次のステップとして
- 公開用ディレクトリ/リポジトリ構成案（実ファイルの雛形）
- MkDocsの最小 `mkdocs.yml` と `requirements-docs.txt`
- `llms.txt` のテンプレ
まで、このリポジトリに合わせて“実装込み”で用意できます。

## 9. 公開用リポジトリ雛形（このリポジトリ内テンプレ）

このリポジトリには、`numbers4-web` をそのまま作ってOKな雛形を配置しています。

- テンプレ場所：`web_templates/numbers4-web/`

完成形の構成（雛形）：

```
numbers4-web/
├─ README.md
├─ mkdocs.yml
├─ requirements-docs.txt
├─ .gitignore
├─ docs/
│  ├─ index.md
│  ├─ numbers4/
│  │  └─ index.md
│  ├─ results/
│  │  └─ index.md
│  ├─ download/
│  │  └─ index.md
│  ├─ privacy/
│  │  └─ index.md
│  ├─ support/
│  │  └─ index.md
│  ├─ release/
│  │  └─ index.md
│  ├─ assets/
│  │  ├─ images/
│  │  │  └─ app_screenshot.png
│  │  └─ css/
│  │     └─ extra.css
│  └─ llms.txt
└─ site/  # mkdocs build 出力（gitignore）
```

### 移植手順（最短）

1) GitHubで新規リポジトリ `numbers4-web` を作成（Public推奨）
2) このテンプレの中身を新規リポジトリのルートにコピー
3) Cloudflare Pages をGitHub連携し、以下でビルド

- Build command: `python -m pip install -r requirements-docs.txt && python scripts/generate_results_static.py && mkdocs build`
- Build output directory: `site`

---

## 10. 当選番号APIも分離する（推奨：numbers4-api-cf）

Webサイト（`numbers4-web`）とは別に、当選番号JSONを配信する **API専用リポジトリ** を用意すると、責務分離が明確になり、将来の拡張（Workers / R2）にも移行しやすくなります。

### 10.1 分離する理由

- API と Web の責務が明確（運用・更新・障害切り分けがしやすい）
- Web を壊さず API だけ差し替え可能（URLを差し替えるだけで移行できる）
- Workers / R2 へ発展させやすい（後から実装型に移行してもURL体系を維持しやすい）

### 10.2 最小構成（Cloudflare Pagesで静的JSON配信）

推奨リポジトリ名：`numbers4-api-cf`（API専用・webとは分離）

```
numbers4-api-cf/
├─ api/
│  └─ v1/
│     ├─ latest.json
│     └─ numbers4_all_min.json
└─ _headers  # CORS/キャッシュ（推奨）
```

Cloudflare Pages 設定（最小）：

- Framework preset：None
- Build command：なし（空）
- Build output directory：`/`（リポジトリ直下）

配信URL例：

- `https://<project>.pages.dev/api/v1/latest.json`
- `https://<project>.pages.dev/api/v1/numbers4_all_min.json`

### 10.3 アプリ改修を最小にするポイント

- `/api/v1/` とファイル名（`latest.json` / `numbers4_all_min.json`）を固定する
- JSONスキーマ（キー名・型）を変えない（変えるなら `/api/v2/` を切る）

### 10.4 このリポジトリ内の雛形

- テンプレ場所：`web_templates/numbers4-api-cf/`
