#!/bin/bash

# メモリ効率化されたビルドスクリプト
set -e

echo "=== メモリ効率化ビルド開始 ==="

# メモリ制限を設定
export NODE_OPTIONS="--max-old-space-size=256"

# 現在のディレクトリを確認
echo "現在のディレクトリ: $(pwd)"

# Node.jsバージョンを確認
echo "Node.jsバージョン: $(node --version)"
echo "npmバージョン: $(npm --version)"

# 既存のnode_modulesとpackage-lock.jsonを削除
echo "=== 既存の依存関係をクリーンアップ ==="
rm -rf node_modules package-lock.json

# npmキャッシュをクリア
echo "=== npmキャッシュをクリア ==="
npm cache clean --force

# 依存関係を段階的にインストール
echo "=== 依存関係を段階的にインストール ==="

# 1. コア依存関係のみインストール
echo "ステップ1: コア依存関係"
npm install --platform=linux --arch=x64 --no-optional --no-audit --no-fund --production=false react react-dom

# 2. 開発依存関係をインストール
echo "ステップ2: 開発依存関係"
npm install --platform=linux --arch=x64 --no-optional --no-audit --no-fund --save-dev @vitejs/plugin-react vite typescript

# 3. 残りの依存関係をインストール
echo "ステップ3: 残りの依存関係"
npm install --platform=linux --arch=x64 --no-optional --no-audit --no-fund --production=false

# プラットフォーム固有の依存関係を確認
echo "=== プラットフォーム固有の依存関係を確認 ==="
ls -la node_modules/@rollup/ || echo "Rollupディレクトリが見つかりません"

# ビルドを実行（メモリ制限付き）
echo "=== ビルドを実行 ==="
NODE_OPTIONS="--max-old-space-size=256" npm run build

echo "=== メモリ効率化ビルド完了 ===" 