# APIエンドポイント設計

## 概要

統合後の**Kenn**は、シンプルで明確な2つの主要機能を提供します：
1. **記事生成（Generate）**: 手動またはAIで記事を作成
2. **記事公開（Publish）**: 生成した記事をZennに公開

---

## エンドポイント一覧

### ヘルスチェック
```
GET /
```

### 記事生成
```
POST /generate           # 基本生成（手動入力）
POST /generate/ai        # AI生成（OpenAI）
```

### 記事公開
```
POST /publish            # 記事を公開
```

---

## 詳細仕様

### 1. ヘルスチェック

#### `GET /`

**概要**: サービスの稼働状態を確認

**リクエスト**: なし

**レスポンス**:
```json
{
  "status": "running",
  "service": "Kenn",
  "version": "1.0.0"
}
```

**ステータスコード**:
- `200 OK` - 正常稼働中

---

### 2. 基本記事生成

#### `POST /generate`

**概要**: タイトル、絵文字、コンテンツを手動で指定して記事を生成

**ユースケース**:
- 既に記事コンテンツを持っている場合
- AIを使わず、手動で記事を作成したい場合

**リクエストボディ**:
```json
{
  "title": "FastAPIで作るREST API入門",
  "emoji": "🚀",
  "type": "tech",
  "content": "# はじめに\n\nこの記事では...",
  "slug": "fastapi-rest-api-intro"  // オプション
}
```

**リクエストスキーマ**:
| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| title | string | ✅ | 記事タイトル |
| emoji | string | ✅ | 記事の絵文字（1文字） |
| type | string | ✅ | 記事タイプ（"tech" または "idea"） |
| content | string | ✅ | 記事本文（Markdown形式） |
| slug | string | ❌ | 記事のslug（省略時は自動生成） |

**レスポンス**:
```json
{
  "status": "generated",
  "slug": "fastapi-rest-api-intro"
}
```

**ステータスコード**:
- `200 OK` - 記事生成成功
- `400 Bad Request` - リクエストデータが不正
- `500 Internal Server Error` - Zenn CLI実行エラー

**処理フロー**:
1. リクエストバリデーション
2. Zenn CLIで記事ファイル作成
3. フロントマター + コンテンツを書き込み
4. slugを返却

---

### 3. AI記事生成

#### `POST /generate/ai`

**概要**: タイトル（テーマ）だけを指定して、OpenAIが記事全体を自動生成

**ユースケース**:
- AIに記事を書いてもらいたい場合
- アイデアだけあって、詳細を考えるのが面倒な場合

**リクエストボディ**:
```json
{
  "prompt": "FastAPIで認証機能を実装する方法"
}
```

**リクエストスキーマ**:
| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| prompt | string | ✅ | 記事のテーマ・タイトル |

**レスポンス**:
```json
{
  "status": "generated",
  "slug": "fastapi-authentication-implementation"
}
```

**ステータスコード**:
- `200 OK` - 記事生成成功
- `400 Bad Request` - リクエストデータが不正
- `500 Internal Server Error` - OpenAI APIエラーまたはZenn CLI実行エラー
- `503 Service Unavailable` - OpenAI APIが利用不可

**処理フロー**:
1. リクエストバリデーション
2. プロンプト構築（専門的な技術記事を書くための詳細な指示）
3. OpenAI APIに送信（GPT-4/GPT-3.5を使用）
4. レスポンスをパース（JSON形式で返却される: title, emoji, type, content）
5. Zenn CLIで記事ファイル作成
6. 生成されたコンテンツを書き込み
7. slugを返却

**OpenAI プロンプト構造**:
```
あなたはZennの技術ライターです。
以下のテーマで高品質な技術記事を日本語で書き、
JSON形式のみで出力してください。

# 入力テーマ
{prompt}

# 記事の要件
- Markdown形式で記述
- 構成: 導入 → 背景 → 手順 → まとめ
- コード例を含める
- です・ます調

# 出力形式
{
  "title": "記事タイトル",
  "emoji": "絵文字",
  "type": "tech or idea",
  "content": "記事本文（Markdown）"
}

最後に「この記事はAIによって作成されました。」と追記してください。
```

---

### 4. 記事公開

#### `POST /publish`

**概要**: 生成済みの記事をZennに公開（GitHub経由）

**ユースケース**:
- 記事を生成後、Zennに公開したい場合

**リクエストボディ**:
```json
{
  "slug": "fastapi-rest-api-intro"
}
```

**リクエストスキーマ**:
| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| slug | string | ✅ | 公開する記事のslug |

**レスポンス**:
```json
{
  "status": "published",
  "slug": "fastapi-rest-api-intro"
}
```

**ステータスコード**:
- `200 OK` - 記事公開成功
- `400 Bad Request` - slugが不正または記事が存在しない
- `500 Internal Server Error` - Git操作エラー

**処理フロー**:
1. リクエストバリデーション
2. slugに対応する記事ファイルの存在確認
3. フロントマターの`published`を`true`に変更
4. Git操作（add → commit → push）
5. 公開完了をレスポンス

---

## エラーハンドリング

### カスタム例外
- `ZennCLIError` - Zenn CLI実行エラー
- `OpenAIAPIError` - OpenAI APIエラー
- `GitOperationError` - Git操作エラー
- `ArticleNotFoundError` - 記事が見つからない

### エラーレスポンス形式
```json
{
  "error": "エラータイプ",
  "message": "詳細なエラーメッセージ",
  "detail": {
    "additional": "追加情報"
  }
}
```

---

## 今後の拡張案

### 将来追加される可能性のある機能
1. **記事一覧取得**: `GET /articles` - 生成済み記事の一覧
2. **記事詳細取得**: `GET /articles/{slug}` - 特定記事の内容取得
3. **記事編集**: `PUT /articles/{slug}` - 既存記事の編集
4. **記事削除**: `DELETE /articles/{slug}` - 記事の削除
5. **トピック管理**: `POST /articles/{slug}/topics` - トピックの追加・削除
6. **本（Book）のサポート**: Zennの本（Book）機能への対応

---

## 次のステップ
実装計画の策定
