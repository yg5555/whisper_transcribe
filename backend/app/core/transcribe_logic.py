from pathlib import Path
import whisper

model = whisper.load_model("base")

def transcribe_file(file_path: str) -> str:
    print(f"[Logic] transcribe_file 呼び出し: {file_path}")  # ← ログ

    # Whisperで文字起こし
    print(f"[Logic] Whisperで文字起こし開始")  # ← ログ
    result = model.transcribe(file_path, language="ja")
    print(f"[Logic] Whisper文字起こし完了（先頭100文字）: {result['text'][:100]}")  # ← ログ

    return result["text"]

def transcribe_latest_file() -> str:
    print("[Logic] transcribe_latest_file 呼び出し")  # ← ログ
    data_dir = Path("app/data")
    audio_files = sorted(
        data_dir.glob("*"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    if not audio_files:
        raise FileNotFoundError("No audio files found.")

    print(f"[Logic] 最新ファイル選択: {audio_files[0]}")  # ← ログ
    return transcribe_file(str(audio_files[0]))