#!/usr/bin/env python3
"""
Notion APIを使用して要件定義書を自動同期するスクリプト
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import markdown
import re

class NotionSync:
    def __init__(self, token: str = None, database_id: str = None):
        self.token = token or os.getenv('NOTION_TOKEN')
        self.database_id = database_id or os.getenv('NOTION_DATABASE_ID')
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
    def get_database_pages(self) -> List[Dict[str, Any]]:
        """データベースからページを取得"""
        url = f"{self.base_url}/databases/{self.database_id}/query"
        response = requests.post(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Notion API エラー: {response.status_code}")
            
        return response.json().get('results', [])
    
    def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """ページの内容を取得"""
        url = f"{self.base_url}/blocks/{page_id}/children"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"ページ取得エラー: {response.status_code}")
            
        return response.json()
    
    def parse_notion_block(self, block: Dict[str, Any]) -> str:
        """NotionブロックをMarkdownに変換"""
        block_type = block.get('type', '')
        
        if block_type == 'paragraph':
            rich_text = block.get('paragraph', {}).get('rich_text', [])
            text = ''.join([rt.get('plain_text', '') for rt in rich_text])
            return text + '\n\n'
            
        elif block_type == 'heading_1':
            rich_text = block.get('heading_1', {}).get('rich_text', [])
            text = ''.join([rt.get('plain_text', '') for rt in rich_text])
            return f"# {text}\n\n"
            
        elif block_type == 'heading_2':
            rich_text = block.get('heading_2', {}).get('rich_text', [])
            text = ''.join([rt.get('plain_text', '') for rt in rich_text])
            return f"## {text}\n\n"
            
        elif block_type == 'heading_3':
            rich_text = block.get('heading_3', {}).get('rich_text', [])
            text = ''.join([rt.get('plain_text', '') for rt in rich_text])
            return f"### {text}\n\n"
            
        elif block_type == 'bulleted_list_item':
            rich_text = block.get('bulleted_list_item', {}).get('rich_text', [])
            text = ''.join([rt.get('plain_text', '') for rt in rich_text])
            return f"- {text}\n"
            
        elif block_type == 'numbered_list_item':
            rich_text = block.get('numbered_list_item', {}).get('rich_text', [])
            text = ''.join([rt.get('plain_text', '') for rt in rich_text])
            return f"1. {text}\n"
            
        elif block_type == 'code':
            rich_text = block.get('code', {}).get('rich_text', [])
            text = ''.join([rt.get('plain_text', '') for rt in rich_text])
            language = block.get('code', {}).get('language', '')
            return f"```{language}\n{text}\n```\n\n"
            
        elif block_type == 'quote':
            rich_text = block.get('quote', {}).get('rich_text', [])
            text = ''.join([rt.get('plain_text', '') for rt in rich_text])
            return f"> {text}\n\n"
            
        return ""
    
    def convert_page_to_markdown(self, page: Dict[str, Any]) -> str:
        """ページをMarkdownに変換"""
        page_id = page.get('id')
        properties = page.get('properties', {})
        
        # ページタイトルを取得
        title = "Untitled"
        for prop_name, prop_value in properties.items():
            if prop_value.get('type') == 'title':
                title_text = prop_value.get('title', [])
                if title_text:
                    title = ''.join([t.get('plain_text', '') for t in title_text])
                break
        
        # ページ内容を取得
        content_blocks = self.get_page_content(page_id)
        markdown_content = f"# {title}\n\n"
        
        for block in content_blocks.get('results', []):
            markdown_content += self.parse_notion_block(block)
        
        # 更新日時を追加
        markdown_content += f"\n---\n最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return markdown_content
    
    def sync_requirements(self, output_dir: str = "docs/specifications/requirements"):
        """要件定義書を同期"""
        print("Notionから要件定義書を同期中...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            pages = self.get_database_pages()
            
            for page in pages:
                properties = page.get('properties', {})
                
                # ページタイプを判定（カスタムプロパティに応じて調整）
                page_type = "unknown"
                for prop_name, prop_value in properties.items():
                    if prop_value.get('type') == 'select':
                        select_value = prop_value.get('select', {})
                        if select_value:
                            page_type = select_value.get('name', 'unknown').lower()
                        break
                
                # ファイル名を決定
                title = "untitled"
                for prop_name, prop_value in properties.items():
                    if prop_value.get('type') == 'title':
                        title_text = prop_value.get('title', [])
                        if title_text:
                            title = ''.join([t.get('plain_text', '') for t in title_text])
                        break
                
                filename = f"{page_type}-{title.lower().replace(' ', '-')}.md"
                filename = re.sub(r'[^\w\-_.]', '', filename)
                
                # Markdownに変換して保存
                markdown_content = self.convert_page_to_markdown(page)
                file_path = output_path / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                print(f"同期完了: {filename}")
                
        except Exception as e:
            print(f"同期エラー: {e}")
            return False
        
        return True

def main():
    """メイン処理"""
    # 環境変数から設定を読み込み
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('NOTION_DATABASE_ID')
    
    if not token or not database_id:
        print("環境変数を設定してください:")
        print("export NOTION_TOKEN='your_notion_token'")
        print("export NOTION_DATABASE_ID='your_database_id'")
        return
    
    sync = NotionSync(token, database_id)
    success = sync.sync_requirements()
    
    if success:
        print("同期が完了しました")
    else:
        print("同期に失敗しました")

if __name__ == "__main__":
    main() 