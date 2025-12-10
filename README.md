# Kenn_Zenn_Publisher

## 概要

Zenn 記事の生成と公開を自動化する FastAPI サービスです。Docker 環境に Zenn CLI を統合し、OpenAI API を使った記事生成、手動コンテンツでの記事作成、GitHub への自動公開をサポートします。

## 主な機能

- ✨ **AI 記事生成**: OpenAI API を使ってタイトルから記事を自動生成
- 📝 **手動記事作成**: 用意したコンテンツで Zenn 記事を作成
- 🚀 **自動公開**: GitHub への commit/push で記事を公開
- 🐳 **Docker 統合**: Python + Node.js + Zenn CLI を 1 コンテナで完結
- 🔄 **ホットリロード**: コード変更が即座に反映

## 技術スタック

<p style="display: inline">
  <img src="https://qiita-user-contents.imgix.net/https%3A%2F%2Fimg.shields.io%2Fbadge%2F-Node.js-000000.svg%3Flogo%3Dnode.js%26style%3Dfor-the-badge?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=58a7faca7c79608cc0f2f1dd1e56645c">
  <img src="https://qiita-user-contents.imgix.net/https%3A%2F%2Fimg.shields.io%2Fbadge%2F-Python-F2C63C.svg%3Flogo%3Dpython%26style%3Dfor-the-badge?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=c17144ccc12f9c19e9dbba2eec5c7980">
  <img src="https://qiita-user-contents.imgix.net/https%3A%2F%2Fimg.shields.io%2Fbadge%2F-fastapi-009688.svg%3Flogo%3DFastAPI%26style%3Dfor-the-badge%26logoColor%3Dblack?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=8dd66665fcc23dfcdeb481e9f1e62dc4">
  <img src="https://qiita-user-contents.imgix.net/https%3A%2F%2Fimg.shields.io%2Fbadge%2F-Docker-1488C6.svg%3Flogo%3Ddocker%26style%3Dfor-the-badge?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=14a6094ef3229a37e7d5126c6cb6ac7a">
  <img src="https://qiita-user-contents.imgix.net/https%3A%2F%2Fimg.shields.io%2Fbadge%2F-githubactions-FFFFFF.svg%3Flogo%3Dgithub-actions%26style%3Dfor-the-badge?ixlib=rb-4.0.0&auto=format&gif-q=60&q=75&s=2476e16acd4c54fb4bf78852e6390101">
</p>

---

## セットアップ

### 前提条件

- Docker & Docker Compose
- Git
- OpenAI API Key
- GitHub Personal Access Token (repo 権限)

### 1. リポジトリをクローン

```bash
git clone https://github.com/kensan0123/Kenn_Zenn_Publisher.git
cd Kenn_Zenn_Publisher
```

### 2. 環境変数を設定

`.env.example`を`.env`にコピーして編集:

```bash
cp .env.example .env
```

**.env の設定内容:**

```bash
# OpenAI API設定
OPENAI_API_KEY=sk-your-openai-api-key-here

# GitHub設定（Zenn公開用）
GITHUB_PAT=ghp_your_github_personal_access_token
GITHUB_USER=your-github-username

# Git設定（コミット時に使用）
USER_NAME=Your Name
USER_EMAIL=your.email@example.com

# アプリケーション設定
ARTICLE_DIR=/app/articles
ROOT_DIR=/app
```

**GitHub Personal Access Token の取得方法:**

1. GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" をクリック
3. `repo` 権限にチェックを入れる
4. 生成されたトークンを`GITHUB_PAT`に設定

### 3. Docker コンテナを起動

```bash
docker-compose up -d --build
```

起動ログを確認:

```bash
docker-compose logs -f
```

以下のようなログが表示されれば成功:

```
[INFO] Starting Zenn Publisher API...
[INFO] Git configured: Your Name <your.email@example.com>
[INFO] GitHub credentials configured
[INFO] Zenn project already initialized
[INFO] Node.js version: v20.19.6
[INFO] npm version: 10.8.2
[INFO] Zenn CLI version: 0.2.3
[INFO] Setup complete! Starting FastAPI server...
```

---

## 使い方

### ヘルスチェック

```bash
curl http://localhost:8000/
```

**レスポンス:**

```json
{
  "status": "ok",
  "message": "Zenn Publisher API is running",
  "version": "1.0.0"
}
```

### 記事生成（手動コンテンツ）

```bash
curl -X POST http://localhost:8000/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Docker環境でZenn CLIを使う方法",
    "emoji": "🐳",
    "type": "tech",
    "content": "# はじめに\n\nDocker環境でZenn CLIを統合する方法を紹介します。"
  }'
```

**レスポンス:**

```json
{
  "status": "success",
  "slug": "abc123def456"
}
```

生成された記事は`articles/`ディレクトリに保存されます。

### 記事生成（AI）

```bash
curl -X POST http://localhost:8000/generate/ai \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "FastAPIとDockerの統合について",
    "title": "FastAPI + Docker入門",
    "emoji": "🚀",
    "type": "tech"
  }'
```

OpenAI API が記事内容を自動生成します。

### 記事公開

```bash
curl -X POST http://localhost:8000/publish/ \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "abc123def456"
  }'
```

記事の`published`フラグが`true`に変更され、GitHub に commit & push されます。

---

## API 仕様

### エンドポイント一覧

| メソッド | エンドポイント | 説明                     |
| -------- | -------------- | ------------------------ |
| GET      | `/`            | ヘルスチェック           |
| POST     | `/generate/`   | 手動コンテンツで記事作成 |
| POST     | `/generate/ai` | AI 生成で記事作成        |
| POST     | `/publish/`    | 記事を Zenn に公開       |

### API ドキュメント

FastAPI の自動生成ドキュメント:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## プロジェクト構成

```
Kenn_Zenn_Publisher/
├── .dockerignore            # Dockerビルド時の除外ファイル
├── .env.example             # 環境変数テンプレート
├── .gitignore               # Git除外設定
├── .pre-commit-config.yaml  # pre-commit設定
├── docker-compose.yml       # Docker Compose設定
├── pyproject.toml           # Python依存関係
├── README.md                # このファイル
│
├── backend/                 # FastAPIアプリケーション
│   ├── Dockerfile           # Dockerイメージ定義
│   ├── entrypoint.sh        # 起動スクリプト
│   ├── main.py              # エントリーポイント
│   │
│   ├── core/                # コア設定
│   │   ├── logger.py        # ロガー
│   │   └── settings.py      # 環境変数管理
│   │
│   ├── routers/             # APIエンドポイント
│   │   ├── generate.py      # 記事生成API
│   │   └── publish.py       # 記事公開API
│   │
│   ├── schemas/             # リクエスト/レスポンス定義
│   │   ├── generate_schema.py
│   │   └── publish_schemas.py
│   │
│   ├── services/            # ビジネスロジック
│   │   ├── ai_service.py    # OpenAI連携（将来実装予定）
│   │   ├── file_service.py  # ファイル操作
│   │   ├── generate_service.py  # 記事生成サービス
│   │   ├── publish_service.py   # 公開サービス
│   │   └── zenn_service.py      # Zenn CLI操作
│   │
│   └── exceptions/          # カスタム例外
│       └── exceptions.py
│
├── articles/                # Zenn記事（Gitに含む）
├── books/                   # Zenn本（将来使用予定）
│
└── docs/                    # プロジェクトドキュメント
    └── integration-design/  # 統合設計ドキュメント
```

---

## 開発環境

### ローカルでの開発（pre-commit 使用）

Docker 環境以外でも開発できます。

#### 1. Python 環境のセットアップ

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

#### 2. pre-commit のインストール

```bash
pre-commit install
```

これで、コミット時に自動で Ruff によるコードチェックとフォーマットが実行されます。

#### 3. コード品質チェック

```bash
# フォーマット
ruff format .

# Lint
ruff check .

# 自動修正
ruff check --fix .
```

### コンテナ操作

```bash
# コンテナ起動
docker-compose up -d

# ログ確認
docker-compose logs -f

# コンテナ停止
docker-compose down

# コンテナに入る
docker-compose exec fastapi bash

# Zenn CLIを直接実行
docker-compose exec fastapi npx zenn new:article
```

---

## トラブルシューティング

### Q. ポート 8000 が既に使用されている

```bash
# ポートを使用しているプロセスを確認
lsof -i :8000

# プロセスを終了
kill -9 <PID>
```

### Q. 環境変数が読み込まれない

- `.env`ファイルが存在するか確認
- `docker-compose down` → `docker-compose up -d --build` で再起動

### Q. Zenn CLI が動作しない

コンテナ内で確認:

```bash
docker-compose exec fastapi npx zenn --version
```

### Q. 記事が生成されない

1. ログを確認: `docker-compose logs -f`
2. `articles/`ディレクトリの権限を確認
3. エラーメッセージを確認して対処

---

## セキュリティに関する注意

⚠️ **本番環境での使用前に以下を確認してください:**

1. **環境変数の管理**

   - `.env`ファイルは`.gitignore`に含まれていますが、誤ってコミットしないよう注意
   - 本番環境では Docker Secrets の使用を推奨（[Issue #5](https://github.com/kensan0123/Kenn_Zenn_Publisher/issues/5)参照）

2. **GitHub Personal Access Token**

   - 必要最小限の権限（`repo`のみ）で生成
   - 定期的にトークンをローテーション

3. **OpenAI API Key**
   - 使用量の監視とレート制限の設定を推奨

---

## ライセンス

MIT License

---

## 貢献

プルリクエストや issue は大歓迎です！

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feat/amazing-feature`)
3. 変更をコミット (`git commit -m 'feat: Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feat/amazing-feature`)
5. プルリクエストを作成

---

## 参考資料

- [Zenn CLI Documentation](https://zenn.dev/zenn/articles/zenn-cli-guide)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
