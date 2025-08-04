# Notion連携セットアップガイド

## 概要
Notionで作成した要件定義書をプロジェクトに取り込む方法を説明します。

## 方法1: Notion APIを使用した自動同期

### 1. Notion APIの設定

#### 1.1 Integration Tokenの取得
1. [Notion Developers](https://developers.notion.com/)にアクセス
2. "New integration"をクリック
3. 統合名を入力（例: "Requirements Sync"）
4. Submitをクリック
5. "Internal Integration Token"をコピー

#### 1.2 データベースの共有設定
1. Notionで要件定義書のデータベースを開く
2. 右上の"Share"ボタンをクリック
3. 作成したIntegrationを追加
4. "Can edit"権限を付与

#### 1.3 データベースIDの取得
1. データベースページのURLをコピー
2. URLからデータベースIDを抽出
   - 例: `https://notion.so/workspace/1234567890abcdef` → `1234567890abcdef`

### 2. 環境変数の設定

```bash
# .envファイルを作成
echo "NOTION_TOKEN=your_integration_token_here" >> .env
echo "NOTION_DATABASE_ID=your_database_id_here" >> .env

# または環境変数として設定
export NOTION_TOKEN="your_integration_token_here"
export NOTION_DATABASE_ID="your_database_id_here"
```

### 3. 依存関係のインストール

```bash
pip install requests markdown
```

### 4. 同期の実行

```bash
# 自動同期を実行
python docs/specifications/scripts/notion-sync.py
```

## 方法2: 手動エクスポート + 変換

### 1. Notionからのエクスポート

#### 1.1 ページ単位でのエクスポート
1. 要件定義書のページを開く
2. 右上の"..."メニューをクリック
3. "Export"を選択
4. 形式を選択（HTML推奨）
5. "Export"をクリック

#### 1.2 データベース全体のエクスポート
1. データベースページを開く
2. 右上の"..."メニューをクリック
3. "Export"を選択
4. 形式を選択（HTML推奨）
5. "Export"をクリック

### 2. ファイルの配置

```bash
# エクスポートしたファイルを配置
mkdir notion-exports
# エクスポートしたファイルをnotion-exportsフォルダにコピー
```

### 3. 依存関係のインストール

```bash
pip install beautifulsoup4 html2text
```

### 4. 変換の実行

```bash
# エクスポートファイルを変換
python docs/specifications/scripts/notion-export-converter.py
```

## 方法3: コピー&ペースト + 手動整形

### 1. テキストのコピー
1. Notionの要件定義書を開く
2. 全選択（Cmd+A / Ctrl+A）
3. コピー（Cmd+C / Ctrl+C）

### 2. ファイルの作成

```bash
# 新しい要件定義書ファイルを作成
touch docs/specifications/requirements/notion-requirements.md
```

### 3. 手動でペースト
1. 作成したファイルをエディタで開く
2. コピーしたテキストをペースト
3. Markdown形式に手動で整形

## 推奨データベース構造

### 機能要件テーブル
| プロパティ | タイプ | 説明 |
|-----------|--------|------|
| 要件ID | Title | 一意の要件ID（FR-001等） |
| 機能名 | Text | 機能の名前 |
| 優先度 | Select | 高/中/低 |
| 詳細 | Text | 機能の詳細説明 |
| ステータス | Select | 未実装/実装中/完了 |
| 担当者 | Person | 担当者 |

### 非機能要件テーブル
| プロパティ | タイプ | 説明 |
|-----------|--------|------|
| 要件ID | Title | 一意の要件ID（NFR-001等） |
| 項目 | Text | 非機能要件の項目名 |
| 詳細 | Text | 要件の詳細説明 |
| カテゴリ | Select | 性能/セキュリティ/可用性等 |
| ステータス | Select | 未実装/実装中/完了 |

## トラブルシューティング

### API認証エラー
- Integration Tokenが正しく設定されているか確認
- データベースにIntegrationが共有されているか確認

### ファイル変換エラー
- エクスポートしたファイルの形式を確認
- 依存関係が正しくインストールされているか確認

### 文字化け
- ファイルのエンコーディングをUTF-8に設定
- 日本語文字が正しく表示されるか確認

## 更新履歴
- 2024-01-XX: 初版作成 