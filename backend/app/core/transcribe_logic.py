from pathlib import Path
import whisper
import tempfile
from app.core.audio_preprocess import remove_silence

model = whisper.load_model("base")

def transcribe_file(file_path: str) -> str:
    # 無音除去のため一時ファイルに出力
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        cleaned_path = tmp.name
        remove_silence(file_path, cleaned_path)

    # Whisperで文字起こし
    result = model.transcribe(cleaned_path, language="ja")
    return result["text"]

def transcribe_latest_file() -> str:
    data_dir = Path("app/data")
    audio_files = sorted(
        data_dir.glob("*"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    if not audio_files:
        raise FileNotFoundError("No audio files found.")
    return transcribe_file(str(audio_files[0]))