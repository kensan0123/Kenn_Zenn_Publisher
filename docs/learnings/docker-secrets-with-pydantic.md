# Docker Secrets と Pydantic Settings の統合

## 問題

Docker Secretsで機密情報を管理する際、Pydantic Settingsで環境変数からファイルパスを読み取り、そのファイルから実際の値を取得する必要があった。

## 試行錯誤

### ❌ 失敗1: `@field_validator(mode="before")`

```python
@field_validator("OPENAI_API_KEY", mode="before")
@classmethod
def load_openai_key(cls, v, info):
    if v and v.startswith("sk-"):
        return v
    file_path = info.data.get("OPENAI_API_KEY_FILE")
    if file_path and Path(file_path).exists():
        return Path(file_path).read_text().strip()
    return v
```

**問題点**:
- Pydanticは各フィールドを個別に検証するため、`OPENAI_API_KEY`が必須フィールドだとエラーになる
- `info.data.get()`で他のフィールドを参照するタイミングが不安定

**エラー**:
```
ValidationError: Field required [type=missing]
```

### ❌ 失敗2: フィールドをオプショナルにしてvalidatorで必須化

```python
OPENAI_API_KEY: str | None = None
```

**問題点**:
- `info.data.get("OPENAI_API_KEY_FILE")`が取得できないケースがある
- validator実行時に他のフィールドがまだ読み込まれていない

## ✅ 解決策: `@model_validator(mode="before")`

```python
@model_validator(mode="before")
@classmethod
def load_secrets_from_files(cls, data: dict) -> dict:
    """Docker Secretsファイルから認証情報を読み込む"""
    if not data.get("OPENAI_API_KEY"):
        file_path = data.get("OPENAI_API_KEY_FILE")
        if file_path and Path(file_path).exists():
            key = Path(file_path).read_text().strip()
            if key.startswith("sk-"):
                data["OPENAI_API_KEY"] = key
    return data

@field_validator("OPENAI_API_KEY")
@classmethod
def validate_openai_key(cls, v):
    if not v or not v.startswith("sk-"):
        raise ValueError("Valid OPENAI_API_KEY is required")
    return v
```

### なぜ成功したか

1. **`@model_validator`は全フィールドを受け取る**: `data`辞書に全環境変数が含まれる
2. **実行タイミングが早い**: 個別フィールド検証の前に実行される
3. **データを書き換えられる**: `data["OPENAI_API_KEY"]`を直接更新できる

### 処理フロー

```
1. Pydantic Settingsが環境変数を読み込む
   OPENAI_API_KEY=None
   OPENAI_API_KEY_FILE="/run/secrets/openai_api_key"
   ↓
2. @model_validator(mode="before") 実行
   ファイルから値を読み込み
   data["OPENAI_API_KEY"] = "sk-xxx"
   ↓
3. @field_validator 実行
   値を検証してOK
```

## Docker構成

```yaml
# docker-compose.yml
services:
  fastapi:
    secrets:
      - openai_api_key
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key

secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt
```

```bash
# secrets/openai_api_key.txt
sk-proj-xxxxx
```

## 学び

- **`@field_validator`**: 単一フィールドの検証に適している
- **`@model_validator`**: 複数フィールドを参照する、データ変換に適している
- **`mode="before"`**: Pydanticの型変換前に実行される
- Docker Secretsは `/run/secrets/` にファイルとしてマウントされる
