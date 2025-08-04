import os

# プロジェクトのルートパス（必要に応じてカスタマイズ可能）
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# データフォルダ構成
AUDIO_DIR = os.path.join(BASE_DIR, "data/audio")
OUTPUT_DIR = os.path.join(BASE_DIR, "data/output")
ARCHIVE_DIR = os.path.join(BASE_DIR, "data/audio_archive")

# Whisperモデル設定（メモリ効率化）
MODEL_NAME = "tiny"  # tiny: 39MB, base: 139MB, small: 244MB, medium: 769MB, large: 1550MB
LANGUAGE = "ja"

# メモリ効率化設定
PYTORCH_CUDA_ALLOC_CONF = "max_split_size_mb:128"
WHISPER_FP16 = False  # FP16を無効化してメモリ使用量を削減
WHISPER_VERBOSE = False  # ログ出力を削減

# その他定数（必要に応じて追加）
LOG_DIR = os.path.join(BASE_DIR, "logs")

# 環境変数から設定を読み込み
def get_model_name():
    """環境変数からモデル名を取得（デフォルト: tiny）"""
    return os.getenv("WHISPER_MODEL", MODEL_NAME)

def get_memory_limit():
    """メモリ制限を取得（MB）"""
    return int(os.getenv("MEMORY_LIMIT_MB", "256"))