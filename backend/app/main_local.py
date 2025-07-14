from nicegui import ui, app
import os
from os.path import basename
from backend.app.config import AUDIO_DIR
from backend.app.core.transcriber import run_transcription_basic
import threading

uploaded_file = None
status_label = None
progress = None
progress_label = None
result_box = None
file_name_label = None
download_txt_button = None
download_json_button = None

def transcribe_direct():
    global uploaded_file, status_label, result_box, progress, progress_label
    global download_txt_button, download_json_button

    if not uploaded_file:
        status_label.text = 'ファイルが未選択です'
        return

    file_path = os.path.join(AUDIO_DIR, uploaded_file.name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.content.read())

    progress.value = 0.2
    progress_label.text = '進捗: 20%'
    status_label.text = '文字起こし中...'

    result = run_transcription_basic(audio_file_path=file_path)

    if isinstance(result, str):
        status_label.text = f'エラー: {result}'
        return

    if not isinstance(result, dict) or result.get("status") == "error":
        status_label.text = result.get("message", "エラーが発生しました")
        return

    progress.value = 1.0
    progress_label.text = '進捗: 100%'
    status_label.text = '完了しました'

    if os.path.exists(result["text_path"]):
        with open(result["text_path"], "r", encoding="utf-8") as f:
            result_box.value = f.read()

    download_txt_button.visible = True
    download_txt_button.on(
        'click',
        lambda: ui.download(result["text_path"], filename=basename(result["text_path"]))
    )

    download_json_button.visible = True
    download_json_button.on(
        'click',
        lambda: ui.download(result["json_path"], filename=basename(result["json_path"]))
    )

def transcribe_nicegui_ui():
    global uploaded_file, status_label, progress, progress_label, file_name_label
    global download_txt_button, download_json_button, result_box

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
            status_label.text = 'アップロード済み。文字起こし実行を押してください。'

            # Save the uploaded file to AUDIO_DIR
            file_path = os.path.join(AUDIO_DIR, uploaded_file.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.content.read())

            def run_in_background():
                result = run_transcription_basic(audio_file_path=file_path)

                if isinstance(result, str):
                    status_label.text = f'エラー: {result}'
                    return

                if not isinstance(result, dict) or result.get("status") == "error":
                    status_label.text = result.get("message", "エラーが発生しました")
                    return

                progress.value = 1.0
                progress_label.text = '進捗: 100%'
                status_label.text = '完了しました'

                if os.path.exists(result["text_path"]):
                    with open(result["text_path"], "r", encoding="utf-8") as f:
                        result_box.value = f.read()

                download_txt_button.visible = True
                download_txt_button.on(
                    'click',
                    lambda: ui.download(result["text_path"], filename=basename(result["text_path"]))
                )

                download_json_button.visible = True
                download_json_button.on(
                    'click',
                    lambda: ui.download(result["json_path"], filename=basename(result["json_path"]))
                )

            threading.Thread(target=run_in_background).start()

        ui.upload(
            label='ここをクリックしてファイルを選択',
            on_upload=handle_upload,
            auto_upload=True,
        ).props('color=primary').classes('w-full')

        file_name_label = ui.label('選択中のファイル: なし').classes('text-sm')
        # ui.button('文字起こしを実行', on_click=transcribe_direct)  # 処理二重化防止のためボタンをコメントアウト

        status_label = ui.label('ステータス: 未実行')
        progress_label = ui.label('進捗: 0%')
        progress = ui.linear_progress().props('value=0').style('width: 100%; max-width: 600px')

        download_txt_button = ui.button('文字起こし（.TXT）をダウンロード').props('color=primary')
        download_txt_button.visible = False

        download_json_button = ui.button('文字起こし（.JSON）をダウンロード').props('color=primary')
        download_json_button.visible = False

        result_box = ui.textarea().style('border: none; box-shadow: none; width: 100%; height: 300px')

    ui.run()

if __name__ in {'__main__', '__mp_main__'}:
    transcribe_nicegui_ui()