from fastapi import APIRouter, UploadFile, File
import shutil
import uuid
from pathlib import Path
import tempfile

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    temp_dir = Path(tempfile.gettempdir())
    output_path = temp_dir / f"{file_id}_{file.filename}"
    with output_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"file_id": file_id, "filename": file.filename}