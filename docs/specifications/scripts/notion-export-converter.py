#!/usr/bin/env python3
"""
Notionから手動エクスポートしたファイルを変換するスクリプト
HTML、Markdown、PDF等の形式に対応
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import html2text
from bs4 import BeautifulSoup

class NotionExportConverter:
    def __init__(self, input_dir: str = "notion-exports"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path("docs/specifications/requirements")
        
    def convert_html_to_markdown(self, html_file: Path) -> str:
        """HTMLファイルをMarkdownに変換"""
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 不要な要素を削除
        for element in soup.find_all(['script', 'style']):
            element.decompose()
        
        # html2textでMarkdownに変換
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0  # 改行を無効化
        
        markdown_content = h.handle(str(soup))
        
        # タイトルを抽出
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            markdown_content = f"# {title_text}\n\n{markdown_content}"
        
        # 更新日時を追加
        markdown_content += f"\n---\n最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return markdown_content
    
    def convert_markdown(self, md_file: Path) -> str:
        """Markdownファイルを整形"""
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新日時を追加
        if "最終更新:" not in content:
            content += f"\n---\n最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return content
    
    def extract_requirements_from_text(self, text: str) -> Dict[str, Any]:
        """テキストから要件を抽出"""
        requirements = {
            "functional": [],
            "non_functional": [],
            "user_stories": []
        }
        
        # 機能要件のパターンマッチング
        func_pattern = r'(?:機能要件|Functional Requirement|FR)[:\s]*([^\n]+)'
        func_matches = re.findall(func_pattern, text, re.IGNORECASE)
        
        for i, match in enumerate(func_matches):
            requirements["functional"].append({
                "id": f"FR-{i+1:03d}",
                "name": match.strip(),
                "priority": "中",  # デフォルト値
                "details": []
            })
        
        # 非機能要件のパターンマッチング
        non_func_pattern = r'(?:非機能要件|Non-Functional Requirement|NFR)[:\s]*([^\n]+)'
        non_func_matches = re.findall(non_func_pattern, text, re.IGNORECASE)
        
        for i, match in enumerate(non_func_matches):
            requirements["non_functional"].append({
                "id": f"NFR-{i+1:03d}",
                "item": match.strip(),
                "details": []
            })
        
        return requirements
    
    def process_notion_export(self):
        """Notionエクスポートファイルを処理"""
        print("Notionエクスポートファイルを処理中...")
        
        if not self.input_dir.exists():
            print(f"入力ディレクトリが見つかりません: {self.input_dir}")
            return False
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        processed_files = []
        
        # HTMLファイルを処理
        for html_file in self.input_dir.glob("*.html"):
            print(f"HTMLファイルを処理中: {html_file.name}")
            
            markdown_content = self.convert_html_to_markdown(html_file)
            
            # ファイル名を生成
            filename = html_file.stem.replace(' ', '-').lower()
            output_file = self.output_dir / f"{filename}.md"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            processed_files.append(output_file)
            
            # 要件を抽出
            requirements = self.extract_requirements_from_text(markdown_content)
            if any(requirements.values()):
                req_file = self.output_dir / f"{filename}-requirements.json"
                with open(req_file, 'w', encoding='utf-8') as f:
                    json.dump(requirements, f, ensure_ascii=False, indent=2)
        
        # Markdownファイルを処理
        for md_file in self.input_dir.glob("*.md"):
            print(f"Markdownファイルを処理中: {md_file.name}")
            
            markdown_content = self.convert_markdown(md_file)
            
            # ファイル名を生成
            filename = md_file.stem.replace(' ', '-').lower()
            output_file = self.output_dir / f"{filename}.md"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            processed_files.append(output_file)
        
        print(f"処理完了: {len(processed_files)}ファイル")
        return True
    
    def create_index_file(self):
        """インデックスファイルを作成"""
        index_content = """# Notion要件定義書

このフォルダには、Notionからエクスポートした要件定義書が格納されています。

## ファイル一覧

"""
        
        for md_file in self.output_dir.glob("*.md"):
            if md_file.name != "README.md":
                index_content += f"- [{md_file.stem}](./{md_file.name})\n"
        
        index_content += f"\n---\n最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        index_file = self.output_dir / "README.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)

def main():
    """メイン処理"""
    converter = NotionExportConverter()
    
    if converter.process_notion_export():
        converter.create_index_file()
        print("変換が完了しました")
    else:
        print("変換に失敗しました")

if __name__ == "__main__":
    main() 