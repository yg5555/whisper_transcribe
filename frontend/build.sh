#!/bin/bash

# Render用ビルドスクリプト
set -e

echo "=== フロントエンドビルド開始 ==="

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

# 依存関係を再インストール
echo "=== 依存関係をインストール ==="
npm install --platform=linux --arch=x64

# プラットフォーム固有の依存関係を確認
echo "=== プラットフォーム固有の依存関係を確認 ==="
ls -la node_modules/@rollup/ || echo "Rollupディレクトリが見つかりません"

# ビルドを実行
echo "=== ビルドを実行 ==="
npm run build

echo "=== フロントエンドビルド完了 ===" 