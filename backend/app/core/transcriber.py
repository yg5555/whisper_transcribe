from core.audio_preprocess import remove_silence


def run_transcription_basic(file_path: str) -> str:
    # 仮の実装。後でwhisper処理に差し替え可能。
    return f"Transcribed: {file_path}"