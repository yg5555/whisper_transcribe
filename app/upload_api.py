from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
import datetime
import whisper
import json

router = APIRouter()

@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    # 日時と元ファイル名を元に出力ファイル名を決定
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(file.filename)[0]  # 拡張子除外
    save_dir = "data/output"
    os.makedirs(save_dir, exist_ok=True)

    # 入力ファイル保存（元ファイル名＋日時）
    input_path = os.path.join(save_dir, f"{base_name}_{now}.m4a")
    with open(input_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Whisperで文字起こし（baseモデル）
    model = whisper.load_model("tiny")  # モデルのロード
    result = model.transcribe(input_path)

    # 出力ファイル名（元ファイル名＋transcript＋日時）
    output_txt = os.path.join(save_dir, f"{base_name}_transcript_{now}.txt")
    output_json = os.path.join(save_dir, f"{base_name}_transcript_{now}.json")

    # テキスト出力
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(result["text"])

    # JSON出力
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # レスポンス返却
    return JSONResponse(content={
        "status": "success",
        "text_path": output_txt,
        "json_path": output_json
    })