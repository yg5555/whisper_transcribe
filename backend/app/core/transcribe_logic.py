from pathlib import Path
import whisper
import gc
import os
import tempfile

# メモリ効率化のための設定
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:64"
os.environ["PYTORCH_NO_CUDA_MEMORY_CACHING"] = "1"

# より軽量なモデルを使用
MODEL_NAME = "tiny"  # 最小サイズのモデル
model = None

def get_model():
    """メモリ効率化されたモデル取得"""
    global model
    if model is None:
        try:
            print(f"[Logic] Whisperモデル読み込み開始: {MODEL_NAME}")
            # メモリ使用量を最小限に
            model = whisper.load_model(MODEL_NAME, device="cpu")  # CPU使用を強制
            print(f"[Logic] Whisperモデル読み込み完了: {MODEL_NAME}")
        except Exception as e:
            print(f"[Logic] モデル読み込みエラー: {e}")
            raise e
    return model

def transcribe_file(file_path: str) -> str:
    print(f"[Logic] transcribe_file 呼び出し: {file_path}")

    try:
        # ファイルの存在確認
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        # ファイルサイズ確認
        file_size = os.path.getsize(file_path)
        print(f"[Logic] ファイルサイズ: {file_size} bytes")
        
        if file_size == 0:
            raise ValueError("ファイルが空です")
        
        # モデルを取得
        model = get_model()
        
        # Whisperで文字起こし（メモリ効率化）
        print(f"[Logic] Whisperで文字起こし開始")
        result = model.transcribe(
            file_path, 
            language="ja",
            fp16=False,  # メモリ使用量削減のためFP16を無効化
            verbose=False,  # ログ出力を削減
            task="transcribe"  # 明示的にタスクを指定
        )
        
        # メモリクリア
        gc.collect()
        
        if not result or 'text' not in result:
            raise ValueError("Whisperの結果が不正です")
        
        text = result['text'].strip()
        if not text:
            raise ValueError("文字起こし結果が空です")
        
        print(f"[Logic] Whisper文字起こし完了（先頭100文字）: {text[:100]}")
        return text
        
    except Exception as e:
        print(f"[Logic] 文字起こしエラー: {e}")
        # エラー時にもメモリクリア
        gc.collect()
        raise e

def transcribe_latest_file() -> str:
    print("[Logic] transcribe_latest_file 呼び出し")
    
    # 複数のパスを試行
    possible_paths = [
        Path("app/data"),
        Path("data"),
        Path("../data"),
        Path("./data")
    ]
    
    data_dir = None
    for path in possible_paths:
        if path.exists():
            data_dir = path
            break
    
    if data_dir is None:
        raise FileNotFoundError(f"データディレクトリが見つかりません。試行したパス: {possible_paths}")
    
    print(f"[Logic] データディレクトリ使用: {data_dir}")
    
    audio_files = sorted(
        data_dir.glob("*"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    
    # 音声ファイルのみをフィルタリング
    audio_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}
    audio_files = [f for f in audio_files if f.suffix.lower() in audio_extensions]
    
    if not audio_files:
        raise FileNotFoundError("音声ファイルが見つかりません。")

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