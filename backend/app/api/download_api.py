from fastapi import APIRouter
from pathlib import Path
import tempfile

router = APIRouter()

@router.get("/audio-files")
def get_audio_files():
    temp_dir = Path(tempfile.gettempdir())
    audio_files = sorted(temp_dir.glob("*.m4a"), key=lambda f: f.stat().st_mtime, reverse=True)
    return {
        "audio_files": [str(f) for f in audio_files],
        "text_path": str(temp_dir / "result.txt"),
        "json_path": str(temp_dir / "result.json")
    }