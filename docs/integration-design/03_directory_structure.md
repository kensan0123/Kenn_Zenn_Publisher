# 統合後のディレクトリ構造設計

## プロジェクト名
**Kenn** (旧 Kenn_Zenn_Publisher)

## ディレクトリ構造

```
Kenn/
├── docs/                           # プロジェクトドキュメント
│   └── integration-design/         # 統合設計ドキュメント
│       ├── 01_project_overview.md
│       ├── 02_integration_approaches.md
│       ├── 03_directory_structure.md
│       ├── 04_api_design.md
│       └── 05_implementation_plan.md
│
├── backend/                        # FastAPIアプリケーション
│   ├── main.py                     # エントリーポイント
│   │
│   ├── core/                       # コア設定・共通機能
│   │   ├── __init__.py
│   │   ├── settings.py             # 環境変数・設定管理
│   │   └── logger.py               # ロガー設定
│   │
│   ├── routers/                    # APIエンドポイント
│   │   ├── __init__.py
│   │   ├── generate.py             # 記事生成エンドポイント
│   │   └── publish.py              # 記事公開エンドポイント
│   │
│   ├── schemas/                    # Pydanticスキーマ（リクエスト/レスポンス）
│   │   ├── __init__.py
│   │   ├── generate_schemas.py     # 生成関連のスキーマ
│   │   └── publish_schemas.py      # 公開関連のスキーマ
│   │
│   ├── services/                   # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── ai_service.py           # OpenAI連携サービス
│   │   ├── zenn_service.py         # Zenn CLI操作サービス（旧Kenn_Zennから移植）
│   │   └── file_service.py         # ファイル操作サービス（旧Kenn_Zennから移植）
│   │
│   ├── exceptions/                 # カスタム例外
│   │   ├── __init__.py
│   │   └── api_exception.py        # API例外定義
│   │
│   └── Dockerfile                  # Dockerイメージ定義
│
├── articles/                       # 生成された記事ファイル（Zenn CLI管理）
├── books/                          # Zenn本（将来の拡張用）
│
├── docker-compose.yml              # Docker Compose設定（単一サービス）
├── pyproject.toml                  # Python依存関係・プロジェクト設定
├── .env.example                    # 環境変数テンプレート
├── .env                            # 環境変数（gitignore）
├── .gitignore                      # Git除外設定
├── .pre-commit-config.yaml         # pre-commit設定
└── README.md                       # プロジェクトREADME
```

## 主要な変更点

### 追加されるファイル
- `backend/services/zenn_service.py` - Kenn_ZennのZenn CLI操作ロジックを移植
- `backend/services/file_service.py` - Kenn_Zennのファイル操作ロジックを移植
- `backend/services/ai_service.py` - OpenAI連携ロジックを独立したサービスに

### 削除されるファイル・機能
- Ollama関連の全コード（docker-compose.ymlのollamaサービス、routers/generate.pyの`/llama`エンドポイント）
- Kenn_Zennプロジェクト全体（統合後は不要）
- Upload機能関連のコード

### 統合されるファイル
- `Kenn_Zenn/app/services/generate_service.py` → `backend/services/zenn_service.py`
- `Kenn_Zenn/app/services/file_service.py` → `backend/services/file_service.py`
- `Kenn_Zenn/app/routers/generate.py` の機能 → `backend/routers/generate.py` に統合
- `Kenn_Zenn/app/routers/publish.py` の機能 → `backend/routers/publish.py` に統合

## ファイルの役割

### `backend/services/zenn_service.py`
**責任**: Zenn CLIの操作全般
- 記事生成（Zenn CLI実行）
- 記事公開（Git操作）
- トピック追加
- フロントマター操作

### `backend/services/ai_service.py`
**責任**: AI記事生成
- OpenAI API連携
- プロンプト構築
- レスポンスパース

### `backend/services/file_service.py`
**責任**: ファイル操作
- 記事ファイルの読み書き
- slugの抽出
- ファイルパスの解決

### `backend/routers/generate.py`
**責任**: 記事生成エンドポイント
- `/generate` - 基本記事生成（タイトル、絵文字、コンテンツを指定）
- `/generate/ai` - AI記事生成（タイトルのみ指定、OpenAIが自動生成）

### `backend/routers/publish.py`
**責任**: 記事公開エンドポイント
- `/publish` - 記事をZennに公開

## 依存関係フロー

```
routers/generate.py
    ├─> services/ai_service.py (OpenAI連携)
    └─> services/zenn_service.py (Zenn CLI操作)
         └─> services/file_service.py (ファイル操作)

routers/publish.py
    └─> services/zenn_service.py (Git操作)
```

## 環境変数

```bash
# OpenAI設定
OPENAI_API_KEY=sk-...

# GitHub設定（Zenn公開用）
GITHUB_PAT=ghp_...
GITHUB_USER=your-username

# Gitユーザー情報
user_name=Your Name
user_email=your-email@example.com

# Zennディレクトリ
ZENN_DIR=/app
```

## 次のステップ
APIエンドポイントの詳細設計
