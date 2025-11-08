from pathlib import Path
import whisper
import gc
import os
import tempfile

#
# 変更点：
# 1. グローバル変数 'model = None' を削除
# 2. 'get_model()' 関数を削除
# 3. 'cleanup_model()' 関数を削除
# 4. 'transcribe_file()' 関数内でモデルのロードとアンロードを行うよう修正
#

MODEL_NAME = "tiny"  # 最小サイズのモデル

def transcribe_file(file_path: str) -> str:
    """
    リクエストごとにモデルをロードし、処理後にアンロードする。
    無料枠のメモリ制限に対応するための戦略。
    """
    print(f"[Logic] transcribe_file 呼び出し: {file_path}")
    
    model = None  # モデル変数をローカルで初期化
    
    try:
        # ファイルの存在確認
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        # ファイルサイズ確認
        file_size = os.path.getsize(file_path)
        print(f"[Logic] ファイルサイズ: {file_size} bytes")
        
        if file_size == 0:
            raise ValueError("ファイルが空です")
        
        # --- ここでモデルをロード ---
        print(f"[Logic] Whisperモデル読み込み開始: {MODEL_NAME}")
        # CPU使用を強制
        model = whisper.load_model(MODEL_NAME, device="cpu")
        print(f"[Logic] Whisperモデル読み込み完了: {MODEL_NAME}")
        
        # Whisperで文字起こし（メモリ効率化）
        print(f"[Logic] Whisperで文字起こし開始")
        result = model.transcribe(
            file_path, 
            language="ja",
            fp16=False,  # CPUではFalse推奨
            verbose=False,  # ログ出力を削減
            task="transcribe"  # 明示的にタスクを指定
        )
        
        if not result or 'text' not in result:
            raise ValueError("Whisperの結果が不正です")
        
        text = result['text'].strip()
        if not text:
            raise ValueError("文字起こし結果が空です")
        
        print(f"[Logic] Whisper文字起こし完了（先頭100文字）: {text[:100]}")
        return text
        
    except Exception as e:
        print(f"[Logic] 文字起こしエラー: {e}")
        raise e  # エラーを呼び出し元に投げる
        
    finally:
        # --- 成功しても失敗しても、必ずモデルをメモリから解放 ---
        if model is not None:
            del model
            gc.collect()
            print("[Logic] モデルメモリをクリアしました")

def transcribe_latest_file() -> str:
    """
    データディレクトリから最新の音声ファイルを検索し、文字起こしを実行する。
    （この関数は変更なし）
    """
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