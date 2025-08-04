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