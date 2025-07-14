import os

file_path = os.path.join(AUDIO_DIR, uploaded_file.name)
os.makedirs(os.path.dirname(file_path), exist_ok=True)