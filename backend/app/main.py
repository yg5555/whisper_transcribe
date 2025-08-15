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
# Render環境では ./static ディレクトリにコピーされている
frontend_build_path = Path("./static")
if frontend_build_path.exists():
    try:
        # 静的ファイルを /static にマウント（MIMEタイプを正しく設定）
        app.mount("/static", StaticFiles(directory=str(frontend_build_path), html=True, check_dir=True), name="static")
        print(f"静的ファイル配信を有効化: {frontend_build_path} -> /static")
        
        # 静的ファイルの内容を確認
        static_files = list(frontend_build_path.rglob("*"))
        print(f"静的ファイル数: {len(static_files)}")
        for file in static_files[:5]:  # 最初の5ファイルを表示
            print(f"  - {file}")
    except Exception as e:
        print(f"静的ファイル配信の設定エラー: {e}")
else:
    print(f"警告: フロントエンドビルドディレクトリが見つかりません: {frontend_build_path}")
    # フォールバック: 相対パスも試行
    fallback_path = Path("../frontend/dist")
    if fallback_path.exists():
        try:
            app.mount("/static", StaticFiles(directory=str(fallback_path), html=True, check_dir=True), name="static")
            print(f"フォールバック静的ファイル配信を有効化: {fallback_path} -> /static")
        except Exception as e:
            print(f"フォールバック静的ファイル配信の設定エラー: {e}")
    else:
        print(f"フォールバックパスも見つかりません: {fallback_path}")

@app.get("/")
async def root():
    """ルートパス: フロントエンドのindex.htmlを返す"""
    frontend_build_path = Path("./static")
    index_path = frontend_build_path / "index.html"
    
    print(f"ルートパスアクセス: index.htmlを探しています")
    print(f"探しているパス: {index_path}")
    
    if index_path.exists():
        print(f"index.htmlが見つかりました: {index_path}")
        return FileResponse(str(index_path))
    
    # フォールバック
    fallback_path = Path("../frontend/dist/index.html")
    print(f"フォールバックパスを確認: {fallback_path}")
    if fallback_path.exists():
        print(f"フォールバックindex.htmlが見つかりました: {fallback_path}")
        return FileResponse(str(fallback_path))
    
    # 静的ファイルディレクトリの内容を確認
    if frontend_build_path.exists():
        static_files = list(frontend_build_path.rglob("*"))
        print(f"静的ファイルディレクトリの内容:")
        for file in static_files[:10]:
            print(f"  - {file}")
    
    # 最後のフォールバック: API情報を返す
    return {"message": "Whisper Transcribe API", "version": "1.0.0", "status": "frontend_not_found", "error": "index.html not found"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Whisper Transcribe API is running"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "ok", "message": "API endpoints are available"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)