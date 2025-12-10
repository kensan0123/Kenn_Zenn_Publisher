#!/bin/bash
set -e

echo "[INFO] Starting Zenn Publisher API..."

if [ -f "$GITHUB_PAT_FILE" ]; then
    GITHUB_PAT=$(cat "$GITHUB_PAT_FILE")
fi

# Git設定（環境変数から）
if [ -n "$USER_NAME" ] && [ -n "$USER_EMAIL" ]; then
    git config --global user.name "$USER_NAME"
    git config --global user.email "$USER_EMAIL"
    echo "[INFO] Git configured: $USER_NAME <$USER_EMAIL>"
else
    echo "[WARN] USER_NAME or USER_EMAIL not set"
fi

# .netrcファイルの作成（GitHub認証用）
if [ -n "$GITHUB_PAT" ] && [ -n "$GITHUB_USER" ]; then
    echo "machine github.com" > ~/.netrc
    echo "login $GITHUB_USER" >> ~/.netrc
    echo "password $GITHUB_PAT" >> ~/.netrc
    chmod 600 ~/.netrc
    echo "[INFO] GitHub credentials configured"
else
    echo "[WARN] GITHUB_PAT or GITHUB_USER not set"
fi

# Zennディレクトリの存在確認
if [ ! -d "/app/articles" ]; then
    echo "[INFO] Initializing Zenn project..."
    cd /app && npx zenn init
    echo "[INFO] Zenn project initialized"
else
    echo "[INFO] Zenn project already initialized"
fi

# Node.jsとZenn CLIのバージョン確認
echo "[INFO] Node.js version: $(node --version)"
echo "[INFO] npm version: $(npm --version)"
echo "[INFO] Zenn CLI version: $(npx zenn --version)"

echo "[INFO] Setup complete! Starting FastAPI server..."

# コマンド実行
exec "$@"
