# SQLAlchemy ORMの基礎理解

このドキュメントは、SQLAlchemyのオブジェクト指向での構造と動作原理についての学習内容をまとめたものです。

## 目次
1. [SQLAlchemyの3つの主要概念](#sqlalchemyの3つの主要概念)
2. [オブジェクト指向での関係性](#オブジェクト指向での関係性)
3. [シングルトンパターンとモジュールキャッシュ](#シングルトンパターンとモジュールキャッシュ)
4. [データの永続化とセッション管理](#データの永続化とセッション管理)
5. [Baseのメタデータと自動登録](#baseのメタデータと自動登録)
6. [実行順序とPythonの仕様](#実行順序とpythonの仕様)

---

## SQLAlchemyの3つの主要概念

### 1. Engine（エンジン）
**データベースへの接続口**

- **役割**: データベースとPythonアプリケーションをつなぐ「橋」
- **責任**: 接続情報（どのデータベースに、どうやって接続するか）を管理
- **比喩**: 自動車のエンジンのように、「動力源」

```python
self._engine: Engine = create_engine(
    self._database_url,
    echo=True,
    pool_pre_ping=True,
)
```

### 2. Base（ベース）
**テーブル設計の親クラス**

- **役割**: すべてのテーブルモデルが継承する基底クラス
- **責任**: テーブル定義を管理する`metadata`を持つ
- **重要**: `Base.metadata.create_all(engine)` で全テーブルを作成できる

```python
Base = declarative_base()

class WritingSessionModel(Base):
    __tablename__ = "writing_session"
    # ...
```

### 3. Session（セッション）
**データベース操作の作業場**

- **役割**: 実際のCRUD操作（作成・読取・更新・削除）を行う
- **責任**: トランザクション管理（commit/rollback）
- **比喩**: 「ショッピングカート」。変更を溜めて、最後にまとめて確定（commit）する

```python
self._session_local = sessionmaker(
    autoflush=False,
    bind=self._engine,
)
```

---

## オブジェクト指向での関係性

### 依存関係の流れ

```
Engine (接続情報)
   ↓ bindで紐付け
SessionMaker (Sessionの工場)
   ↓ 呼び出すたびに新しいSessionを生成
Session (実際の作業場)
   ↓ ここでBaseを継承したモデルを操作
Model (WritingSessionModel)
   ↓ metadata経由で
Base (テーブル設計情報の親)
   ↓ metadata.create_all()でEngineに送る
Engine (テーブルをDBに作成)
```

### EngineがBaseとSessionの両方に必要な理由

Engineは**データベースへの唯一の接続口**として、2つの異なる目的で使われる：

#### Base + Engine: テーブル構造を作る
```python
Base.metadata.create_all(engine)
# SQL: CREATE TABLE writing_session (...)
```

- **目的**: テーブル構造を作る
- **SQL種類**: DDL (CREATE TABLE)
- **タイミング**: 起動時1回
- **やっていること**: 「箱」を作る

#### Session + Engine: データを操作する
```python
session = SessionMaker(bind=engine)()
session.add(model)
session.commit()
# SQL: INSERT INTO writing_session VALUES (...)
```

- **目的**: データを操作する
- **SQL種類**: DML (INSERT/SELECT)
- **タイミング**: リクエストごと
- **やっていること**: 「中身」を入れる

---

## シングルトンパターンとモジュールキャッシュ

### モジュールレベルのインスタンス化

```python
# database.py
database = DataBase()  # モジュール読み込み時に1度だけ実行

def get_db() -> Generator[Session, None, None]:
    yield from database.get_session()  # 常に同じインスタンスを使用
```

### Pythonのモジュールキャッシュの仕組み

- Pythonは一度インポートしたモジュールを`sys.modules`にキャッシュ
- 同じモジュールは何回インポートしても**1回しか実行されない**
- モジュールレベルの変数（`database = DataBase()`）も1回だけ初期化

### 何を共有し、何を分離するか

| 要素 | 共有される？ | 理由 |
|------|------------|------|
| `database`インスタンス | ✅ 共有される | モジュールキャッシュ |
| `Engine`（接続プール） | ✅ 共有される | `database`の一部 |
| `SessionMaker` | ✅ 共有される | `database`の一部 |
| `Session` | ❌ 毎回新規 | リクエストごとに作成・破棄 |
| モデルオブジェクト（メモリ内） | ❌ 毎回新規 | Sessionと一緒に破棄 |
| データ（DB内） | ✅ 永続化 | PostgreSQLに保存 |

### なぜこの設計なのか？

**効率性と安全性のバランス**

```
アプリ起動
  ↓
database = DataBase() 実行（1回だけ）
  ├─ Engine作成（接続プール）
  └─ SessionMaker作成（セッション工場）

リクエスト1 → get_db()呼び出し
  └─ Session1作成 → 使用 → commit → close

リクエスト2 → get_db()呼び出し
  └─ Session2作成 → 使用 → commit → close

全て同じEngine・SessionMakerを使用 ✅ (効率的)
でもSessionは毎回新しい ✅ (安全)
```

---

## データの永続化とセッション管理

### データが保存されるまでの流れ

```python
# リクエスト1
db = get_db()  # 新しいSessionを取得
model1 = WritingSessionModel(topic="AAA")  # Pythonオブジェクト作成（メモリ内）
db.add(model1)  # Sessionの「追跡リスト」に追加（まだメモリ内）
db.commit()     # ここで初めてEngineを使ってDBに送信（永続化）
db.close()      # Sessionを閉じる（メモリから削除）

# リクエスト2（別のリクエスト）
db = get_db()  # 完全に新しいSession
# リクエスト1のmodel1はもうメモリにない
# でもPostgreSQLには保存されている

# データベースから取得
results = db.query(WritingSessionModel).all()  # PostgreSQLから取得
```

### Generatorとコンテキストマネージャ

```python
def get_session(self) -> Generator[Session, None, None]:
    session = self._session_local()
    try:
        yield session        # エンドポイントに渡される
        # エンドポイント処理が終わったら戻ってくる
        session.commit()     # 成功したら確定
    except Exception:
        session.rollback()   # エラーなら取り消し
        raise
    finally:
        session.close()      # 必ず閉じる
```

FastAPIの`Depends(get_db)`と組み合わせると、自動的にトランザクション管理が行われる。

### Docker再起動時のデータ永続化

- `docker-compose.yml`でボリュームをバインドしているため、Dockerを再起動してもデータは保持される
- データはPostgreSQLのディスクに保存されている（Pythonのメモリではない）

---

## Baseのメタデータと自動登録

### 継承時の自動登録の仕組み

```python
Base = declarative_base()  # metadata という辞書を持つ

class WritingSessionModel(Base):  # Base を継承した瞬間...
    __tablename__ = "writing_session"
    # この時点で自動的に Base.metadata に登録される
```

### 内部の仕組み（メタクラスプログラミング）

```python
# declarative_base() の内部イメージ
def declarative_base():
    class Base:
        metadata = MetaData()  # テーブル情報を格納

        # クラスが継承されたときに呼ばれる特殊メソッド
        def __init_subclass__(cls):
            if hasattr(cls, '__tablename__'):
                # metadata に自動登録
                Base.metadata.tables[cls.__tablename__] = cls

    return Base
```

### create_all()の動作

```python
Base.metadata.create_all(engine)
# 内部で以下を実行：
# 1. Base.metadata.tables を見る
# 2. 各テーブルについてPostgreSQLに存在確認
#    SQL: SELECT * FROM information_schema.tables WHERE table_name = '...';
# 3. 存在しない → CREATE TABLE を実行
#    存在する → 何もしない（スキップ）
```

**重要**: `create_all()`は「テーブルの存在」のみ確認し、「構造の変更」は検出しない。カラム変更にはマイグレーションツール（Alembic）が必要。

---

## 実行順序とPythonの仕様

### uvicorn起動時の実行フロー

```python
# 1. uvicorn backend.main:app を実行
#    ↓
# 2. main.py が読み込まれる
#    ↓
# 3. main.py の import 文が実行される
from backend.core.database import database
#    ↓
# 4. database.py が読み込まれる
#    ↓
# 5. database = DataBase() が実行される
#    ↓
# 6. main.py の lifespan が実行される
@asynccontextmanager
async def lifespan(app: FastAPI):
    database.create_tables()  # ここで初めて呼ばれる
#    ↓
# 7. create_tables() の中で import が実行される
from backend.models.session_model import Base
#    ↓
# 8. session_model.py が読み込まれる
Base = declarative_base()  # 実行される
class WritingSessionModel(Base):  # この瞬間に Base.metadata に自動登録
#    ↓
# 9. import 完了（Base.metadata に WritingSessionModel が入ってる）
#    ↓
# 10. Base.metadata.create_all(engine) が実行される
```

### クラス定義は実行文

Pythonでは**クラス定義も実行文**：

```python
# これは「宣言」ではなく「実行」
class WritingSessionModel(Base):  # この行が実行される瞬間
    __tablename__ = "writing_session"
    # __init_subclass__ が呼ばれて Base.metadata に登録
```

### importの同期実行

```python
from backend.models.session_model import Base  # この1行で以下が全て起きる：
# 1. session_model.py を読み込む
# 2. Base = declarative_base() を実行
# 3. class WritingSessionModel(Base) を実行（定義）
# 4. → __init_subclass__ が自動で呼ばれる
# 5. → Base.metadata に登録される
# 6. import 完了

# だから次の行では既に登録済み
Base.metadata.create_all(engine)  # WritingSessionModel の情報が使える
```

**重要**: Pythonのimport文は**ブロッキング**（完全に終わるまで次に進まない）なので、順序が保証される。

---

## まとめ

### 設計の核心

1. **Engine**: 重い（接続管理）→ 1つを使い回す
2. **SessionMaker**: 軽い（設定情報）→ 1つを使い回す
3. **Session**: 軽い（作業単位）→ 毎回新しく作る

### Pythonの仕様による保証

- モジュールは1回だけ実行される（`sys.modules`キャッシュ）
- import文は同期的に実行される（上から順）
- クラス定義も実行文である

### SQLAlchemyの魔法

- `Base`を継承すると自動的に`metadata`に登録される（メタクラス）
- `create_all()`は既存テーブルをスキップする（冪等性）
- トランザクション管理が自動化される（Generator + Depends）

### データの流れ

```
Python Object (メモリ)
   ↓ session.add()
Session (追跡リスト)
   ↓ session.commit()
Engine (SQL変換・送信)
   ↓
PostgreSQL (ディスク永続化)
```

---

## 参考ファイル

- [backend/core/database.py](../../backend/core/database.py)
- [backend/models/session_model.py](../../backend/models/session_model.py)
- [backend/main.py](../../backend/main.py)
