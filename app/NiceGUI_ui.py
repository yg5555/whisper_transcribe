import sys
import os
import threading
import shutil
import time
import json
from nicegui import ui, app
from fastapi.responses import FileResponse

from app.core.transcriber import run_transcription_basic
from app.config import AUDIO_DIR

uploaded_file = None
status_label = None
result_box = None
progress = None
progress_label = None
file_name_label = None
download_txt_button = None
download_json_button = None

@ui.page("/ads.txt")
def ads_txt():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static/ads.txt"))
    return FileResponse(path, media_type='text/plain')

def transcribe_with_status():
    global uploaded_file, status_label, result_box, progress, progress_label, download_txt_button, download_json_button

    if not uploaded_file:
        status_label.text = 'ファイルが未選択です'
        return

    progress.value = 0.1
    progress_label.text = '進捗: 10%'
    status_label.text = 'ステータス: 音声ファイルをコピー中...'
    filename = uploaded_file.name
    dst_path = os.path.join(AUDIO_DIR, filename)
    with open(dst_path, 'wb') as f:
        f.write(uploaded_file.content.read())

    time.sleep(0.5)

    progress.value = 0.4
    progress_label.text = '進捗: 40%'
    status_label.text = 'ステータス: Whisperで文字起こし中...'

    result = run_transcription_basic()

    progress.value = 1.0
    progress_label.text = '進捗: 100%'
    status_label.text = 'ステータス: 完了しました。'

    with open(result["text_path"], "r", encoding="utf-8") as f:
        result_box.value = f.read()

    json_path = result["text_path"].replace(".txt", ".json")
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(result, f_json, ensure_ascii=False, indent=2)

    download_txt_button.visible = True
    download_txt_button.on('click', lambda: ui.download(result["text_path"], filename="transcription.txt"))

    download_json_button.visible = True
    download_json_button.on('click', lambda: ui.download(json_path, filename="transcription.json"))

def transcribe_nicegui_ui():
    global uploaded_file, status_label, result_box, progress, progress_label, file_name_label
    global download_txt_button, download_json_button

    app.add_static_files('/static', os.path.abspath(os.path.join(os.path.dirname(__file__), '../static')))

    with ui.column().classes('items-center').style('gap: 20px; max-width: 700px; margin: auto'):

        ui.label('Whisper 文字起こしアプリ').classes('text-2xl font-bold')
        ui.label('① 音声ファイルをアップロードしてください').classes('text-lg font-bold')
        ui.label('ファイルを選ぶだけでアップロードされます').style('color: gray')

        def handle_upload(e):
            global uploaded_file
            uploaded_file = e
            file_name_label.text = f'選択中のファイル: {uploaded_file.name}'
            progress.value = 0.0
            progress_label.text = '進捗: 0%'
            status_label.text = 'ファイルアップロード済み。実行を押してください。'

        ui.upload(
            label='ここをクリックしてファイルを選択',
            on_upload=handle_upload,
            auto_upload=True,
        ).props('color=primary').classes('w-full')

        file_name_label = ui.label('選択中のファイル: なし').classes('text-sm')
        ui.button('文字起こしを実行', on_click=lambda: threading.Thread(target=transcribe_with_status).start())

        status_label = ui.label('ステータス: 未実行')
        progress_label = ui.label('進捗: 0%')
        progress = ui.linear_progress().props('value=0').style('width: 100%; max-width: 600px')

        # ✅ ここで先に配置（上部に表示される）
        download_txt_button = ui.button(
            '文字起こし（.TXT）をダウンロード',
            on_click=lambda: None
        ).props('color=primary')
        download_txt_button.visible = False

        download_json_button = ui.button(
            '文字起こし（.JSON）をダウンロード',
            on_click=lambda: None
        ).props('color=primary')
        download_json_button.visible = False

        # ✅ 結果表示エリア（ボタンの下に来る）
        result_box = ui.textarea().style('border: none; box-shadow: none; width: 100%; height: 300px')

    with ui.footer().style('padding: 20px;'):
        ui.label('広告')
    ui.add_body_html('<script src="/static/ads/admax.js"></script>')

    ui.run()

if __name__ in {'__main__', '__mp_main__'}:
    transcribe_nicegui_ui()