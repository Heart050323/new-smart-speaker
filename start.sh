#!/bin/bash

# お母さんスイッチ Web GUI 起動スクリプト

echo "======================================"
echo "  お母さんスイッチ システム起動"
echo "======================================"
echo ""

# カレントディレクトリをスクリプトの場所に変更
cd "$(dirname "$0")"

# Pythonの確認
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3がインストールされていません"
    exit 1
fi

echo "✅ Python3: $(python3 --version)"

# Flaskのインストール確認
if ! python3 -c "import flask" &> /dev/null; then
    echo "📦 Flaskをインストールしています..."
    pip3 install -r requirements.txt
fi

echo ""
echo "🚀 サーバーを起動しています..."
echo ""
echo "ブラウザで以下のURLにアクセスしてください:"
echo "👉 http://localhost:5001"
echo ""
echo "終了するには Ctrl+C を押してください"
echo ""

# Flaskサーバー起動
python3 app.py
