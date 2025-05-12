import os
import shutil
import datetime
import glob
import whisper
model = whisper.load_model("base")
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "audio"))
ARCHIVE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "audio_archive"))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "output"))

def run_transcription_basic():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    audio_files = sorted(
        glob.glob(os.path.join(AUDIO_DIR, "*.*")),
        key=os.path.getmtime,
        reverse=True
    )
    print(f"AUDIO_DIR: {AUDIO_DIR}")
    print(f"検出されたファイル一覧: {audio_files}")

    if not audio_files:
        return "音声ファイルがありません。"

    audio_path = audio_files[0]
    result = model.transcribe(audio_path)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = os.path.splitext(os.path.basename(audio_path))[0] + f"_{timestamp}.txt"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

    output_json_filename = os.path.splitext(os.path.basename(audio_path))[0] + f"_{timestamp}.json"
    output_json_path = os.path.join(OUTPUT_DIR, output_json_filename)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    try:
        shutil.move(audio_path, os.path.join(ARCHIVE_DIR, os.path.basename(audio_path)))
    except Exception as e:
        return f"移動エラー: {e}"

    return {
        "text_path": output_path,
        "json_path": output_json_path
    }