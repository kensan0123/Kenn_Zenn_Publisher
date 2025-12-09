#!/bin/bash
# backend/entrypoint.sh

set -e

echo "🚀 Starting Zenn Publisher API..."

# Git設定（環境変数から）
if [ -n "$USER_NAME" ] && [ -n "$USER_EMAIL" ]; then
    git config --global user.name "$USER_NAME"
    git config --global user.email "$USER_EMAIL"
    echo "✅ Git configured: $USER_NAME <$USER_EMAIL>"
else
    echo "⚠️  Warning: USER_NAME or USER_EMAIL not set"
fi

# .netrcファイルの作成（GitHub認証用）
if [ -n "$GITHUB_PAT" ] && [ -n "$GITHUB_USER" ]; then
    echo "machine github.com" > ~/.netrc
    echo "login $GITHUB_USER" >> ~/.netrc
    echo "password $GITHUB_PAT" >> ~/.netrc
    chmod 600 ~/.netrc
    echo "✅ GitHub credentials configured"
else
    echo "⚠️  Warning: GITHUB_PAT or GITHUB_USER not set"
fi

# Zennディレクトリの存在確認
if [ ! -d "/app/articles" ]; then
    echo "📝 Initializing Zenn project..."
    cd /app && npx zenn init
    echo "✅ Zenn project initialized"
else
    echo "✅ Zenn project already initialized"
fi

# Node.jsとZenn CLIのバージョン確認
echo "📦 Node.js version: $(node --version)"
echo "📦 npm version: $(npm --version)"
echo "📦 Zenn CLI version: $(npx zenn --version)"

echo "🎉 Setup complete! Starting FastAPI server..."

# コマンド実行
exec "$@"
