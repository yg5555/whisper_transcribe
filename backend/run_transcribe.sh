#!/bin/bash

# 仮想環境を有効化
source /Users/yg/projects/whisper_diarization/whisper_env/bin/activate

# プロジェクトディレクトリに移動
cd /Users/yg/projects/whisper_transcribe

# スクリプトを実行
python3 app/whisper_transcribe.py

# 仮想環境を無効化
deactivate