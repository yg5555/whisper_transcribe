from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import tempfile
from app.core.transcribe_logic import transcribe_file, transcribe_latest_file

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    print(f"[API] /transcribe 呼び出し - ファイル名: {file.filename}")  # ← 追加

    # 一時ファイルとして保存
    suffix = Path(file.filename).suffix
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        print(f"[API] 一時ファイル保存成功: {tmp_path}")  # ← 追加
    except Exception as e:
        print(f"[API] 一時ファイル保存エラー: {e}")  # ← 追加
        raise HTTPException(status_code=500, detail=f"ファイル保存エラー: {e}")

    # ロジック関数で文字起こし
    try:
        text = transcribe_file(tmp_path)
        print(f"[API] 文字起こし成功（先頭100文字）: {text[:100]}")  # ← 追加
        return {"transcription": text}
    except Exception as e:
        print(f"[API] 文字起こし失敗: {e}")  # ← 追加
        raise HTTPException(status_code=500, detail=f"文字起こし失敗: {e}")


@router.post("/transcribe/latest")
async def transcribe_latest():
    print("[API] /transcribe/latest 呼び出し")  # ← 追加
    try:
        text = transcribe_latest_file()
        print(f"[API] 最新ファイル文字起こし成功（先頭100文字）: {text[:100]}")  # ← 追加
        return {"text": text}
    except Exception as e:
        print(f"[API] 最新ファイル文字起こし失敗: {e}")  # ← 追加
        raise HTTPException(status_code=500, detail=str(e))