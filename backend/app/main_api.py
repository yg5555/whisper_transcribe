<file name=0 path=/Users/yg/projects/whisper_transcribe/backend/app/main_api.py># app/main_api.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.transcriber import run_transcription_basic
import shutil
import tempfile
import os

app = FastAPI()

# CORS設定（本番では allow_origins を限定する）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # 一時ファイルとして保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    result_path = run_transcription_basic(tmp_path, file.filename)

    # 一時ファイル削除
    os.remove(tmp_path)

    return {"result_path": result_path}