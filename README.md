# Ken_Zenn_Publisher

## 概要
Zenn 記事を自動生成するシンプルな FastAPI サービスです。タイトルを送ると、バックエンドが Ollama（llama3）を使って Markdown 形式の記事を返し、`backend/articles/` に保存します。

## 動かし方
1. Docker と Docker Compose を用意する。
2. リポジトリ直下でコンテナを起動:
   ```bash
   docker compose up -d --build
   ```
3. 動作確認:
   - ヘルスチェック: `GET http://localhost:8000/` → `{"status": "running"}`
   - 記事生成: `POST http://localhost:8000/generate`（JSON 例: `{"title": "Python 入門"}`）

生成された記事ファイルは `backend/articles/` にタイムスタンプ付きで保存されます。
