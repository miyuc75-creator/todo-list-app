# Todoリスト Webアプリ

Python + Flask で作った Todo 管理 Web アプリケーション。  
Google スプレッドシートにデータを保存し、Vercel で公開しています。

## 成果物リンク

| 種類 | URL |
|------|-----|
| **デモ（本番）** | https://todo-list-app-idyq.vercel.app |
| **ソースコード** | https://github.com/miyuc75-creator/todo-list-app |
| **開発ログ** | [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) |

## できること

- Todo の **新規登録・編集・一覧表示**
- **タイトル・内容・期日** の管理
- **Google スプレッドシート** への永続化（再読み込みしても残る）
- **日本語 UI**・**レスポンシブデザイン**（スマホ / PC 対応）
- **環境変数** による安全な認証情報管理

## 使用技術

| カテゴリ | 技術 |
|----------|------|
| 言語 | Python 3 |
| Web | Flask |
| データ | Google スプレッドシート（Google Sheets API） |
| 認証 | Google サービスアカウント |
| デプロイ | Vercel |
| 管理 | GitHub |

## フォルダ構成

```
todo-list-app/
├── app.py              # Flask アプリ本体
├── sheets.py           # Google スプレッドシート連携
├── styles.py           # CSS（Vercel 向けに Python に同梱）
├── api/index.py        # Vercel エントリーポイント
├── templates/          # HTML テンプレート
├── docs/DEVELOPMENT.md # 開発過程の記録
├── vercel.json         # Vercel 設定
├── requirements.txt
├── .env.example
└── .gitignore
```

## 開発の流れ

1. 要件整理・設計
2. Google Sheets API 連携（`sheets.py`）
3. Flask ルーティング・バリデーション（`app.py`）
4. 画面・CSS 作成（`templates/`, `styles.py`）
5. GitHub 公開 → Vercel デプロイ
6. 本番環境の CSS 問題を修正

詳細は [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) を参照。

## セキュリティ

- API キー・サービスアカウント JSON は **コードに直書きしない**
- ローカル: `.env` / 本番: Vercel Environment Variables
- `.env` と認証 JSON は `.gitignore` で除外

---

## セットアップ手順

### 1. ローカル起動

```bash
git clone https://github.com/miyuc75-creator/todo-list-app.git
cd todo-list-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env を編集（下記参照）
python app.py
```

→ http://127.0.0.1:5000

### 2. 環境変数（`.env`）

```env
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
GOOGLE_SPREADSHEET_ID=スプレッドシートID
FLASK_SECRET_KEY=ランダムな長い文字列
```

### 3. Google Cloud 設定

1. [Google Cloud Console](https://console.cloud.google.com/) で **Google Sheets API** を有効化
2. **サービスアカウント** を作成し JSON キーをダウンロード
3. スプレッドシートを作成し、1 行目に `id`, `title`, `content`, `due_date`, `created_at`, `updated_at` を設定
4. スプレッドシートをサービスアカウントの `client_email` に **編集者** として共有

JSON を 1 行にする:

```bash
python3 -c "import json; print(json.dumps(json.load(open('path/to/service-account.json'))))"
```

### 4. Vercel デプロイ

1. [Vercel](https://vercel.com/) で GitHub リポジトリをインポート
2. **Environment Variables** に上記 3 変数を登録
3. Deploy

---

## スプレッドシート列構成

| 列 | 内容 |
|----|------|
| id | UUID |
| title | タイトル（必須） |
| content | 内容 |
| due_date | 期日 |
| created_at | 登録日時 |
| updated_at | 更新日時 |

---

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| スプレッドシート接続エラー | `.env` / Vercel 環境変数、共有設定を確認 |
| 変更後に反映されない | Flask を再起動（`Ctrl+C` → `python app.py`） |
| Vercel で CSS が効かない | 最新版では `styles.py` に CSS を同梱済み |

---

## ライセンス

個人・学習用途で自由にご利用ください。
