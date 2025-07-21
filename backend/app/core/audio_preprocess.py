import subprocess
import os

def remove_silence(input_path: str, output_path: str):
    print(f"[Silence] 無音除去開始: 入力={input_path} → 出力={output_path}")  # ← ログ追加

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-af", "silenceremove=1:0:-30dB",
        output_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"[Silence] 無音除去完了: {output_path}")  # ← ログ追加
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"[Silence] 無音除去エラー: {e}")  # ← ログ追加
        return None