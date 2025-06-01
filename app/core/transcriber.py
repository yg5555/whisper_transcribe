import os
import shutil
import datetime
import glob
import whisper
import json

from app.config import AUDIO_DIR, OUTPUT_DIR, ARCHIVE_DIR
from app.core.audio_preprocess import remove_silence

# Whisperモデルのロード
model = whisper.load_model("base")

def run_transcription_basic(audio_dir=None, output_dir=None, archive_dir=None, audio_file_path=None):
    # デフォルトのパスを補完（引数がNoneならconfigの定数を使う）
    audio_dir = audio_dir or AUDIO_DIR
    output_dir = output_dir or OUTPUT_DIR
    archive_dir = archive_dir or ARCHIVE_DIR

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    # 処理対象の音声ファイルの決定
    if audio_file_path:
        audio_path = audio_file_path
    else:
        # 指定がなければ最新のファイルを探す
        audio_files = sorted(
            glob.glob(os.path.join(audio_dir, "*.*")),
            key=os.path.getmtime,
            reverse=True
        )
        print(f"AUDIO_DIR: {audio_dir}")
        print(f"検出されたファイル一覧: {audio_files}")

        if not audio_files:
            return "音声ファイルがありません。"

        audio_path = audio_files[0]

    # 無音除去処理
    cleaned_path = os.path.splitext(audio_path)[0] + "_cleaned.wav"
    cleaned = remove_silence(audio_path, cleaned_path)
    if cleaned:
        audio_path = cleaned

    # Whisperで文字起こし
    result = model.transcribe(audio_path, language="ja")

    # 出力ファイル名の生成
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_basename = os.path.splitext(os.path.basename(audio_path))[0] + f"_{timestamp}"
    output_path = os.path.join(output_dir, output_basename + ".txt")
    output_json_path = os.path.join(output_dir, output_basename + ".json")

    # テキスト書き出し
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

    # JSON書き出し
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"文字起こし完了: {output_path}")
    return {
        "text_path": output_path,
        "json_path": output_json_path
    }