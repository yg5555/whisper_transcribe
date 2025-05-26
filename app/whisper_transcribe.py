import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import whisper
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import gradio as gr

# 定数パスをインポート
from app.config import AUDIO_DIR, OUTPUT_DIR, ARCHIVE_DIR

# トランスクリプション関数をインポート
from app.core.transcriber import run_transcription_basic as run_transcription

# UIとルーターをインポート
from app.NiceGUI_ui import transcribe_nicegui_ui
from app.upload_api import router as upload_router

# FastAPI アプリケーション
app = FastAPI()
app.include_router(upload_router, prefix="/api")

# Gradio UI を FastAPI に統合
gradio_app = transcribe_nicegui_ui()
app = gr.mount_gradio_app(app, gradio_app, path="/")

# APIエンドポイント
@app.post("/transcribe")
def transcribe_api():
    try:
        output_json, output_txt = run_transcription(
            audio_dir=AUDIO_DIR,
            output_dir=OUTPUT_DIR,
            archive_dir=ARCHIVE_DIR
        )
        return JSONResponse(content={
            "status": "success",
            "json_result": output_json,
            "text_result": output_txt
        })
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"音声ファイルが見つかりません: {e}")
    except whisper.WhisperException as e:
        raise HTTPException(status_code=500, detail=f"Whisperエラー: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予期しないエラー: {e}")

# CLI実行時
if __name__ == "__main__":
    output_json, output_txt = run_transcription(
        audio_dir=AUDIO_DIR,
        output_dir=OUTPUT_DIR,
        archive_dir=ARCHIVE_DIR
    )
    print(f"文字起こし完了: {output_txt}")