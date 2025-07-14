import os

# プロジェクトのルートパス（必要に応じてカスタマイズ可能）
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# データフォルダ構成
AUDIO_DIR = os.path.join(BASE_DIR, "data/audio")
OUTPUT_DIR = os.path.join(BASE_DIR, "data/output")
ARCHIVE_DIR = os.path.join(BASE_DIR, "data/audio_archive")

# Whisperモデル設定（必要に応じて拡張）
MODEL_NAME = "base"
LANGUAGE = "ja"

# その他定数（必要に応じて追加）
LOG_DIR = os.path.join(BASE_DIR, "logs")