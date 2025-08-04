#!/usr/bin/env python3
"""
ターミナルエラーを収集してNotionに同期するスクリプト
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import logging

class ErrorLogSync:
    def __init__(self, notion_token: str = None, database_id: str = None):
        self.notion_token = notion_token or os.getenv('NOTION_TOKEN')
        self.database_id = database_id or os.getenv('NOTION_ERROR_DB_ID')
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('error_sync.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def capture_command_output(self, command: str, timeout: int = 300) -> Dict[str, Any]:
        """コマンドを実行して出力とエラーをキャプチャ"""
        try:
            self.logger.info(f"コマンド実行開始: {command}")
            
            # プロセスを実行
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            stdout_lines = []
            stderr_lines = []
            
            # リアルタイムで出力をキャプチャ
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                
                if stdout_line:
                    stdout_lines.append(stdout_line.strip())
                    print(f"STDOUT: {stdout_line.strip()}")
                
                if stderr_line:
                    stderr_lines.append(stderr_line.strip())
                    print(f"STDERR: {stderr_line.strip()}", file=sys.stderr)
                
                # プロセスが終了したかチェック
                if process.poll() is not None:
                    break
            
            # 残りの出力を読み取り
            remaining_stdout, remaining_stderr = process.communicate()
            stdout_lines.extend(remaining_stdout.strip().split('\n') if remaining_stdout else [])
            stderr_lines.extend(remaining_stderr.strip().split('\n') if remaining_stderr else [])
            
            return {
                "command": command,
                "return_code": process.returncode,
                "stdout": stdout_lines,
                "stderr": stderr_lines,
                "timestamp": datetime.now().isoformat(),
                "success": process.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "command": command,
                "return_code": -1,
                "stdout": stdout_lines,
                "stderr": stderr_lines + ["Command timed out"],
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "command": command,
                "return_code": -1,
                "stdout": [],
                "stderr": [str(e)],
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def parse_errors(self, output_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """出力からエラーを解析"""
        errors = []
        
        # エラー出力を解析
        for line in output_data.get("stderr", []):
            error_info = self.parse_error_line(line)
            if error_info:
                errors.append(error_info)
        
        # 標準出力からもエラーパターンを検索
        for line in output_data.get("stdout", []):
            error_info = self.parse_error_line(line)
            if error_info:
                errors.append(error_info)
        
        return errors
    
    def parse_error_line(self, line: str) -> Optional[Dict[str, Any]]:
        """エラー行を解析"""
        # Pythonエラーパターン
        python_pattern = r'(\w+Error):\s*(.+)'
        python_match = re.search(python_pattern, line)
        if python_match:
            return {
                "type": "Python Error",
                "error_class": python_match.group(1),
                "message": python_match.group(2),
                "line": line
            }
        
        # ファイルパス付きエラーパターン
        file_pattern = r'File\s+"([^"]+)",\s+line\s+(\d+),\s+in\s+(\w+)\s*\n\s*(\w+Error):\s*(.+)'
        file_match = re.search(file_pattern, line)
        if file_match:
            return {
                "type": "Python File Error",
                "file": file_match.group(1),
                "line_number": int(file_match.group(2)),
                "function": file_match.group(3),
                "error_class": file_match.group(4),
                "message": file_match.group(5),
                "line": line
            }
        
        # 一般的なエラーパターン
        general_pattern = r'(ERROR|FATAL|CRITICAL|Exception):\s*(.+)'
        general_match = re.search(general_pattern, line, re.IGNORECASE)
        if general_match:
            return {
                "type": "General Error",
                "level": general_match.group(1),
                "message": general_match.group(2),
                "line": line
            }
        
        # HTTPエラーパターン
        http_pattern = r'HTTP\s+(\d+):\s*(.+)'
        http_match = re.search(http_pattern, line)
        if http_match:
            return {
                "type": "HTTP Error",
                "status_code": int(http_match.group(1)),
                "message": http_match.group(2),
                "line": line
            }
        
        return None
    
    def create_notion_page(self, error_data: Dict[str, Any]) -> bool:
        """Notionにエラーページを作成"""
        if not self.notion_token or not self.database_id:
            self.logger.warning("Notion設定が不完全です")
            return False
        
        try:
            # ページタイトルを生成
            title = f"エラー: {error_data.get('type', 'Unknown')} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # ページプロパティを設定
            properties = {
                "タイトル": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "エラータイプ": {
                    "select": {
                        "name": error_data.get("type", "Unknown")
                    }
                },
                "ステータス": {
                    "select": {
                        "name": "未対応"
                    }
                },
                "発生日時": {
                    "date": {
                        "start": error_data.get("timestamp")
                    }
                }
            }
            
            # ページ内容を生成
            content_blocks = []
            
            # エラー詳細
            if error_data.get("message"):
                content_blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"エラーメッセージ: {error_data['message']}"
                                }
                            }
                        ]
                    }
                })
            
            # ファイル情報
            if error_data.get("file"):
                content_blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"ファイル: {error_data['file']}:{error_data.get('line_number', 'N/A')}"
                                }
                            }
                        ]
                    }
                })
            
            # 元のコマンド
            if error_data.get("command"):
                content_blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": error_data["command"]
                                }
                            }
                        ],
                        "language": "bash"
                    }
                })
            
            # 完全なエラー行
            if error_data.get("line"):
                content_blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": error_data["line"]
                                }
                            }
                        ],
                        "language": "text"
                    }
                })
            
            # ページを作成
            page_data = {
                "parent": {
                    "database_id": self.database_id
                },
                "properties": properties,
                "children": content_blocks
            }
            
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=page_data
            )
            
            if response.status_code == 200:
                self.logger.info(f"エラーページを作成しました: {title}")
                return True
            else:
                self.logger.error(f"ページ作成失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Notionページ作成エラー: {e}")
            return False
    
    def sync_errors_to_notion(self, errors: List[Dict[str, Any]]) -> int:
        """エラーをNotionに同期"""
        success_count = 0
        
        for error in errors:
            if self.create_notion_page(error):
                success_count += 1
        
        return success_count
    
    def run_command_and_sync(self, command: str) -> Dict[str, Any]:
        """コマンドを実行してエラーを同期"""
        self.logger.info(f"コマンド実行とエラー同期開始: {command}")
        
        # コマンド実行
        output_data = self.capture_command_output(command)
        
        # エラー解析
        errors = self.parse_errors(output_data)
        
        # Notionに同期
        synced_count = self.sync_errors_to_notion(errors)
        
        result = {
            "command": command,
            "success": output_data["success"],
            "errors_found": len(errors),
            "errors_synced": synced_count,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"同期完了: {synced_count}/{len(errors)} エラーを同期")
        
        return result

def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ターミナルエラーをNotionに同期")
    parser.add_argument("command", help="実行するコマンド")
    parser.add_argument("--notion-token", help="Notion API Token")
    parser.add_argument("--database-id", help="Notion Database ID")
    
    args = parser.parse_args()
    
    # 環境変数から設定を読み込み
    token = args.notion_token or os.getenv('NOTION_TOKEN')
    database_id = args.database_id or os.getenv('NOTION_ERROR_DB_ID')
    
    if not token or not database_id:
        print("環境変数を設定してください:")
        print("export NOTION_TOKEN='your_notion_token'")
        print("export NOTION_ERROR_DB_ID='your_error_database_id'")
        return
    
    sync = ErrorLogSync(token, database_id)
    result = sync.run_command_and_sync(args.command)
    
    print(f"実行結果: {json.dumps(result, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    main() 