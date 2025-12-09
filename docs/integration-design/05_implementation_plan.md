# 実装計画（簡潔版）

> 📌 詳細な参考資料は `05_implementation_plan_detailed.md` を参照してください

## 統合の目標

Kenn_ZennとKenn_Zenn_Publisherを統合し、**Kenn**として1つのサービスにする。

---

## 実装の流れ

### 1. 準備
- [ ] ブランチ作成: `feat/integration-kenn-zenn`
- [ ] 依存関係の更新（pyproject.toml）

### 2. コード移植
**Kenn_Zennから移植するファイル:**
- [ ] `app/services/file_service.py` → `backend/services/file_service.py`
- [ ] `app/services/generate_service.py` → `backend/services/zenn_service.py`
  - クラス名変更: `GenerateService` → `ZennService`
- [ ] `app/services/publish_service.py` → `zenn_service.py` に統合

**新規作成:**
- [ ] `backend/services/ai_service.py` - OpenAI連携ロジック

### 3. スキーマ整理
- [ ] `generate_schema.py` → `generate_schemas.py` にリネーム
- [ ] 不要なスキーマ削除（Ollama関連）

### 4. ルーター更新
**`backend/routers/generate.py`:**
- [ ] `/generate/llama` を削除
- [ ] `/generate/openai` → `/generate/ai` にリネーム
- [ ] HTTP呼び出しを直接サービス呼び出しに変更

**`backend/routers/publish.py`:**
- [ ] HTTP呼び出しを直接サービス呼び出しに変更

### 5. 設定とインフラ
**`backend/core/settings.py`:**
- [ ] 環境変数追加: `GITHUB_PAT`, `GITHUB_USER`, `user_name`, `user_email`, `ZENN_DIR`
- [ ] 削除: `KENN_ZENN_URL`, `OLLAMA_URL`

**`docker-compose.yml`:**
- [ ] ollamaサービスを削除
- [ ] fastapiサービスの環境変数を追加

**`backend/Dockerfile`:**
- [ ] Node.js/npmをインストール
- [ ] Zenn CLIをインストール: `npm install -g zenn-cli`
- [ ] Git設定を追加

**`.env.example`:**
- [ ] 新しい環境変数を追加
- [ ] 古い環境変数を削除

### 6. 例外処理
- [ ] カスタム例外を追加: `ZennCLIError`, `OpenAIAPIError`, `GitOperationError`, `ArticleNotFoundError`

### 7. テスト
- [ ] 各エンドポイントの動作確認（`GET /`, `POST /generate`, `POST /generate/ai`, `POST /publish`）
- [ ] エラーケースの確認
- [ ] E2Eテスト（記事生成→公開）

### 8. クリーンアップ
- [ ] Ollama関連コードを全削除
- [ ] Upload関連コードを全削除
- [ ] コードフォーマット: `ruff format .`
- [ ] リント: `ruff check .`
- [ ] README.mdを更新

### 9. コミット・PR
- [ ] コミット: `git commit -m "feat: integrate Kenn_Zenn into Kenn_Zenn_Publisher"`
- [ ] プッシュ: `git push -u origin feat/integration-kenn-zenn`
- [ ] PRを作成

---

## 統合後のAPIエンドポイント

```
GET  /                   # ヘルスチェック
POST /generate           # 基本記事生成（手動入力）
POST /generate/ai        # AI記事生成（OpenAI）
POST /publish            # 記事公開
```

---

## 重要なポイント

### Zenn CLIの操作
- `npx zenn new:article` で記事を作成
- フロントマターとコンテンツを操作

### OpenAI連携
- プロンプトを構築してGPT-4/3.5に送信
- JSON形式でレスポンスを受け取る（title, emoji, type, content）

### Git操作
- 記事公開時に `git add → commit → push`

### 削除対象
- Ollama関連の全て
- Upload機能
- `KENN_ZENN_URL`（HTTP呼び出しが不要になるため）

---

## トラブルシューティング

問題が発生した場合は、`05_implementation_plan_detailed.md` を参照してください。
