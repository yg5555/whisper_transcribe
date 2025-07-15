from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

@router.post("/transcribe")
async def transcribe():
    import whisper

    data_dir = Path("app/data")
    audio_files = sorted(data_dir.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not audio_files:
        return {"error": "No audio files found."}

    try:
        model = whisper.load_model("base")
        result = model.transcribe(str(audio_files[0]))
        return {"text": result["text"]}
    except Exception as e:
        return {"error": str(e)}

@router.get("/download/txt")
async def download_txt():
    path = Path("app/data/result.txt")
    if not path.exists():
        return {"error": "Text result not found."}
    return FileResponse(path, media_type="text/plain", filename="result.txt")

@router.get("/download/json")
async def download_json():
    path = Path("app/data/result.json")
    if not path.exists():
        return {"error": "JSON result not found."}
    return FileResponse(path, media_type="application/json", filename="result.json")