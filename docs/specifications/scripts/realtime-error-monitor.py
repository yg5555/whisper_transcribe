#!/usr/bin/env python3
"""
リアルタイムでターミナルエラーを監視してNotionに同期するスクリプト
"""

import os
import sys
import json
import subprocess
import re
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import requests
import logging
import queue

class RealtimeErrorMonitor:
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
                logging.FileHandler('realtime_error_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # エラーキュー
        self.error_queue = queue.Queue()
        self.running = False
        self.error_patterns = self._load_error_patterns()
        
    def _load_error_patterns(self) -> List[Dict[str, Any]]:
        """エラーパターンを読み込み"""
        return [
            {
                "name": "Python Error",
                "pattern": r'(\w+Error):\s*(.+)',
                "type": "Python Error"
            },
            {
                "name": "Python File Error",
                "pattern": r'File\s+"([^"]+)",\s+line\s+(\d+),\s+in\s+(\w+)\s*\n\s*(\w+Error):\s*(.+)',
                "type": "Python File Error"
            },
            {
                "name": "General Error",
                "pattern": r'(ERROR|FATAL|CRITICAL|Exception):\s*(.+)',
                "type": "General Error"
            },
            {
                "name": "HTTP Error",
                "pattern": r'HTTP\s+(\d+):\s*(.+)',
                "type": "HTTP Error"
            },
            {
                "name": "Import Error",
                "pattern": r'ModuleNotFoundError:\s*No module named\s+\'([^\']+)\'',
                "type": "Import Error"
            },
            {
                "name": "Permission Error",
                "pattern": r'PermissionError:\s*\[Errno\s+\d+\]\s+(.+)',
                "type": "Permission Error"
            },
            {
                "name": "Connection Error",
                "pattern": r'ConnectionError|ConnectionRefusedError|TimeoutError',
                "type": "Connection Error"
            }
        ]
    
    def monitor_command(self, command: str, callback: Callable = None):
        """コマンドを監視"""
        self.logger.info(f"コマンド監視開始: {command}")
        
        try:
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
            
            # 出力監視スレッドを開始
            stdout_thread = threading.Thread(
                target=self._monitor_output,
                args=(process.stdout, "stdout", command)
            )
            stderr_thread = threading.Thread(
                target=self._monitor_output,
                args=(process.stderr, "stderr", command)
            )
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()
            
            # エラー同期スレッドを開始
            sync_thread = threading.Thread(target=self._sync_errors_worker)
            sync_thread.daemon = True
            sync_thread.start()
            
            # プロセス終了を待機
            while process.poll() is None:
                time.sleep(0.1)
            
            # スレッド終了を待機
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)
            
            self.logger.info(f"コマンド監視終了: {command}")
            
        except Exception as e:
            self.logger.error(f"コマンド監視エラー: {e}")
    
    def _monitor_output(self, pipe, pipe_type: str, command: str):
        """出力を監視"""
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    line = line.strip()
                    
                    # エラーパターンをチェック
                    error_info = self._check_error_patterns(line, command)
                    if error_info:
                        self.error_queue.put(error_info)
                        self.logger.warning(f"エラー検出 ({pipe_type}): {error_info['type']}")
                    
                    # 元の出力を表示
                    if pipe_type == "stdout":
                        print(f"STDOUT: {line}")
                    else:
                        print(f"STDERR: {line}", file=sys.stderr)
                        
        except Exception as e:
            self.logger.error(f"出力監視エラー: {e}")
    
    def _check_error_patterns(self, line: str, command: str) -> Optional[Dict[str, Any]]:
        """エラーパターンをチェック"""
        for pattern_info in self.error_patterns:
            pattern = pattern_info["pattern"]
            match = re.search(pattern, line, re.IGNORECASE)
            
            if match:
                error_info = {
                    "type": pattern_info["type"],
                    "line": line,
                    "command": command,
                    "timestamp": datetime.now().isoformat(),
                    "pattern_name": pattern_info["name"]
                }
                
                # マッチしたグループを追加
                if pattern_info["name"] == "Python Error":
                    error_info.update({
                        "error_class": match.group(1),
                        "message": match.group(2)
                    })
                elif pattern_info["name"] == "Python File Error":
                    error_info.update({
                        "file": match.group(1),
                        "line_number": int(match.group(2)),
                        "function": match.group(3),
                        "error_class": match.group(4),
                        "message": match.group(5)
                    })
                elif pattern_info["name"] == "General Error":
                    error_info.update({
                        "level": match.group(1),
                        "message": match.group(2)
                    })
                elif pattern_info["name"] == "HTTP Error":
                    error_info.update({
                        "status_code": int(match.group(1)),
                        "message": match.group(2)
                    })
                elif pattern_info["name"] == "Import Error":
                    error_info.update({
                        "message": f"Missing module: {match.group(1)}"
                    })
                elif pattern_info["name"] == "Permission Error":
                    error_info.update({
                        "message": match.group(1)
                    })
                
                return error_info
        
        return None
    
    def _sync_errors_worker(self):
        """エラー同期ワーカー"""
        while self.running:
            try:
                # キューからエラーを取得
                error_info = self.error_queue.get(timeout=1)
                
                # Notionに同期
                self._create_notion_error_page(error_info)
                
                # キュータスク完了
                self.error_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"エラー同期ワーカーエラー: {e}")
    
    def _create_notion_error_page(self, error_info: Dict[str, Any]) -> bool:
        """Notionにエラーページを作成"""
        if not self.notion_token or not self.database_id:
            self.logger.warning("Notion設定が不完全です")
            return False
        
        try:
            # ページタイトルを生成
            title = f"リアルタイムエラー: {error_info.get('type', 'Unknown')} - {datetime.now().strftime('%H:%M:%S')}"
            
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
                        "name": error_info.get("type", "Unknown")
                    }
                },
                "ステータス": {
                    "select": {
                        "name": "未対応"
                    }
                },
                "発生日時": {
                    "date": {
                        "start": error_info.get("timestamp")
                    }
                },
                "監視タイプ": {
                    "select": {
                        "name": "リアルタイム"
                    }
                }
            }
            
            # ページ内容を生成
            content_blocks = []
            
            # エラー詳細
            if error_info.get("message"):
                content_blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"エラーメッセージ: {error_info['message']}"
                                }
                            }
                        ]
                    }
                })
            
            # ファイル情報
            if error_info.get("file"):
                content_blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"ファイル: {error_info['file']}:{error_info.get('line_number', 'N/A')}"
                                }
                            }
                        ]
                    }
                })
            
            # 元のコマンド
            if error_info.get("command"):
                content_blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": error_info["command"]
                                }
                            }
                        ],
                        "language": "bash"
                    }
                })
            
            # 完全なエラー行
            if error_info.get("line"):
                content_blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": error_info["line"]
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
                self.logger.info(f"リアルタイムエラーページを作成しました: {title}")
                return True
            else:
                self.logger.error(f"ページ作成失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Notionページ作成エラー: {e}")
            return False
    
    def start_monitoring(self, command: str):
        """監視を開始"""
        self.running = True
        self.monitor_command(command)
    
    def stop_monitoring(self):
        """監視を停止"""
        self.running = False
        self.logger.info("監視を停止しました")

def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description="リアルタイムでターミナルエラーを監視")
    parser.add_argument("command", help="監視するコマンド")
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
    
    monitor = RealtimeErrorMonitor(token, database_id)
    
    try:
        print(f"リアルタイム監視開始: {args.command}")
        print("Ctrl+C で停止")
        monitor.start_monitoring(args.command)
    except KeyboardInterrupt:
        print("\n監視を停止します...")
        monitor.stop_monitoring()

if __name__ == "__main__":
    main() 