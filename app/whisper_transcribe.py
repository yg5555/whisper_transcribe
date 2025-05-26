# セキュリティ警告を回避してSSL接続を許可（自己署名証明書などのケース用）
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# NiceGUIで作成したUI構成をインポート（この関数内でUIが構築される）
from app.NiceGUI_ui import transcribe_nicegui_ui

# NiceGUIのメインオブジェクト（イベントループやルーティングを持つ）
from nicegui import ui

# アプリのエントリーポイント
if __name__ == "__main__":
    # UIを構築（ボタン・アップロード欄・テキスト出力欄など）
    transcribe_nicegui_ui()

    # アプリを起動（デフォルトで http://localhost:8080 で表示される）
    ui.run(title='Whisper Transcribe App', reload=False)