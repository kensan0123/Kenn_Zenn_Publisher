FROM python:3.11-slim

WORKDIR /app

# pyproject.toml と必要なファイルをコピー
COPY pyproject.toml ./
COPY backend/ ./backend/

# 依存関係をインストール（本番環境のみ）
RUN pip install --upgrade pip && pip install -e .[dev]

# FastAPI 実行ディレクトリ（backendフォルダ内）
WORKDIR /app/backend

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
