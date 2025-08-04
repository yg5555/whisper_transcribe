# デプロイメント問題解決ガイド

## 概要
Renderでのデプロイ時に発生する一般的な問題とその解決策を説明します。

## 1. FastAPIインポートエラー

### 問題
```
ImportError: cannot import name 'StaticFiles' from 'fastapi'
```

### 原因
- FastAPIのバージョンによって`StaticFiles`のインポート場所が変更
- 古いバージョンでは`fastapi.staticfiles`からインポートする必要がある

### 解決策

#### 1.1 正しいインポート方法
```python
# 誤ったインポート
from fastapi import FastAPI, StaticFiles

# 正しいインポート
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
```

#### 1.2 バージョン固定
```txt
# requirements.txt
fastapi==0.109.2
aiofiles>=0.8.0
```

#### 1.3 フォールバック機能
```python
# 静的ファイル配信の設定
frontend_build_path = Path("../frontend/dist")
if frontend_build_path.exists():
    try:
        app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="static")
        print(f"静的ファイル配信を有効化: {frontend_build_path}")
    except Exception as e:
        print(f"静的ファイル配信の設定エラー: {e}")
else:
    print(f"警告: フロントエンドビルドディレクトリが見つかりません: {frontend_build_path}")
```

## 2. メモリ不足エラー

### 問題
```
==> Out of memory (used over 512Mi)
```

### 原因
- Render無料プランの512MBメモリ制限
- npm installやビルドプロセスでの大量メモリ使用
- Node.jsのデフォルトメモリ設定

### 解決策

#### 2.1 Node.jsメモリ制限の設定
```bash
# メモリ制限を256MBに設定
export NODE_OPTIONS="--max-old-space-size=256"
```

#### 2.2 npm設定の最適化
```bash
# メモリ効率化されたインストール
npm install --no-optional --no-audit --no-fund --production=false
```

#### 2.3 段階的インストール
```bash
# 1. コア依存関係のみ
npm install react react-dom

# 2. 開発依存関係
npm install --save-dev @vitejs/plugin-react vite typescript

# 3. 残りの依存関係
npm install
```

#### 2.4 Vite設定の最適化
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    // メモリ効率化
    chunkSizeWarningLimit: 1000,
    sourcemap: false
  },
  esbuild: {
    target: 'es2015'
  }
})
```

## 3. Rollup依存関係エラー

### 問題
```
Error: Cannot find module @rollup/rollup-linux-x64-gnu
```

### 原因
- npmのオプショナル依存関係のバグ
- プラットフォーム固有のバイナリが正しくインストールされていない
- Node.jsバージョンの互換性問題

### 解決策

#### 3.1 package.jsonの更新
```json
{
  "scripts": {
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

#### 3.2 .npmrcファイルの作成
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
# メモリ効率化
maxsockets=1
fetch-retries=3
fetch-retry-mintimeout=10000
fetch-retry-maxtimeout=60000
```

#### 3.3 最適化されたビルドスクリプト
```bash
#!/bin/bash
# メモリ効率化されたビルドスクリプト
set -e

echo "=== メモリ効率化ビルド開始 ==="

# メモリ制限を設定
export NODE_OPTIONS="--max-old-space-size=256"

# 既存の依存関係をクリーンアップ
echo "=== 依存関係クリーンアップ ==="
rm -rf node_modules package-lock.json

# npmキャッシュをクリア
echo "=== npmキャッシュクリア ==="
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

# ビルドを実行（メモリ制限付き）
echo "=== ビルド実行 ==="
NODE_OPTIONS="--max-old-space-size=256" npm run build

echo "=== メモリ効率化ビルド完了 ==="
```

## 4. 本番環境での起動問題

### 問題
- 開発サーバーが本番環境で起動しようとする
- 静的ファイルが配信されない
- ポートが正しく設定されていない

### 解決策

#### 4.1 start.shの更新
```bash
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
else
    echo "=== フロントエンドビルド失敗 - APIのみモードで起動 ==="
fi

# バックエンドディレクトリに移動
cd ../backend

# バックエンドの依存関係をインストール
echo "=== バックエンド依存関係インストール ==="
pip install -r requirements.txt

# 静的ファイルの存在確認
frontend_dist_path="../frontend/dist"
if [ -d "$frontend_dist_path" ]; then
    echo "=== フロントエンド + バックエンドモードで起動 ==="
    uvicorn app.main:app --host 0.0.0.0 --port 8000
else
    echo "=== APIのみモードで起動 ==="
    uvicorn app.main_fallback:app --host 0.0.0.0 --port 8000
fi
```

#### 4.2 render.yamlの更新
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
      
      # バックエンド依存関係インストール
      cd backend
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
      - key: NODE_OPTIONS
        value: "--max-old-space-size=256"
```

## 5. 静的ファイル配信の設定

### 5.1 バックエンドでの静的ファイル配信
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# 静的ファイル配信（フロントエンドのビルド結果）
frontend_build_path = Path("../frontend/dist")
if frontend_build_path.exists():
    try:
        app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="static")
        print(f"静的ファイル配信を有効化: {frontend_build_path}")
    except Exception as e:
        print(f"静的ファイル配信の設定エラー: {e}")
```

### 5.2 フロントエンドのAPIエンドポイント設定
```typescript
// 本番環境では相対パスを使用
const apiUrl = import.meta.env.PROD ? '/api/transcribe' : 'http://localhost:8000/api/transcribe';
```

## 6. デバッグ方法

### 6.1 ログの確認
```bash
# Renderダッシュボードでログを確認
# または、ローカルでテスト
npm run build
```

### 6.2 ローカルテスト
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

## 7. 予防策

### 7.1 依存関係の管理
- 定期的に`npm audit`を実行
- 依存関係のバージョンを固定
- セキュリティアップデートを適用

### 7.2 ビルドテスト
- プルリクエスト時に自動ビルドテスト
- 複数のNode.jsバージョンでテスト
- 本番環境に近い環境でテスト

## 8. よくある問題と解決策

### 8.1 メモリ不足
```bash
# Node.jsのメモリ制限を増やす
export NODE_OPTIONS="--max-old-space-size=256"
```

### 8.2 タイムアウト
```yaml
# render.yaml
buildCommand: |
  timeout 600 bash -c '
    cd frontend && npm install && npm run build
    cd ../backend && pip install -r requirements.txt
  '
```

### 8.3 権限エラー
```bash
# 実行権限を付与
chmod +x build.sh
chmod +x start.sh
```

## 9. 監視とアラート

### 9.1 エラー監視の設定
```bash
# エラー監視スクリプトを使用
python docs/specifications/scripts/error-log-sync.py "npm run build"
```

### 9.2 通知設定
- Renderの通知設定を有効化
- Slackやメールでのアラート設定
- エラー発生時の自動通知

## 更新履歴
- 2024-01-XX: 初版作成
- 2024-01-XX: Rollup依存関係問題の解決策を追加
- 2024-01-XX: 本番環境での静的ファイル配信設定を追加
- 2024-01-XX: メモリ不足問題の解決策を追加
- 2024-01-XX: FastAPIインポート問題の解決策を追加 