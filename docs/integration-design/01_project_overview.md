# プロジェクト統合概要

## 背景

### Kenn_Zenn
- **目的**: Zenn CLIをFastAPIでラップして使いやすくする
- **主要機能**:
  - 記事生成（`/generate`）: タイトル、絵文字、コンテンツから記事ファイルを作成
  - 公開（`/publish`）: 記事をZennに公開
- **ポート**: 9000, 9001
- **技術スタック**: FastAPI, Zenn CLI, Docker
- **未完成機能**: ログ機能など

### Kenn_Zenn_Publisher
- **目的**: OpenAI LLMを使って記事を簡単に作成
- **主要機能**:
  - AI記事生成（`/generate`）: タイトルからOpenAIが記事コンテンツを自動生成
  - 記事公開（`/publish`）: 生成した記事をKenn_Zennサービス経由でZennに公開
- **ポート**: 8000
- **LLM統合**: OpenAI API（GPT-4/GPT-3.5など）
- **技術スタック**: FastAPI, OpenAI, Docker
- **アーキテクチャ**: より構造化（core/, routers/, services/, schemas/, exceptions/）

## 統合の目的

### 主な動機
1. **開発効率の向上**: Docker Compose一つで全システムを起動したい
2. **コードの重複削減**: 両プロジェクトに類似した機能（generate, publish）が存在
3. **保守性の向上**: 一つのリポジトリで管理することで、メンテナンスが容易に
4. **機能の拡張性**: 統合により、より強力な機能セットを提供できる

### 統合後の目標
- **名称**: Kenn（統合プロジェクト名）
- **ワンコマンド起動**: `docker compose up` で全サービスが起動
- **シームレスな連携**: OpenAI生成からZenn公開までの一貫したワークフロー
- **設計ドキュメントの蓄積**: 意思決定と設計の記録を残す

## 現在の依存関係

```
Kenn_Zenn_Publisher (Port 8000)
    |
    | HTTP Request (requests library)
    v
Kenn_Zenn (Port 9000)
    |
    v
Zenn CLI
```

**現状の課題**:
- 2つのサービスを別々に起動する必要がある
- Publisher が Kenn_Zenn を外部 API として呼び出す（ネットワークオーバーヘッド）
- 依存関係の管理が複雑
- コードの重複（generate, publish のロジック）

## 技術的な決定事項

### ✅ 確定した方針
1. **LLMプロバイダー**: OpenAI APIのみを使用
   - **削除**: Ollama関連の全コード・設定・依存関係
   - **理由**: 性能の観点から、OpenAIの方が優れている
   - **メリット**: Dockerイメージの軽量化、リソース消費の削減

2. **機能のスコープ**: コア機能に絞る
   - **残す**: Generate（記事生成）、Publish（記事公開）
   - **削除**: Upload機能
   - **理由**: シンプルさを保ち、メンテナンスしやすくする

## 次のステップ
統合アプローチの検討と設計方針の決定
