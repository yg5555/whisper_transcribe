from pathlib import Path
import whisper
import gc
import os

# メモリ効率化のための設定
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"

# より軽量なモデルを使用
MODEL_NAME = "tiny"  # baseからtinyに変更
model = None

def get_model():
    """メモリ効率化されたモデル取得"""
    global model
    if model is None:
        print(f"[Logic] Whisperモデル読み込み開始: {MODEL_NAME}")
        model = whisper.load_model(MODEL_NAME)
        print(f"[Logic] Whisperモデル読み込み完了: {MODEL_NAME}")
    return model

def transcribe_file(file_path: str) -> str:
    print(f"[Logic] transcribe_file 呼び出し: {file_path}")

    try:
        # モデルを取得
        model = get_model()
        
        # Whisperで文字起こし（メモリ効率化）
        print(f"[Logic] Whisperで文字起こし開始")
        result = model.transcribe(
            file_path, 
            language="ja",
            fp16=False,  # メモリ使用量削減のためFP16を無効化
            verbose=False  # ログ出力を削減
        )
        
        # メモリクリア
        gc.collect()
        
        print(f"[Logic] Whisper文字起こし完了（先頭100文字）: {result['text'][:100]}")
        return result["text"]
        
    except Exception as e:
        print(f"[Logic] 文字起こしエラー: {e}")
        # エラー時にもメモリクリア
        gc.collect()
        raise e

def transcribe_latest_file() -> str:
    print("[Logic] transcribe_latest_file 呼び出し")
    data_dir = Path("app/data")
    audio_files = sorted(
        data_dir.glob("*"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    if not audio_files:
        raise FileNotFoundError("No audio files found.")

    print(f"[Logic] 最新ファイル選択: {audio_files[0]}")
    return transcribe_file(str(audio_files[0]))

def cleanup_model():
    """モデルのメモリをクリア"""
    global model
    if model is not None:
        del model
        model = None
        gc.collect()
        print("[Logic] モデルメモリをクリアしました")