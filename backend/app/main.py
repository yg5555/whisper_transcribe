from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from pathlib import Path

# APIルーターをインポート
from app.api import transcribe_api, upload_api, health_api, result_api, status_api, download_api

app = FastAPI(title="Whisper Transcribe API", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターを追加
app.include_router(transcribe_api.router, prefix="/api", tags=["transcribe"])
app.include_router(upload_api.router, prefix="/api", tags=["upload"])
app.include_router(health_api.router, prefix="/api", tags=["health"])
app.include_router(result_api.router, prefix="/api", tags=["result"])
app.include_router(status_api.router, prefix="/api", tags=["status"])
app.include_router(download_api.router, prefix="/api", tags=["download"])

# 静的ファイル配信（フロントエンドのビルド結果）
frontend_build_path = Path("../frontend/dist")
if frontend_build_path.exists():
    try:
        app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="static")
        print(f"静的ファイル配信を有効化: {frontend_build_path}")
    except Exception as e:
        print(f"静的ファイル配信の設定エラー: {e}")
else:
    print(f"警告: フロントエンドビルドディレクトリが見つかりません: {frontend_build_path}")

@app.get("/")
async def root():
    return {"message": "Whisper Transcribe API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Root health endpoint for Render health checks"""
    return {"status": "healthy", "version": "1.0.0", "mode": "full"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)