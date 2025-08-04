## モード別のドキュメント

- [ローカルUI構成はこちら（NiceGUI 直結）](./README_LOCAL.md)
- [API構成はこちら（FastAPI + UI）](./README_API.md)

## 仕様書・要件定義書

- [仕様書一覧](./specifications/README.md)
- [機能要件定義](./specifications/requirements/functional.md)
- [非機能要件定義](./specifications/requirements/non-functional.md)
- [要件マトリックス](./specifications/requirements/requirements-matrix.md)

## ドキュメント生成

```bash
# 要件定義書から各種ドキュメントを自動生成
python docs/specifications/scripts/generate-docs.py
```

## Notion連携

### 自動同期（推奨）
```bash
# 環境変数を設定
export NOTION_TOKEN="your_integration_token"
export NOTION_DATABASE_ID="your_database_id"

# 自動同期を実行
python docs/specifications/scripts/notion-sync.py
```

### 手動エクスポート変換
```bash
# エクスポートしたファイルをnotion-exportsフォルダに配置
# 変換を実行
python docs/specifications/scripts/notion-export-converter.py
```

詳細は[セットアップガイド](./specifications/scripts/notion-setup.md)を参照してください。

## エラー監視・同期

### 手動エラー同期
```bash
# コマンドを実行してエラーを同期
python docs/specifications/scripts/error-log-sync.py "python app/main.py"
```

### リアルタイム監視
```bash
# リアルタイムでエラーを監視
python docs/specifications/scripts/realtime-error-monitor.py "python app/main.py"
```

### エラーデータベース設定
詳細は[エラーデータベース設定ガイド](./specifications/scripts/error-database-setup.md)を参照してください。