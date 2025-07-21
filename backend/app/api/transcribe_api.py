# app/api/transcribe_api.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import tempfile
from app.core.transcribe_logic import transcribe_file, transcribe_latest_file

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # 一時ファイルとして保存
    suffix = Path(file.filename).suffix
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル保存エラー: {e}")

    # ロジック関数で文字起こし
    try:
        text = transcribe_file(tmp_path)
        return {"transcription": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文字起こし失敗: {e}")


@router.post("/transcribe/latest")
async def transcribe_latest():
    try:
        text = transcribe_latest_file()
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))