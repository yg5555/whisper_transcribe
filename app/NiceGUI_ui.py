import os
import threading
import time
from nicegui import ui
from app.core.transcriber import run_transcription_basic
from app.config import AUDIO_DIR

uploaded_file = None
status_label = None
result_box = None
progress = None
progress_label = None
file_name_label = None

def transcribe_with_status():
    global uploaded_file, status_label, result_box, progress, progress_label

    if not uploaded_file:
        status_label.set_text('ファイルが未選択です')
        return

    progress.set_value(0.1)
    progress_label.set_text('進捗: 10%')
    status_label.set_text('ステータス: 音声ファイルをコピー中...')
    filename = uploaded_file.name
    dst_path = os.path.join(AUDIO_DIR, filename)
    with open(dst_path, 'wb') as f:
        f.write(uploaded_file.content.read())

    time.sleep(0.5)

    progress.set_value(0.4)
    progress_label.set_text('進捗: 40%')
    status_label.set_text('ステータス: Whisperで文字起こし中...')

    result = run_transcription_basic()

    progress.set_value(1.0)
    progress_label.set_text('進捗: 100%')
    status_label.set_text('ステータス: 完了しました。')
    with open(result["text_path"], "r", encoding="utf-8") as f:
        result_box.set_text(f.read())

def transcribe_nicegui_ui():
    global uploaded_file, status_label, result_box, progress, progress_label, file_name_label

    with ui.column().classes('items-center').style('gap: 20px; max-width: 700px; margin: auto'):

        ui.label('Whisper 文字起こしアプリ').classes('text-2xl font-bold')

        ui.label('① 音声ファイルをアップロードしてください').classes('text-lg font-bold')
        ui.label('ファイルを選ぶだけでアップロードされます').style('color: gray')

        def handle_upload(e):
            global uploaded_file
            uploaded_file = e
            file_name_label.set_text(f'選択中のファイル: {uploaded_file.name}')
            progress.set_value(0.0)
            progress_label.set_text('進捗: 0%')
            status_label.set_text('ファイルアップロード済み。実行を押してください。')

        ui.upload(
            label='ここをクリックしてファイルを選択',
            on_upload=handle_upload,
            auto_upload=True
        ).props('color=primary').classes('w-full')

        file_name_label = ui.label('選択中のファイル: なし').classes('text-sm')

        ui.button('文字起こしを実行', on_click=lambda: threading.Thread(target=transcribe_with_status).start())

        status_label = ui.label('ステータス: 未実行')
        progress_label = ui.label('進捗: 0%')
        progress = ui.linear_progress().props('value=0').style('width: 100%; max-width: 600px')

        result_box = ui.textarea(label='文字起こし結果')
        result_box.props('rows=10')

    return ui

if __name__ in {'__main__', '__mp_main__'}:
    transcribe_nicegui_ui()