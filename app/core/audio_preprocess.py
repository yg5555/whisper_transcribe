#無音除去
import subprocess
import os

def remove_silence(input_path: str, output_path: str):
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-af", "silenceremove=1:0:-30dB",
        output_path
    ]
    try:
        subprocess.run(cmd, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"無音除去エラー: {e}")
        return None