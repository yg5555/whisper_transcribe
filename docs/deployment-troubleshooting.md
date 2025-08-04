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
    "postinstall": "npm rebuild"
  },
  "overrides": {
    "rollup": {
      "@rollup/rollup-linux-x64-gnu": "4.9.5"
    }
  },
  "engines": {
    "node": ">=18.0.0"
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
```

#### 1.3 ビルドスクリプトの使用
```bash
#!/bin/bash
set -e

# 既存の依存関係をクリーンアップ
rm -rf node_modules package-lock.json

# npmキャッシュをクリア
npm cache clean --force

# 依存関係を再インストール
npm install --platform=linux --arch=x64

# ビルドを実行
npm run build
```

## 2. Node.jsバージョン問題

### 問題
- Node.js v22.14.0での互換性問題
- 古いバージョンでの機能不足

### 解決策
```yaml
# render.yaml
envVars:
  - key: NODE_VERSION
    value: 18.19.0
```

## 3. ビルドプロセス最適化

### 3.1 Vite設定の調整
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
    minify: 'terser'
  },
  optimizeDeps: {
    include: ['react', 'react-dom']
  }
})
```

### 3.2 ビルドコマンドの改善
```yaml
# render.yaml
buildCommand: |
  cd frontend && chmod +x build.sh && ./build.sh
  cd ../backend && pip install -r requirements.txt
```

## 4. 環境変数の設定

### 4.1 必要な環境変数
```bash
# フロントエンド
NODE_ENV=production
VITE_API_URL=https://your-backend-url.com

# バックエンド
PYTHON_VERSION=3.11.0
NODE_VERSION=18.19.0
```

### 4.2 Renderでの設定方法
1. Renderダッシュボードでプロジェクトを開く
2. "Environment"タブを選択
3. 必要な環境変数を追加

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
    cd frontend && chmod +x build.sh && ./build.sh
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