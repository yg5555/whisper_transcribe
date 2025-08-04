#!/bin/bash

echo "=== Whisper Transcribe 起動開始 ==="

# 環境変数の設定
export PYTHONPATH=./backend

# フロントエンドのビルド（静的ファイル生成）
echo "=== フロントエンドビルド開始 ==="
cd frontend

# 既存の依存関係をクリーンアップ
echo "=== 依存関係クリーンアップ ==="
rm -rf node_modules package-lock.json

# npmキャッシュをクリア
echo "=== npmキャッシュクリア ==="
npm cache clean --force

# 依存関係を再インストール
echo "=== 依存関係インストール ==="
npm install --platform=linux --arch=x64 --production=false

# ビルドを実行
echo "=== ビルド実行 ==="
npm run build

# バックエンドディレクトリに移動
cd ../backend

# バックエンドの依存関係をインストール
echo "=== バックエンド依存関係インストール ==="
pip install -r requirements.txt

# バックエンドサーバーを起動
echo "=== バックエンドサーバー起動 ==="
uvicorn app.main:app --host 0.0.0.0 --port 8000
