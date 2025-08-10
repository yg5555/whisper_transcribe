from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import tempfile
import os
from app.core.transcribe_logic import transcribe_file, transcribe_latest_file

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    print(f"[API] /transcribe 呼び出し - ファイル名: {file.filename}")
    print(f"[API] ファイルサイズ: {file.size} bytes")
    print(f"[API] ファイルタイプ: {file.content_type}")

    # ファイルの検証
    if not file.filename:
        raise HTTPException(status_code=400, detail="ファイル名が指定されていません")
    
    if file.size == 0:
        raise HTTPException(status_code=400, detail="ファイルが空です")
    
    # 音声ファイルの拡張子チェック
    allowed_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"サポートされていないファイル形式です: {file_extension}. サポート形式: {', '.join(allowed_extensions)}"
        )

    # 一時ファイルとして保存
    suffix = Path(file.filename).suffix
    tmp_path = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            print(f"[API] ファイル内容読み込み完了: {len(contents)} bytes")
            
            if len(contents) == 0:
                raise HTTPException(status_code=400, detail="ファイル内容が空です")
            
            tmp.write(contents)
            tmp_path = tmp.name
            tmp.flush()  # 確実にディスクに書き込み
            os.fsync(tmp.fileno())  # ファイルシステムに同期
        
        print(f"[API] 一時ファイル保存成功: {tmp_path}")
        print(f"[API] 一時ファイルサイズ: {os.path.getsize(tmp_path)} bytes")
        
    except Exception as e:
        print(f"[API] 一時ファイル保存エラー: {e}")
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)  # 一時ファイルを削除
        raise HTTPException(status_code=500, detail=f"ファイル保存エラー: {e}")

    # ロジック関数で文字起こし
    try:
        print(f"[API] 文字起こし処理開始")
        text = transcribe_file(tmp_path)
        
        if not text or text.strip() == "":
            raise HTTPException(status_code=500, detail="文字起こし結果が空です")
        
        print(f"[API] 文字起こし成功（先頭100文字）: {text[:100]}")
        print(f"[API] 文字起こし結果の長さ: {len(text)} 文字")
        
        return {"transcription": text}
        
    except Exception as e:
        print(f"[API] 文字起こし失敗: {e}")
        raise HTTPException(status_code=500, detail=f"文字起こし失敗: {e}")
        
    finally:
        # 一時ファイルのクリーンアップ
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
                print(f"[API] 一時ファイル削除完了: {tmp_path}")
            except Exception as cleanup_error:
                print(f"[API] 一時ファイル削除エラー: {cleanup_error}")

@router.post("/transcribe/latest")
async def transcribe_latest():
    print("[API] /transcribe/latest 呼び出し")
    try:
        text = transcribe_latest_file()
        
        if not text or text.strip() == "":
            raise HTTPException(status_code=500, detail="文字起こし結果が空です")
        
        print(f"[API] 最新ファイル文字起こし成功（先頭100文字）: {text[:100]}")
        return {"text": text}
        
    except Exception as e:
        print(f"[API] 最新ファイル文字起こし失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))