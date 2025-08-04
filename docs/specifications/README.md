# 仕様書・要件定義書

このフォルダには、プロジェクトの仕様書や要件定義書を格納します。

## フォルダ構成

```
specifications/
├── requirements/          # 要件定義書
│   ├── functional.md     # 機能要件
│   ├── non-functional.md # 非機能要件
│   └── user-stories.md   # ユーザーストーリー
├── design/               # 設計仕様書
│   ├── system-design.md  # システム設計
│   ├── api-design.md     # API設計
│   └── ui-design.md      # UI設計
├── technical/            # 技術仕様書
│   ├── architecture.md   # アーキテクチャ
│   ├── database.md       # データベース設計
│   └── deployment.md     # デプロイメント仕様
└── README.md            # このファイル
```

## ドキュメント管理ルール

1. **ファイル名**: 英語で記述し、ハイフン区切りを使用
2. **フォーマット**: Markdown形式を推奨
3. **バージョン管理**: Gitで管理し、変更履歴を記録
4. **更新日**: 各ドキュメントの末尾に最終更新日を記載

## テンプレート

各ドキュメントは以下のテンプレートを使用してください：

```markdown
# ドキュメントタイトル

## 概要
[ドキュメントの目的と概要]

## 詳細
[詳細な内容]

## 関連ドキュメント
[関連する他のドキュメントへのリンク]

## 更新履歴
- YYYY-MM-DD: 初版作成
- YYYY-MM-DD: 内容更新
``` 