import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nicegui import ui
import shutil
import time

from app.core.transcriber import run_transcription_basic
from app.config import AUDIO_DIR

uploaded_file = None
status_label = None
result_box = None

# 実行ボタンが押されたときに発火
def transcribe_with_status():
    global uploaded_file, status_label, result_box

    if not uploaded_file:
        status_label.set_text('ファイルが未選択です')
        return

    status_label.set_text('ステータス: 音声ファイルをコピー中...')
    filename = uploaded_file.name
    dst_path = os.path.join(AUDIO_DIR, filename)
    shutil.copy(uploaded_file.content.read(), dst_path)

    time.sleep(0.5)
    status_label.set_text('ステータス: Whisperで文字起こし中...')

    result = run_transcription_basic()

    status_label.set_text('ステータス: 完了しました。')
    with open(result["text_path"], "r", encoding="utf-8") as f:
        result_box.set_text(f.read())

def transcribe_nicegui_ui():
    global uploaded_file, status_label, result_box

    ui.label('Whisper 文字起こしアプリ')

    def handle_upload(e):
        nonlocal uploaded_file
        uploaded_file = e

    ui.upload(label='音声ファイルを選択', on_upload=handle_upload)
    ui.button('文字起こしを実行', on_click=transcribe_with_status)

    status_label = ui.label('ステータス: 未実行')
    result_box = ui.textarea(label='文字起こし結果')
    result_box.props('rows=10')

    ui.run()

if __name__ in {'__main__', '__mp_main__'}:
    transcribe_nicegui_ui()