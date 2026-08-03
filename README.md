# Todoリスト Webアプリ

Google スプレッドシートにデータを保存する、シンプルな Todo 管理 Web アプリです。  
タイトル・内容・期日を登録・編集でき、スマートフォンと PC の両方で見やすいデザインになっています。

> **ポートフォリオ向け:** 設計から実装までの過程は [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) に記録しています。  
> Git のコミット履歴も開発ステップ順になっているので、作成の流れを追えます。

---

## 1. アプリの概要

- Todo の新規登録・編集・一覧表示
- データは Google スプレッドシートに保存（再読み込みしても残る）
- 各 Todo には UUID で重複しない ID を付与
- タイトル未入力時は分かりやすいエラーメッセージを表示
- 日本語 UI、レスポンシブデザイン

---

## 2. 使用技術

| 種類 | 技術 |
|------|------|
| 言語 | Python 3 |
| Web フレームワーク | Flask |
| データ保存 | Google スプレッドシート（Google Sheets API） |
| 認証 | Google サービスアカウント |
| デプロイ | Vercel |
| バージョン管理 | GitHub |

---

## 3. フォルダ構成

```
todoリストアプリ/
├── app.py              # Flask アプリ本体（ルーティング・画面処理）
├── sheets.py           # Google スプレッドシート連携
├── api/
│   └── index.py        # Vercel 用エントリーポイント
├── public/
│   └── static/
│       └── style.css   # スタイルシート（Vercel / ローカル共通）
├── templates/
│   ├── index.html      # 一覧・登録画面
│   └── edit.html       # 編集画面
├── requirements.txt    # Python パッケージ一覧
├── vercel.json         # Vercel 設定
├── .env.example        # 環境変数の例（値は書かない）
├── .gitignore          # Git 除外設定
└── README.md           # このファイル
```

### 処理の流れ

1. ユーザーがブラウザでフォームを送信
2. `app.py` が入力内容を検証（タイトル必須など）
3. `sheets.py` が Google スプレッドシートに読み書き
4. 登録・更新後は一覧画面（`/`）へリダイレクト
5. エラー時は画面にメッセージを表示（アプリは停止しない）

---

## 4. ローカルでの起動方法

### 前提

- Python 3.10 以上
- Google スプレッドシートとサービスアカウントの準備（下記手順 5〜7）

### 手順

```bash
# 1. プロジェクトフォルダへ移動
cd todoリストアプリ

# 2. 仮想環境を作成・有効化（推奨）
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. パッケージをインストール
pip install -r requirements.txt

# 4. 環境変数を設定（.env.example をコピーして編集）
cp .env.example .env
# .env をエディタで開き、値を設定（詳細は「7. .env の設定方法」）

# 5. アプリを起動
python app.py
```

ブラウザで [http://127.0.0.1:5000](http://127.0.0.1:5000) を開いてください。

---

## 5. Google Cloud で Google Sheets API を有効化する方法

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（または既存プロジェクトを選択）
3. 左メニュー **「API とサービス」→「ライブラリ」**
4. 「Google Sheets API」を検索
5. **「有効にする」** をクリック

---

## 6. サービスアカウントの作成方法

1. Google Cloud Console で **「API とサービス」→「認証情報」**
2. **「認証情報を作成」→「サービスアカウント」**
3. 名前を入力（例: `todo-app-sheets`）して作成
4. 作成したサービスアカウントをクリック
5. **「キー」タブ →「鍵を追加」→「新しい鍵を作成」→ JSON**
6. ダウンロードした JSON ファイルは **ローカルの安全な場所に保存**
   - ⚠️ このファイルを GitHub にアップロードしないでください

---

## 7. スプレッドシートをサービスアカウントに共有する方法

1. [Google スプレッドシート](https://sheets.google.com/) で新しいシートを作成
2. 1 行目に以下の列名を入力（アプリ起動時に自動設定される場合もあります）:

   | A | B | C | D | E | F |
   |---|---|---|---|---|---|
   | id | title | content | due_date | created_at | updated_at |

3. スプレッドシート URL から ID を控える  
   例: `https://docs.google.com/spreadsheets/d/【ここがスプレッドシートID】/edit`
4. 右上 **「共有」** をクリック
5. サービスアカウントのメールアドレス（JSON 内の `client_email`）を追加
6. 権限を **「編集者」** に設定

---

## 8. .env の設定方法

`.env.example` をコピーして `.env` を作成し、次の 3 つを設定します。

```env
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
GOOGLE_SPREADSHEET_ID=your-spreadsheet-id-here
FLASK_SECRET_KEY=ランダムな長い文字列
```

### 各項目の説明

| 変数名 | 説明 |
|--------|------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | サービスアカウント JSON の**中身全体**を 1 行の文字列として設定 |
| `GOOGLE_SPREADSHEET_ID` | スプレッドシート URL の ID 部分 |
| `FLASK_SECRET_KEY` | Flask のセッション用秘密鍵（任意の長いランダム文字列） |

### JSON を 1 行にする例（macOS / Linux）

```bash
python3 -c "import json; print(json.dumps(json.load(open('path/to/service-account.json'))))"
```

出力された 1 行を `.env` の `GOOGLE_SERVICE_ACCOUNT_JSON=` の右側に貼り付けます。

---

## 9. GitHub にアップロードする手順

```bash
git init
git add .
git status   # .env や JSON が含まれていないか必ず確認
git commit -m "Initial commit: Todo list app"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/リポジトリ名.git
git push -u origin main
```

---

## 10. Vercel にデプロイする手順

1. [Vercel](https://vercel.com/) にログイン
2. **「Add New…」→「Project」**
3. GitHub リポジトリを選択してインポート
4. Framework Preset は **Other** のままで OK
5. **Environment Variables** を設定（次のセクション参照）
6. **Deploy** をクリック

デプロイ後、表示された URL（例: `https://your-app.vercel.app`）でアプリにアクセスできます。

---

## 11. Vercel の Environment Variables の登録方法

Vercel プロジェクトの **Settings → Environment Variables** で以下を追加します。

| Name | Value | Environment |
|------|-------|-------------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | サービスアカウント JSON（1 行） | Production, Preview, Development |
| `GOOGLE_SPREADSHEET_ID` | スプレッドシート ID | Production, Preview, Development |
| `FLASK_SECRET_KEY` | ランダムな秘密鍵 | Production, Preview, Development |

保存後、**Redeploy** して反映させてください。

---

## 12. 機密情報が GitHub に含まれていないことを確認する方法

```bash
# .env が Git 管理外か確認
git check-ignore -v .env

# ステージング前に機密ファイルが含まれていないか確認
git status

# コミット履歴に秘密鍵らしき文字列がないか（任意）
git grep -i "private_key" || echo "private_key は見つかりませんでした"
git grep -i "GOOGLE_SERVICE_ACCOUNT" -- ':!.env.example' || true
```

**確認ポイント**

- [ ] `.env` が `.gitignore` に含まれている
- [ ] `service-account.json` などがコミットされていない
- [ ] `.env.example` には変数名のみで、実際の値がない
- [ ] `app.py` / `sheets.py` に API キーや JSON が直書きされていない

---

## スプレッドシートの列構成

| 列 | 内容 |
|----|------|
| id | UUID（自動生成） |
| title | タイトル（必須） |
| content | 内容 |
| due_date | 期日（YYYY-MM-DD） |
| created_at | 登録日時（UTC） |
| updated_at | 更新日時（UTC） |

---

## トラブルシューティング

| 症状 | 確認すること |
|------|----------------|
| 環境変数エラー | `.env` または Vercel の Environment Variables |
| スプレッドシート接続エラー | サービスアカウントへの共有、JSON の形式 |
| 静的ファイルが表示されない | `static/style.css` がリポジトリに含まれているか |
| Vercel で 500 エラー | Vercel の Function Logs を確認 |

---

## ライセンス

個人・学習用途で自由にご利用ください。
