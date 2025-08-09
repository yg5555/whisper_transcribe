#!/bin/bash

echo "=== Whisper Transcribe 起動開始 ==="

# 環境変数の設定
export PYTHONPATH=./backend

# バックエンドを起動（フロントはビルド段階で作成済みの dist を配信）
cd backend
echo "=== バックエンド起動 ==="
echo "=== ポート: $PORT ==="
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --timeout-keep-alive 75
