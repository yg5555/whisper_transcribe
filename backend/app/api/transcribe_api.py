from fastapi import APIRouter
from pathlib import Path
import whisper
import tempfile

router = APIRouter()

@router.post("/transcribe")
async def transcribe():
    temp_dir = Path(tempfile.gettempdir())
    audio_files = sorted(temp_dir.glob("*.m4a"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not audio_files:
        return {"error": "No audio files found."}
    model = whisper.load_model("base")
    result = model.transcribe(str(audio_files[0]))
    (temp_dir / "result.txt").write_text(result["text"], encoding="utf-8")
    (temp_dir / "result.json").write_text(str(result), encoding="utf-8")
    return {"text": result["text"], "json": result}