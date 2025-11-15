import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- APIルーターのインポート ---
# (app/api/transcribe_api.py などが存在することを前提)
from app.api import transcribe_api, upload_api, health_api, result_api, status_api, download_api

app = FastAPI(title="Whisper Transcribe API", version="1.0.0")

# --- 1. CORS設定 (これは必須) ---
# Render上のReactアプリ (フロントエンド) から
# このAPI (バックエンド) へのアクセスを許可します。
origins = [
    "https://whisper-transcribe-mdxq.onrender.com",  # RenderのフロントエンドURL
    # "https://whisper-transcribe-m6xq.onrender.com",  # (必要であれば)
    "http://localhost:3000",                        # ローカル開発用 (React)
    "http://127.0.0.1:3000",                      # ローカル開発用 (React)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 許可するオリジンを指定
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


# --- 3. ルート ("/") の動作確認エンドポイント ---
# (静的ファイルの配信は削除)
# HF SpacesのURLに直接アクセスした際に、
# APIが起動していることを確認するために追加。
@app.get("/")
async def root_fallback():
    return {
        "message": "Whisper Transcribe API is running",
        "docs_url": "/docs" # FastAPIの自動ドキュメント
    }

# --- 4. 開発用サーバー起動設定 ---
# (このブロックはローカルでの開発・テスト用です)
# (Hugging Face Spacesは Dockerfile の CMD を使って起動します)
if __name__ == "__main__":
    import uvicorn
    # ローカル開発時は 8000 ポートで実行
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)