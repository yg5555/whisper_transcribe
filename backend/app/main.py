import os
from pathlib import Path
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# --- APIルーターのインポート ---
# app/api/transcribe_api.py などが存在することを前提
from app.api import transcribe_api, upload_api, health_api, result_api, status_api, download_api

app = FastAPI(title="Whisper Transcribe API", version="1.0.0")

# --- 1. CORS設定の修正 ---
# 許可するオリジン（フロントエンドのURL）を指定
origins = [
    "https://whisper-transcribe-mdxq.onrender.com",  # ★ 今回のエラー画像で確認されたURL
    "https://whisper-transcribe-m6xq.onrender.com",  # 以前のURL（念のため残す）
    "http://localhost:3000",                        # ローカル開発用 (React)
    "http://127.0.0.1:3000",                      # ローカル開発用 (React)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 修正: 具体的なオリジンリストに変更
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. APIルーターの登録 ---
# APIは "/api" という接頭辞（prefix）でグループ化
app.include_router(transcribe_api.router, prefix="/api", tags=["transcribe"])
app.include_router(upload_api.router, prefix="/api", tags=["upload"])
app.include_router(health_api.router, prefix="/api", tags=["health"])
app.include_router(result_api.router, prefix="/api", tags=["result"])
app.include_router(status_api.router, prefix="/api", tags=["status"])
app.include_router(download_api.router, prefix="/api", tags=["download"])


# --- 3. 静的ファイル（Reactアプリ）の配信設定 ---
# (注意: この設定は APIルーター登録の *後* に記述する必要があります)

frontend_build_path = Path("./static")

if frontend_build_path.exists():
    print(f"フロントエンドビルドパスが見つかりました: {frontend_build_path.resolve()}")
    
    # StaticFilesをルート("/")にマウントします
    # html=True にすることで、/ や /other-path などの
    # 存在しないパスへのアクセス時に index.html を返し、
    # React Router (SPA) が正しく動作するようになります。
    app.mount(
        "/", 
        StaticFiles(directory=str(frontend_build_path), html=True), 
        name="static-root"
    )
else:
    print(f"警告: フロントエンドビルドディレクトリが見つかりません: {frontend_build_path.resolve()}")
    
    @app.get("/")
    async def root_fallback():
        return {
            "message": "Whisper Transcribe API is running", 
            "error": "Frontend static directory not found.",
            "path_checked": str(frontend_build_path.resolve())
        }

# --- 4. 開発用サーバー起動設定 ---
if __name__ == "__main__":
    import uvicorn
    # PORT環境変数を読み込む（RenderなどのPaaS対応）
    port = int(os.getenv("PORT", 8000))
    # "main:app" のように文字列で指定し、reload=Trueで開発時に自動リロード
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)