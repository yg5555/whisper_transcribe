from fastapi import APIRouter
from pathlib import Path
from fastapi.responses import FileResponse
import tempfile

router = APIRouter()

@router.get("/download/txt/{file_id}")
async def download_txt(file_id: str):
    temp_dir = Path(tempfile.gettempdir())
    path = temp_dir / f"{file_id}_result.txt"
    if not path.exists():
        return {"error": "Text result not found."}
    return FileResponse(path, media_type="text/plain", filename="result.txt")

@router.get("/download/json/{file_id}")
async def download_json(file_id: str):
    temp_dir = Path(tempfile.gettempdir())
    path = temp_dir / f"{file_id}_result.json"
    if not path.exists():
        return {"error": "JSON result not found."}
    return FileResponse(path, media_type="application/json", filename="result.json")