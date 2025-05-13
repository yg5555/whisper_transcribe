import os
import shutil
import datetime
import glob
import whisper
import json

from app.core.audio_preprocess import remove_silence

# モデルのロード（ここでは base モデル）
model = whisper.load_model("base")

# ディレクトリパスの定義
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "audio"))
ARCHIVE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "audio_archive"))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "output"))

def run_transcription_basic():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    # 音声ファイルの取得（更新日時で降順ソート）
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

    # 無音除去処理の実行
    cleaned_path = os.path.splitext(audio_path)[0] + "_cleaned.wav"
    cleaned = remove_silence(audio_path, cleaned_path)
    if cleaned:
        audio_path = cleaned

    # Whisperで文字起こし
    result = model.transcribe(audio_path)

    # 出力ファイル名の生成
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_basename = os.path.splitext(os.path.basename(audio_path))[0] + f"_{timestamp}"
    output_path = os.path.join(OUTPUT_DIR, output_basename + ".txt")
    output_json_path = os.path.join(OUTPUT_DIR, output_basename + ".json")

    # テキスト書き出し
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

    # JSON書き出し
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 音声ファイルをアーカイブへ移動（失敗しても無視）
    try:
        shutil.move(audio_path, os.path.join(ARCHIVE_DIR, os.path.basename(audio_path)))
    except Exception as e:
        return f"移動エラー: {e}"

    print(f"文字起こし完了: {output_path}")
    return {
        "text_path": output_path,
        "json_path": output_json_path
    }