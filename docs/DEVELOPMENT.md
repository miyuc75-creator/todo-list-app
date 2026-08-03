# 開発ログ — Todoリスト Webアプリ

このドキュメントは、Todoリスト Webアプリを **ゼロから構築した過程** を記録したものです。  
ポートフォリオとして「何を・なぜ・どの順番で作ったか」を確認できます。

---

## プロジェクトの目的

| 項目 | 内容 |
|------|------|
| 作りたいもの | Todo を登録・編集できる Web アプリ |
| データ保存 | Google スプレッドシート（DB なしで運用可能） |
| 公開方法 | GitHub → Vercel でデプロイ |
| 対象ユーザー | 自分（プログラミング初心者） |

**学びたかったこと**

- Python + Flask で Web アプリを作る流れ
- 外部 API（Google Sheets）との連携
- 環境変数を使った安全な設定管理
- GitHub と Vercel を使った公開の流れ

---

## 要件整理（開発前）

### 必須機能

1. Todo の新規登録
2. 登録済み Todo の編集
3. Todo 一覧の表示
4. 各 Todo に「タイトル・内容・期日」を設定
5. Google スプレッドシートへの保存
6. 登録・編集後は一覧画面へ戻る
7. 入力不足時のエラーメッセージ
8. スマホ・PC 両対応のレスポンシブデザイン
9. 画面表示は日本語

### セキュリティ要件（最重要）

- API キー・サービスアカウント JSON を **コードに直書きしない**
- ローカルは `.env`、本番は Vercel の Environment Variables
- `.env` や JSON ファイルは `.gitignore` で除外
- ログや画面に認証情報を出さない

---

## アーキテクチャの設計

### なぜこの構成にしたか

```
ブラウザ → Flask (app.py) → sheets.py → Google スプレッドシート
                ↓
         templates/ + static/
```

| 判断 | 理由 |
|------|------|
| Flask を選んだ | 軽量で学習しやすく、小規模 Web アプリに向いている |
| スプレッドシートを DB 代わりに | 無料で始めやすく、データを GUI で確認できる |
| `sheets.py` を分離 | 画面処理とデータ処理を分け、読みやすく保守しやすくする |
| `api/index.py` を追加 | Vercel のサーバーレス実行に対応するため |

### スプレッドシートの列設計

| 列名 | 用途 |
|------|------|
| `id` | UUID（重複しない識別子） |
| `title` | タイトル（必須） |
| `content` | 内容 |
| `due_date` | 期日（HTML date 入力） |
| `created_at` | 登録日時 |
| `updated_at` | 更新日時 |

---

## 開発ステップ（時系列）

### Step 1 — プロジェクトの土台

**作成ファイル:** `.gitignore`, `.env.example`, `requirements.txt`

- 最初に **機密情報を Git から除外** する設定を用意
- 必要パッケージを固定: Flask, gspread, google-auth, python-dotenv
- `.env.example` には **変数名だけ** を記載（値は空）

```text
GOOGLE_SERVICE_ACCOUNT_JSON=
GOOGLE_SPREADSHEET_ID=
FLASK_SECRET_KEY=
```

### Step 2 — Google スプレッドシート連携

**作成ファイル:** `sheets.py`

実装した主な処理:

- 環境変数 `GOOGLE_SERVICE_ACCOUNT_JSON` を `json.loads()` で読み込み
- `GOOGLE_SPREADSHEET_ID` で対象シートを特定
- 1 行目にヘッダー行がなければ自動作成
- CRUD 相当: 一覧取得 / ID 検索 / 新規追加 / 更新

**エラー設計:**

- 環境変数未設定 → 原因が分かるメッセージ
- 接続失敗 → アプリを落とさず `SheetsError` として上位に返す

### Step 3 — Flask アプリ本体

**作成ファイル:** `app.py`

| ルート | 処理 |
|--------|------|
| `GET/POST /` | 一覧表示 + 新規登録 |
| `GET/POST /edit/<id>` | 編集画面 + 更新 |

**バリデーション:**

- タイトル空 → 「タイトルは必須です」
- 存在しない ID → 一覧へリダイレクト
- 登録・更新成功 → フラッシュメッセージ + 一覧へリダイレクト

### Step 4 — 画面（HTML）

**作成ファイル:** `templates/index.html`, `templates/edit.html`

- 日本語 UI
- 一覧画面: 登録フォーム + Todo カード一覧 + 編集ボタン
- 編集画面: 既存値をフォームに表示 + 「更新する」「一覧へ戻る」
- 期日は `<input type="date">` を使用

### Step 5 — デザイン（CSS）

**作成ファイル:** `static/style.css`

- 白ベースのカード UI
- 期日バッジで視認性を向上
- `@media (max-width: 640px)` でスマホ縦並び対応
- 外部テンプレート・有料サービスは不使用

### Step 6 — Vercel デプロイ設定

**作成ファイル:** `vercel.json`, `api/index.py`

- `@vercel/python` で Flask をサーバーレス実行
- `/static/*` は静的ファイルとして配信
- それ以外のリクエストは `api/index.py` 経由で Flask に渡す

### Step 7 — ドキュメント

**作成ファイル:** `README.md`, `docs/DEVELOPMENT.md`（本ファイル）

- README: セットアップ・デプロイ手順
- DEVELOPMENT.md: 開発の思考過程（ポートフォリオ用）

---

## セキュリティ設計の詳細

### 環境変数一覧

| 変数名 | 用途 |
|--------|------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | サービスアカウント JSON（1 行文字列） |
| `GOOGLE_SPREADSHEET_ID` | スプレッドシート ID |
| `FLASK_SECRET_KEY` | Flask セッション用秘密鍵 |

### .gitignore で除外しているもの

- `.env`
- `service-account.json`, `credentials.json`, `secret.json`
- `venv/`, `__pycache__/`

### 確認コマンド

```bash
git check-ignore -v .env service-account.json
git status   # .env が含まれていないこと
```

---

## 動作確認チェックリスト

| # | 確認項目 | 結果 |
|---|----------|------|
| 1 | ローカル起動 (`python app.py`) | ✅ |
| 2 | 一覧画面表示 | ✅ |
| 3 | タイトル空でエラー表示 | ✅ |
| 4 | 存在しない ID で一覧へ戻る | ✅ |
| 5 | CSS 読み込み（ローカル） | ✅ |
| 6 | 環境変数未設定時のエラー表示 | ✅ |
| 7 | 機密情報がコード内にない | ✅ |
| 8 | `.env` が Git 追跡外 | ✅ |
| 9 | Todo 登録 → スプレッドシート保存 | ✅ |
| 10 | Todo 編集 → スプレッドシート更新 | ✅ |
| 11 | Vercel デプロイ | ✅ |
| 12 | Vercel 本番 CSS 表示 | ✅ |

**本番 URL:** https://todo-list-app-idyq.vercel.app

---

## 直面した課題と対処

### 課題 1: Python 3.9 で型ヒントエラー

**現象:** `dict | None` が Python 3.9 では使えない

**対処:** `sheets.py` 先頭に `from __future__ import annotations` を追加

### 課題 2: 認証情報を GitHub に載せない

**対処:**

- コード内直書き禁止
- `.gitignore` で除外
- Vercel は Environment Variables のみ使用

### 課題 3: 接続失敗時にアプリが止まる

**対処:** `SheetsError` を定義し、Flask 側で `flash()` して画面表示

### 課題 4: Vercel で CSS が適用されない

**現象:** ローカルでは正常だが、Vercel 上では `<style></style>` が空になり、登録ボタンが灰色のまま

**原因:** Vercel のサーバーレス環境に `public/static/style.css` が同梱されない

**対処:** CSS を `styles.py` に Python コードとして同梱し、HTML にインラインで埋め込む方式に変更

### 課題 5: `.env` 設定前に起動した Flask が接続エラーを表示

**現象:** 古いプロセスが環境変数なしで動き続ける

**対処:** Flask を再起動（`Ctrl+C` → `python app.py`）

---

## Git コミット履歴（開発の流れ）

このリポジトリは、開発ステップに沿ったコミット履歴になっています。

```bash
git log --oneline
```

| コミット | 内容 |
|----------|------|
| 1 | プロジェクト初期設定 |
| 2 | Google スプレッドシート連携 |
| 3 | Flask ルーティングとバリデーション |
| 4 | HTML テンプレート |
| 5 | レスポンシブ CSS |
| 6 | Vercel デプロイ設定 |
| 7 | README と開発ログ |
| 8 | Vercel CSS 修正（styles.py 同梱） |
| 9 | 成果物ドキュメント更新 |

---

## 成果物まとめ

| 項目 | 内容 |
|------|------|
| 本番アプリ | https://todo-list-app-idyq.vercel.app |
| GitHub | https://github.com/miyuc75-creator/todo-list-app |
| データ保存 | Google スプレッドシート |
| 状態 | **完成・公開済み** |

---

## 今後の改善案

- [ ] Todo の削除機能
- [ ] 完了チェック（done 列の追加）
- [ ] 期日順・登録日順のソート切り替え
- [ ] ユニットテストの追加
- [ ] GitHub Actions で lint / テスト自動化

---

## ポートフォリオとしてのアピールポイント

1. **要件定義から実装まで一貫** — 機能・セキュリティ・デプロイを最初から設計
2. **セキュリティ意識** — 環境変数・gitignore・機密情報の分離
3. **モジュール分割** — `app.py`（画面）と `sheets.py`（データ）の責務分離
4. **エラーハンドリング** — ユーザー向けメッセージとアプリの安定性
5. **本番公開を見据えた構成** — Vercel + GitHub の CI/CD 的ワークフロー

---

*最終更新: 2026年8月*
