FROM python:3.11-slim

# Node.jsのインストール（Zenn CLI用）
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python依存関係のインストール
COPY pyproject.toml ./
COPY backend/ ./backend/

RUN pip install --upgrade pip && pip install -e .[dev]

# Zenn CLIのグローバルインストール
RUN npm install -g zenn-cli

# Zennプロジェクトの初期化（articles/, books/ディレクトリを作成）
# 初回のみ実行されるように条件付きで実行
RUN npx zenn init || true

# エントリーポイントスクリプトをコピー
COPY backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# FastAPI 実行ディレクトリ（backendフォルダ内）
WORKDIR /app/backend

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
