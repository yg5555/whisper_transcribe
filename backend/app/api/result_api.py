from fastapi import APIRouter
from pathlib import Path
import tempfile
import json

router = APIRouter()

@router.get("/result/{file_id}")
async def get_result(file_id: str):
    temp_dir = Path(tempfile.gettempdir())
    text_path = temp_dir / "result.txt"
    json_path = temp_dir / "result.json"
    if not text_path.exists() or not json_path.exists():
        return {"error": "Result files not found"}
    return {
        "text": text_path.read_text(encoding="utf-8"),
        "json": json.loads(json_path.read_text(encoding="utf-8"))
    }