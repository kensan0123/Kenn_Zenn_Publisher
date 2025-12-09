# 実装計画（詳細版）

## 概要

このドキュメントは、Kenn_ZennとKenn_Zenn_Publisherを統合し、**Kenn**として完成させるための詳細な実装計画です。
**このドキュメントは参考資料として保持し、実装時は簡潔版（05_implementation_plan.md）を使用してください。**

---

## フェーズ1: 準備と環境整備

### タスク1.1: プロジェクトのバックアップ
- [x] Kenn_Zenn_Publisherをベースプロジェクトとして使用
- [ ] Kenn_Zennのバックアップを作成（既に完了: Kenn_Zenn_backup_20251208_172952）
- [ ] 作業用ブランチを作成: `git checkout -b feat/integration-kenn-zenn`

### タスク1.2: ドキュメント整備
- [x] `docs/integration-design/` ディレクトリ作成
- [x] 01_project_overview.md 作成
- [x] 02_integration_approaches.md 作成
- [x] 03_directory_structure.md 作成
- [x] 04_api_design.md 作成
- [x] 05_implementation_plan.md 作成

### タスク1.3: 依存関係の確認と更新
- [ ] `pyproject.toml` の依存関係を確認
- [ ] Kenn_Zennの依存関係を追加（`python-multipart`など）
- [ ] Ollama関連の依存関係を削除（存在しないはず）

---

## フェーズ2: コードの移植

### タスク2.1: File Serviceの移植
**ソース**: `Kenn_Zenn/app/services/file_service.py`
**宛先**: `backend/services/file_service.py`

**作業内容**:
1. ファイルを新規作成
2. Kenn_Zennのfile_service.pyの内容をコピー
3. インポートパスを修正（`app.core.settings` → `core.settings`）
4. 動作確認

### タスク2.2: Zenn Serviceの移植
**ソース**: `Kenn_Zenn/app/services/generate_service.py`
**宛先**: `backend/services/zenn_service.py`

**作業内容**:
1. ファイルを新規作成
2. クラス名を `GenerateService` → `ZennService` に変更
3. Zenn CLI操作のロジックを移植:
   - `generate_article()` メソッド
   - `add_topics()` メソッド
4. `file_service.py` への依存関係を追加
5. `publish` 機能の追加（Kenn_Zennのpublish_service.pyから移植）
6. インポートパスを修正
7. 動作確認

### タスク2.3: AI Serviceの作成
**宛先**: `backend/services/ai_service.py`

**作業内容**:
1. ファイルを新規作成
2. 現在のrouters/generate.pyからOpenAI関連のロジックを抽出
3. `AIService` クラスを作成:
   - `generate_with_openai()` メソッド: プロンプト構築 + OpenAI API呼び出し
   - `_build_prompt()` メソッド: プロンプト生成（private）
4. OpenAI SDKの適切な使用方法を確認（最新API）
5. エラーハンドリングを追加

---

## フェーズ3: スキーマの整理

### タスク3.1: Generate Schemasの整理
**対象**: `backend/schemas/generate_schemas.py`

**作業内容**:
1. 現在の `generate_schema.py` を `generate_schemas.py` にリネーム（複数形に統一）
2. スキーマを整理:
   - `GenerateRequest` - 基本生成用（title, emoji, type, content, slug?）
   - `AIGenerateRequest` - AI生成用（prompt）
   - `GeneratedResponse` - 生成結果（status, slug）
3. 不要なスキーマを削除（Ollama関連など）

### タスク3.2: Publish Schemasの確認
**対象**: `backend/schemas/publish_schemas.py`

**作業内容**:
1. 現在のスキーマを確認
2. 必要に応じて調整

---

## フェーズ4: ルーターの統合

### タスク4.1: Generate Routerの統合
**対象**: `backend/routers/generate.py`

**作業内容**:
1. 既存の`/generate/openai`を`/generate/ai`にリネーム
2. `/generate/llama`エンドポイントを削除
3. `/generate`エンドポイントを更新:
   - HTTP経由でKenn_Zenn APIを呼び出すのではなく、直接`ZennService`を使用
4. `/generate/ai`エンドポイントを更新:
   - `AIService`を使用
   - OpenAI APIでコンテンツ生成
   - `ZennService`で記事作成
5. エラーハンドリングを追加
6. ロガーを使用してログ出力

### タスク4.2: Publish Routerの更新
**対象**: `backend/routers/publish.py`

**作業内容**:
1. HTTP経由でKenn_Zenn APIを呼び出すのではなく、直接`ZennService.publish()`を呼び出す
2. エラーハンドリングを更新
3. ロガーを使用してログ出力

---

## フェーズ5: 設定とインフラ

### タスク5.1: Settings の更新
**対象**: `backend/core/settings.py`

**作業内容**:
1. 環境変数を追加:
   - `GITHUB_PAT`: GitHubアクセストークン
   - `GITHUB_USER`: GitHubユーザー名
   - `user_name`: Gitコミット用の名前
   - `user_email`: Gitコミット用のメールアドレス
   - `ZENN_DIR`: Zennディレクトリパス
2. `KENN_ZENN_URL`を削除（不要になるため）
3. `OLLAMA_URL`を削除

### タスク5.2: Docker Composeの更新
**対象**: `docker-compose.yml`

**作業内容**:
1. `ollama`サービスを削除
2. `fastapi`サービスの設定を更新:
   - コンテナ名を`kenn-api`に変更
   - 環境変数を追加（GITHUB_PAT, GITHUB_USER, user_name, user_emailなど）
   - Zenn CLIのインストールが必要な場合、Dockerfileを更新
3. ボリューム設定を確認（`articles/`ディレクトリがマウントされているか）

### タスク5.3: Dockerfileの更新
**対象**: `backend/Dockerfile`

**作業内容**:
1. Node.js / npmのインストールを追加（Zenn CLI用）
2. Zenn CLIのインストール: `npm install -g zenn-cli`
3. Git設定の追加（user.name, user.email）
4. 必要なディレクトリの作成（`articles/`, `books/`）

### タスク5.4: 環境変数ファイルの更新
**対象**: `.env.example`

**作業内容**:
1. 新しい環境変数を追加
2. 削除された環境変数を除去（KENN_ZENN_URL, OLLAMA_URL）
3. コメントで説明を追加

---

## フェーズ6: 例外処理の追加

### タスク6.1: カスタム例外の追加
**対象**: `backend/exceptions/api_exception.py`

**作業内容**:
1. 既存の`KennZennAPIError`を`ZennCLIError`にリネーム
2. 新しい例外を追加:
   - `OpenAIAPIError` - OpenAI APIエラー
   - `GitOperationError` - Git操作エラー
   - `ArticleNotFoundError` - 記事が見つからない
3. 各例外に適切なステータスコードとメッセージを設定

---

## フェーズ7: テストと動作確認

### タスク7.1: 基本動作確認
**対象**: 全エンドポイント

**確認項目**:
1. [ ] `GET /` - ヘルスチェックが正常に動作するか
2. [ ] `POST /generate` - 基本記事生成が正常に動作するか
3. [ ] `POST /generate/ai` - AI記事生成が正常に動作するか
4. [ ] `POST /publish` - 記事公開が正常に動作するか

### タスク7.2: エラーケースの確認
1. [ ] 不正なリクエストデータ（バリデーションエラー）
2. [ ] OpenAI APIエラー（APIキーが無効など）
3. [ ] Zenn CLIエラー
4. [ ] Git操作エラー

### タスク7.3: エンドツーエンドテスト
1. [ ] AI記事生成 → 公開までの一連の流れ
2. [ ] 手動記事生成 → 公開までの一連の流れ
3. [ ] 複数記事の生成

---

## フェーズ8: クリーンアップと最終化

### タスク8.1: 不要なコードの削除
1. [ ] Ollama関連のコードを全削除
2. [ ] Upload関連のコードを全削除（`routers/upload.py`など）
3. [ ] 使用されていないインポートを削除

### タスク8.2: コードフォーマットとリント
1. [ ] `ruff format .` でコードをフォーマット
2. [ ] `ruff check .` でリントチェック
3. [ ] エラーを修正

### タスク8.3: ドキュメントの最終化
1. [ ] README.mdを更新（新しい統合プロジェクトの説明）
2. [ ] APIドキュメントの確認（FastAPIの自動生成ドキュメント）
3. [ ] 環境変数の説明を追加

---

## フェーズ9: コミットとPR作成

### タスク9.1: Git操作
1. [ ] 変更をステージング: `git add .`
2. [ ] コミット: `git commit -m "feat: integrate Kenn_Zenn into Kenn_Zenn_Publisher"`
3. [ ] リモートにプッシュ: `git push -u origin feat/integration-kenn-zenn`

### タスク9.2: PR作成
1. [ ] GitHubでPRを作成
2. [ ] PRの説明を記載（統合の概要、変更点、テスト結果など）
3. [ ] レビュー・マージ

---

## マイルストーン

| フェーズ | 期間目安 | 完了条件 |
|---------|---------|---------|
| フェーズ1: 準備 | 1日 | ドキュメント完成、ブランチ作成 |
| フェーズ2: 移植 | 2-3日 | 全サービスが移植され、ビルドエラーなし |
| フェーズ3: スキーマ | 1日 | スキーマが整理され、バリデーションが動作 |
| フェーズ4: ルーター | 2-3日 | 全エンドポイントが統合され、動作確認完了 |
| フェーズ5: インフラ | 1-2日 | Docker Composeで起動可能 |
| フェーズ6: 例外 | 1日 | エラーハンドリングが完全 |
| フェーズ7: テスト | 2-3日 | 全機能が正常動作、エラーケースも確認 |
| フェーズ8: クリーンアップ | 1日 | コードが整理され、ドキュメント完成 |
| フェーズ9: リリース | 1日 | PR作成、マージ完了 |

**合計期間**: 約2週間

---

## リスクと対策

### リスク1: Zenn CLIの互換性問題
**対策**: 最新のZenn CLIドキュメントを確認し、必要に応じてコマンドを調整

### リスク2: OpenAI APIの変更
**対策**: 最新のOpenAI Python SDKドキュメントを参照し、適切なAPIエンドポイントを使用

### リスク3: Git操作のエラー
**対策**: Git操作をテスト環境で十分に確認し、エラーハンドリングを強化

### リスク4: 環境変数の設定ミス
**対策**: `.env.example`を詳細に記述し、READMEに設定手順を明記

---

## 次のアクション

実装を開始する準備ができました。以下の順序で進めることを推奨します：

1. **フェーズ1のタスク1.1を完了** - 作業用ブランチを作成
2. **フェーズ1のタスク1.3を実施** - 依存関係を確認・更新
3. **フェーズ2に着手** - コードの移植を開始

実装中に不明点や問題が発生した場合は、このドキュメントを更新してください。
