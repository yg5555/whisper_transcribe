# セキュリティ警告を回避してSSL接続を許可（自己署名証明書などのケース用）
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# NiceGUIで作成したUI構成をインポート（この関数内でUIが構築される）
from whisper_transcribe.app.main_local import transcribe_nicegui_ui

# NiceGUIのメインオブジェクト（イベントループやルーティングを持つ）
from nicegui import ui

# アプリのエントリーポイント
if __name__ in {"__main__", "__mp_main__"}:
    transcribe_nicegui_ui()
    ui.run(title='Whisper Transcribe App', reload=False)