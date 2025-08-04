#!/bin/bash

echo "=== Whisper Transcribe 起動開始 ==="

# 環境変数の設定
export PYTHONPATH=./backend
export NODE_OPTIONS="--max-old-space-size=256"

# フロントエンドのビルド（静的ファイル生成）
echo "=== フロントエンドビルド開始 ==="
cd frontend

# 最適化されたビルドスクリプトを使用
echo "=== 最適化されたビルドスクリプトを実行 ==="
chmod +x build-optimized.sh
./build-optimized.sh

# ビルド結果を確認
if [ -d "dist" ]; then
    echo "=== フロントエンドビルド成功 ==="
    ls -la dist/
    FRONTEND_AVAILABLE=true
else
    echo "=== フロントエンドビルド失敗 - APIのみモードで起動 ==="
    FRONTEND_AVAILABLE=false
fi

# バックエンドディレクトリに移動
cd ../backend

# バックエンドの依存関係をインストール
echo "=== バックエンド依存関係インストール ==="
pip install -r requirements.txt

# 静的ファイルの存在確認
frontend_dist_path="../frontend/dist"
if [ -d "$frontend_dist_path" ] && [ "$FRONTEND_AVAILABLE" = true ]; then
    echo "=== フロントエンド + バックエンドモードで起動 ==="
    echo "=== ポート: $PORT ==="
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --timeout-keep-alive 75
else
    echo "=== APIのみモードで起動 ==="
    echo "=== ポート: $PORT ==="
    uvicorn app.main_fallback:app --host 0.0.0.0 --port ${PORT:-8000} --timeout-keep-alive 75
fi
