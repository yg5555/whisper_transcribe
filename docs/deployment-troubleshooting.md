# デプロイメント問題解決ガイド

## 概要
Renderでのデプロイ時に発生する一般的な問題とその解決策を説明します。

## 1. Rollup依存関係エラー

### 問題
```
Error: Cannot find module @rollup/rollup-linux-x64-gnu
```

### 原因
- npmのオプショナル依存関係のバグ
- プラットフォーム固有のバイナリが正しくインストールされていない
- Node.jsバージョンの互換性問題

### 解決策

#### 1.1 package.jsonの更新
```json
{
  "scripts": {
    "postinstall": "npm rebuild",
    "clean": "rm -rf node_modules package-lock.json dist",
    "reinstall": "npm run clean && npm install"
  },
  "overrides": {
    "rollup": {
      "@rollup/rollup-linux-x64-gnu": "4.9.5"
    },
    "vite": {
      "rollup": {
        "@rollup/rollup-linux-x64-gnu": "4.9.5"
      }
    }
  },
  "engines": {
    "node": ">=18.0.0 <23.0.0",
    "npm": ">=8.0.0"
  },
  "resolutions": {
    "@rollup/rollup-linux-x64-gnu": "4.9.5"
  }
}
```

#### 1.2 .npmrcファイルの作成
```
platform=linux
arch=x64
optional=false
registry=https://registry.npmjs.org/
cache=.npm-cache
loglevel=warn
legacy-peer-deps=true
strict-peer-dependencies=false
target_platform=linux
target_arch=x64
target_libc=glibc
```

#### 1.3 ビルドスクリプトの使用
```bash
#!/bin/bash
set -e

echo "=== フロントエンドビルド開始 ==="

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
```

## 2. 本番環境での起動問題

### 問題
- 開発サーバーが本番環境で起動しようとする
- 静的ファイルが配信されない
- ポートが正しく設定されていない

### 解決策

#### 2.1 start.shの更新
```bash
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
```

#### 2.2 render.yamlの更新
```yaml
services:
  - type: web
    name: whisper-transcribe
    env: python
    plan: free
    buildCommand: |
      echo "=== ビルド開始 ==="
      echo "Node.js バージョン: $(node --version)"
      echo "npm バージョン: $(npm --version)"
      echo "Python バージョン: $(python --version)"
      
      # フロントエンドビルド
      cd frontend
      echo "=== フロントエンド依存関係クリーンアップ ==="
      rm -rf node_modules package-lock.json
      
      echo "=== フロントエンド依存関係インストール ==="
      npm install --platform=linux --arch=x64 --production=false
      
      echo "=== フロントエンドビルド ==="
      npm run build
      
      # バックエンド依存関係インストール
      cd ../backend
      echo "=== バックエンド依存関係インストール ==="
      pip install -r requirements.txt
      
      echo "=== ビルド完了 ==="
    startCommand: bash start.sh
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: NODE_VERSION
        value: 18.19.0
      - key: PORT
        value: 8000
```

## 3. 静的ファイル配信の設定

### 3.1 バックエンドでの静的ファイル配信
```python
from fastapi import FastAPI, StaticFiles
from pathlib import Path

app = FastAPI()

# 静的ファイル配信（フロントエンドのビルド結果）
frontend_build_path = Path("../frontend/dist")
if frontend_build_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="static")
```

### 3.2 フロントエンドのAPIエンドポイント設定
```typescript
// 本番環境では相対パスを使用
const apiUrl = import.meta.env.PROD ? '/api/transcribe' : 'http://localhost:8000/api/transcribe';
```

## 4. Vite設定の最適化

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      external: [],
      output: {
        manualChunks: undefined
      }
    },
    target: 'es2015',
    minify: 'terser',
    commonjsOptions: {
      include: []
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom'],
    exclude: ['@rollup/rollup-linux-x64-gnu']
  },
  define: {
    global: 'globalThis'
  }
})
```

## 5. デバッグ方法

### 5.1 ログの確認
```bash
# Renderダッシュボードでログを確認
# または、ローカルでテスト
npm run build
```

### 5.2 ローカルテスト
```bash
# フロントエンド
cd frontend
npm install
npm run build

# バックエンド
cd backend
pip install -r requirements.txt
python app/main.py
```

## 6. 予防策

### 6.1 依存関係の管理
- 定期的に`npm audit`を実行
- 依存関係のバージョンを固定
- セキュリティアップデートを適用

### 6.2 ビルドテスト
- プルリクエスト時に自動ビルドテスト
- 複数のNode.jsバージョンでテスト
- 本番環境に近い環境でテスト

## 7. よくある問題と解決策

### 7.1 メモリ不足
```bash
# Node.jsのメモリ制限を増やす
export NODE_OPTIONS="--max-old-space-size=4096"
```

### 7.2 タイムアウト
```yaml
# render.yaml
buildCommand: |
  timeout 600 bash -c '
    cd frontend && npm install && npm run build
    cd ../backend && pip install -r requirements.txt
  '
```

### 7.3 権限エラー
```bash
# 実行権限を付与
chmod +x build.sh
chmod +x start.sh
```

## 8. 監視とアラート

### 8.1 エラー監視の設定
```bash
# エラー監視スクリプトを使用
python docs/specifications/scripts/error-log-sync.py "npm run build"
```

### 8.2 通知設定
- Renderの通知設定を有効化
- Slackやメールでのアラート設定
- エラー発生時の自動通知

## 更新履歴
- 2024-01-XX: 初版作成
- 2024-01-XX: Rollup依存関係問題の解決策を追加
- 2024-01-XX: 本番環境での静的ファイル配信設定を追加 