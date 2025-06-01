from fastapi import FastAPI
from nicegui import ui, app as nicegui_app
from app.upload_api import router
from app.core.transcriber import run_transcription_basic

# FastAPI アプリ定義
fastapi_app = FastAPI()
fastapi_app.include_router(router)

# NiceGUI UI 定義
@ui.page("/")
async def main_page():
    ui.label("音声ファイルをアップロードして文字起こし").classes('text-h5')
    upload = ui.upload(label='音声ファイルを選択', auto_upload=True)

    @upload.on('upload')
    async def handle_upload(e):
        uploaded_file = e.args[0]
        result_path = run_transcription_basic(uploaded_file.content, uploaded_file.name)
        ui.notify(f'文字起こし完了: {result_path}')

# FastAPI に NiceGUI をマウント
fastapi_app.mount("/", nicegui_app)

# アプリエントリポイント
app = fastapi_app